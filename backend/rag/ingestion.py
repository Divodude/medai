import os
import tempfile
import fitz  # PyMuPDF
import base64
from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from llm_provider import get_embeddings, get_llm


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from a PDF file bytes."""
    text = ""
    # fitz can open from stream
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

import easyocr
import numpy as np
import cv2

_reader = None

def get_easyocr_reader():
    global _reader
    if _reader is None:
        _reader = easyocr.Reader(['en'])
    return _reader





from collections import Counter

def multi_pass_easyocr(img):
    """
    Runs EasyOCR on multiple preprocessed versions of the image
    and returns the text that appears most consistently.
    """

    reader = get_easyocr_reader()

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    variants = {
        "original": img,
        "gray": gray,
        "equalized": cv2.equalizeHist(gray),
        "adaptive": cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            10,
        ),
        "otsu": cv2.threshold(
            gray,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )[1],
    }

    all_results = []

    for name, variant in variants.items():
        try:
            text = " ".join(reader.readtext(variant, detail=0))

            if text.strip():
                all_results.append(text)

        except Exception:
            continue

    if not all_results:
        return ""

    vote = Counter(all_results)

    best_text, count = vote.most_common(1)[0]

    return best_text

def extract_text_from_image(file_bytes: bytes, mime: str) -> str:
    """Extract text from image using local EasyOCR."""
    reader = get_easyocr_reader()
    
    nparr = np.frombuffer(file_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        raise ValueError("Could not decode image bytes for OCR.")
        
    results = multi_pass_easyocr(img)
    return results

def ingest_document(file_bytes: bytes, filename: str, mime: str, session_id: str) -> Chroma:
    """
    Extracts text from the file, chunks it, and stores it in ChromaDB for the given session.
    """
    text = ""
    
    if "pdf" in mime or filename.endswith(".pdf"):
        text = extract_text_from_pdf(file_bytes)
    elif "image" in mime:
        text = extract_text_from_image(file_bytes, mime)
    else:
        # Assume plain text
        text = file_bytes.decode("utf-8", errors="ignore")
        
    if not text.strip():
        raise ValueError("Text extraction returned empty content")
        
    # Split text
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    
    chunks = text_splitter.split_text(text)
    
    documents = [
        Document(page_content=chunk, metadata={"session_id": session_id})
        for chunk in chunks
    ]
    
    # Store in Chroma
    embeddings = get_embeddings()
    persist_directory = os.path.join(os.path.dirname(__file__), "..", "chroma_db")
    
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    
    return text  # Return full text so we can also generate structured output
