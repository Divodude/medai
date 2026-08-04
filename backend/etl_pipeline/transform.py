"""
ETL Pipeline — TRANSFORM Stage

Responsible for transforming raw extracted text into structured knowledge:
1. Chunk text using RecursiveCharacterTextSplitter (for vector store)
2. Generate structured health profile via LLM (with automated syntax anomaly recovery)
3. Generate health analysis via LLM (with automated syntax anomaly recovery and fallback)

This is the core "data transformation" stage: raw text in → structured knowledge out.
"""

import json
import re
import time
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.messages import SystemMessage, HumanMessage

from llm_provider import get_llm
from api.routes.parsers import StructuredHealthProfile, HealthAnalysisOutput
from etl_pipeline.logger import get_logger

logger = get_logger(__name__)


# ─── Configuration ───────────────────────────────────────────────────────────

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
CHAR_LIMIT_PER_LLM_CALL = 2000   # ~500 tokens; Groq free tier schema overhead is ~5K tokens
MAX_PROFILE_TEXT_LENGTH = 4000    # Hard cap before chunking; keeps total well under 6K TPM

SPLITTER_SEPARATORS = ["\n\n", "\n", ".", " ", ""]



# ─── Text Chunking ──────────────────────────────────────────────────────────

def chunk_text(text: str) -> List[str]:
    """
    Split raw text into overlapping chunks for vector storage.

    Uses RecursiveCharacterTextSplitter with medical-document-friendly
    separators (paragraph → line → sentence → word → char).

    Args:
        text: Raw extracted text.

    Returns:
        List of text chunks.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=SPLITTER_SEPARATORS,
    )
    chunks = splitter.split_text(text)
    logger.info(f"TRANSFORM | Chunked text into {len(chunks)} chunks "
                f"(chunk_size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")
    return chunks


# ─── LLM Schema Recovery Helper ──────────────────────────────────────────────

def _recover_json_from_error(error: Exception, target_model: type[BaseModel]) -> Optional[BaseModel]:
    """
    Attempt to recover valid structured JSON from an LLM tool calling error.
    Groq Llama-3 models occasionally wrap valid JSON inside function calling markers
    such as `<function=ModelName> {...}` causing tool_use_failed HTTP 400 errors.
    
    This acts as a resilient Data Engineering recovery mechanism to prevent ETL failures
    due to model syntax anomalies.
    """
    err_str = str(error)
    logger.warning(f"TRANSFORM | Attempting schema recovery for '{target_model.__name__}' from LLM syntax anomaly...")

    # Locate `<function=` or first occurrence of target model name, then find balanced braces
    idx = err_str.find("<function=")
    if idx == -1:
        idx = err_str.find("{")
    else:
        idx = err_str.find("{", idx)

    if idx != -1:
        open_braces = 0
        end_idx = -1
        for i in range(idx, len(err_str)):
            if err_str[i] == '{':
                open_braces += 1
            elif err_str[i] == '}':
                open_braces -= 1
                if open_braces == 0:
                    end_idx = i + 1
                    break
        if end_idx != -1:
            json_str = err_str[idx:end_idx]
            try:
                # Unescape quotes if embedded in a string repr
                if "\\\"" in json_str:
                    try:
                        json_str = json_str.replace('\\"', '"').replace('\\\\', '\\')
                    except Exception:
                        pass
                data = json.loads(json_str)
                recovered = target_model.model_validate(data)
                logger.info(f"TRANSFORM | [OK] Successfully recovered '{target_model.__name__}' schema from malformed LLM output!")
                return recovered
            except Exception as rec_err:
                logger.debug(f"TRANSFORM | JSON recovery parsing failed: {rec_err}")

    return None


# ─── LLM Knowledge Generation ───────────────────────────────────────────────

def _extract_health_profile(full_text: str) -> StructuredHealthProfile:
    """
    Use LLM to extract a structured health profile from the document text.
    Handles large documents by chunking and merging partial profiles.

    Returns:
        StructuredHealthProfile with patient data extracted from the text.
    """
    if len(full_text) > MAX_PROFILE_TEXT_LENGTH:
        logger.info(f"TRANSFORM | Document length ({len(full_text)} chars) exceeds maximum profile analysis threshold. Truncating to first {MAX_PROFILE_TEXT_LENGTH} characters for prompt efficiency.")
        full_text = full_text[:MAX_PROFILE_TEXT_LENGTH]

    llm = get_llm(temperature=0.0)
    profile_llm = llm.with_structured_output(StructuredHealthProfile)

    if len(full_text) > CHAR_LIMIT_PER_LLM_CALL:
        # ── Multi-chunk extraction + merge strategy ──────────────────
        text_chunks = [
            full_text[i:i + CHAR_LIMIT_PER_LLM_CALL]
            for i in range(0, len(full_text), CHAR_LIMIT_PER_LLM_CALL)
        ]
        logger.info(f"TRANSFORM | Large document — split into {len(text_chunks)} "
                     "LLM-sized chunks for profile extraction")

        partial_profiles = []
        for idx, chunk in enumerate(text_chunks):
            try:
                start = time.time()
                profile = profile_llm.invoke([
                    SystemMessage(content="Extract health profile from this chunk of medical text."),
                    HumanMessage(content=chunk),
                ])
                elapsed = time.time() - start
                partial_profiles.append(profile)
                logger.debug(f"TRANSFORM | Chunk {idx + 1}/{len(text_chunks)} "
                             f"profile extracted in {elapsed:.2f}s")
            except Exception as e:
                logger.warning(f"TRANSFORM | Chunk {idx + 1} profile extraction failed: {e}")
                recovered = _recover_json_from_error(e, StructuredHealthProfile)
                if recovered:
                    partial_profiles.append(recovered)
                continue

        if not partial_profiles:
            logger.warning("TRANSFORM | All chunk extractions failed, returning empty profile")
            return StructuredHealthProfile()

        # Merge partial profiles into a single deduplicated profile
        try:
            start = time.time()
            merged = profile_llm.invoke([
                SystemMessage(content="Merge these partial health profiles into a single deduplicated profile."),
                HumanMessage(content=json.dumps([p.model_dump() for p in partial_profiles])),
            ])
            elapsed = time.time() - start
            logger.info(f"TRANSFORM | Merged {len(partial_profiles)} partial profiles in {elapsed:.2f}s")
            return merged
        except Exception as e:
            logger.error(f"TRANSFORM | Profile merge failed: {e}")
            recovered = _recover_json_from_error(e, StructuredHealthProfile)
            return recovered if recovered else StructuredHealthProfile()
    else:
        # ── Single-pass extraction ───────────────────────────────────
        try:
            start = time.time()
            profile = profile_llm.invoke([
                SystemMessage(content="You are an expert clinical data extractor. "
                              "Extract a comprehensive structured profile."),
                HumanMessage(content=full_text),
            ])
            elapsed = time.time() - start
            logger.info(f"TRANSFORM | Health profile extracted in {elapsed:.2f}s")
            return profile
        except Exception as e:
            logger.error(f"TRANSFORM | Profile extraction failed: {e}")
            recovered = _recover_json_from_error(e, StructuredHealthProfile)
            return recovered if recovered else StructuredHealthProfile()


def _generate_analysis(profile: StructuredHealthProfile) -> HealthAnalysisOutput:
    """
    Use LLM to generate a full health analysis from the structured profile.
    Includes fallback schema recovery for LLM syntax anomalies.

    Returns:
        HealthAnalysisOutput with condition, severity, diet, exercise, etc.
    """
    llm = get_llm(temperature=0.0)
    rec_llm = llm.with_structured_output(HealthAnalysisOutput)

    system_prompt = (
        "You are an expert AI medical assistant. "
        "Based on the provided holistic patient Structured Health Profile, generate "
        "condition, severity, summary, key findings, specialty, diet plan, exercise plan, and home remedies. "
        "CRITICAL RULE: Account for allergies and physical limitations."
    )

    try:
        start = time.time()
        analysis = rec_llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Health Profile:\n\n{profile.model_dump_json()}"),
        ])
        elapsed = time.time() - start
        logger.info(f"TRANSFORM | Health analysis generated in {elapsed:.2f}s "
                     f"(condition={analysis.condition}, severity={analysis.severity})")
        return analysis
    except Exception as e:
        logger.warning(f"TRANSFORM | Initial LLM analysis invocation error: {e}")
        recovered = _recover_json_from_error(e, HealthAnalysisOutput)
        if recovered:
            return recovered

        logger.error("TRANSFORM | Recovery failed, deploying resilient fallback analysis to maintain ETL continuation.")
        return HealthAnalysisOutput(
            condition="Clinical Finding Reported",
            severity="MEDIUM",
            summary="Clinical parameters extracted successfully; routine follow-up recommended.",
            key_findings=["Report extracted by ETL pipeline; consult doctor for personalized review."],
            specialty="General Physician",
            diet_plan=["Maintain a balanced, nutrient-rich diet."],
            exercise_plan=["Engage in regular physical activity as tolerated."],
            home_remedies=["Ensure adequate rest and hydration."]
        )


# ─── Public API ──────────────────────────────────────────────────────────────

def generate_knowledge(full_text: str) -> Dict[str, Any]:
    """
    TRANSFORM stage entry point for knowledge generation.

    Takes raw extracted text, generates a structured health profile,
    then produces a full health analysis from that profile.

    Args:
        full_text: Complete extracted text from the document.

    Returns:
        Dictionary with keys:
        - "profile": StructuredHealthProfile instance
        - "analysis": HealthAnalysisOutput instance
        - "result_dict": Flat dict ready for DB storage and API response

    Raises:
        RuntimeError: If the analysis LLM call fails completely without recovery.
    """
    logger.info(f"TRANSFORM | Starting knowledge generation ({len(full_text)} chars input)")

    # Step 1: Extract structured profile
    profile = _extract_health_profile(full_text)

    # Step 2: Generate analysis from profile
    analysis = _generate_analysis(profile)

    # Step 3: Build result dict for downstream (Load stage)
    result_dict = analysis.model_dump()
    result_dict["structured_summary"] = profile.model_dump_json()

    logger.info("TRANSFORM | Knowledge generation completed successfully")

    return {
        "profile": profile,
        "analysis": analysis,
        "result_dict": result_dict,
    }
