from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1400, 1000
BG_COLOR = (250, 250, 250)
BOX_FILL = (230, 244, 255)
BOX_OUTLINE = (30, 100, 180)
TEXT_COLOR = (20, 20, 20)
LINE_COLOR = (20, 80, 160)
ARROW_SIZE = 12

try:
    FONT = ImageFont.truetype("arial.ttf", 20)
except IOError:
    FONT = ImageFont.load_default()

boxes = [
    {
        "id": "app",
        "text": "FastAPI App\n(api/main.py)",
        "pos": (500, 50, 800, 130),
    },
    {
        "id": "analyze",
        "text": "POST /analyze\n(routes/analyze.py)",
        "pos": (150, 250, 450, 330),
    },
    {
        "id": "chat",
        "text": "POST /chat\n(routes/chat.py)",
        "pos": (850, 250, 1150, 330),
    },
    {
        "id": "ingest",
        "text": "Document Ingestion\n(rag/ingestion.py)",
        "pos": (150, 450, 450, 530),
    },
    {
        "id": "graph",
        "text": "LangGraph RAG Agent\n(graph/builder.py)",
        "pos": (850, 450, 1150, 530),
    },
    {
        "id": "chroma",
        "text": "ChromaDB\nVector Store",
        "pos": (150, 650, 450, 730),
    },
    {
        "id": "sqlite",
        "text": "SQLite Database\n(db/crud.py)",
        "pos": (500, 800, 800, 880),
    },
    {
        "id": "llm",
        "text": "Singleton LLM Provider\n(llm_provider.py)",
        "pos": (500, 650, 800, 730),
    },
    {
        "id": "tools",
        "text": "Tool Node: DDG Doctors\n(tools/doctor_search.py)",
        "pos": (950, 650, 1250, 730),
    }
]

# Calculate centers for drawing arrows
centers = {}
for b in boxes:
    x0, y0, x1, y1 = b["pos"]
    centers[b["id"]] = ((x0 + x1) // 2, (y0 + y1) // 2)

edges = [
    ("app", "analyze", "REST API"),
    ("app", "chat", "REST API"),
    ("analyze", "ingest", "Upload PDF/Image"),
    ("analyze", "sqlite", "Save Structured JSON"),
    ("chat", "graph", "Chat message"),
    ("graph", "sqlite", "Load Session History"),
    ("graph", "tools", "Agent calls Tool"),
    ("graph", "chroma", "Retrieve Context"),
    ("ingest", "chroma", "Chunk & Embed"),
    ("analyze", "llm", "Structured Output (Groq)"),
    ("graph", "llm", "Agent LLM Generation (Groq)"),
]

img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
draw = ImageDraw.Draw(img)

def draw_arrow(start, end, label):
    # Just draw a line for simplicity, and a circle at the end
    draw.line([start, end], fill=LINE_COLOR, width=3)
    r = 6
    draw.ellipse((end[0]-r, end[1]-r, end[0]+r, end[1]+r), fill=LINE_COLOR)
    
    # Draw label in the middle
    mid_x = (start[0] + end[0]) // 2
    mid_y = (start[1] + end[1]) // 2
    
    # white background for text
    bbox = draw.textbbox((mid_x, mid_y), label, font=FONT)
    draw.rectangle(bbox, fill=BG_COLOR)
    draw.text((mid_x, mid_y), label, fill=(100, 100, 100), font=FONT)

for start_id, end_id, label in edges:
    start_pos = centers[start_id]
    end_pos = centers[end_id]
    draw_arrow(start_pos, end_pos, label)

for box in boxes:
    x0, y0, x1, y1 = box["pos"]
    draw.rounded_rectangle([x0, y0, x1, y1], fill=BOX_FILL, outline=BOX_OUTLINE, width=3, radius=10)
    
    text = box["text"]
    # center text
    bbox = draw.multiline_textbbox((0,0), text, font=FONT)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    
    cx, cy = centers[box["id"]]
    draw.multiline_text((cx - w//2, cy - h//2), text, fill=TEXT_COLOR, font=FONT, align="center")

output_path = Path(__file__).parent / "backend_flow_diagram.png"
img.save(output_path)
print(f"Saved diagram to {output_path}")
