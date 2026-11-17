from pypdf import PdfReader

def extract_text_from_pdf(pdf_path: str) -> list[dict]:
    """
    Returns a list of dicts: [{"text": "...", "page": 1}, ...]
    We keep the page number so we can cite it later.
    """
    reader = PdfReader(pdf_path)
    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if text.strip():  # skip empty pages
            pages.append({"text": text, "page": i + 1})
    return pages

def chunk_pages(pages: list[dict], chunk_size: int = 800, overlap: int = 150) -> list[dict]:
    """
    Splits each page's text into overlapping chunks.
    chunk_size: target characters per chunk
    overlap: characters repeated between consecutive chunks (preserves context)
    """
    chunks = []
    for page in pages:
        text = page["text"]
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end]
            chunks.append({
                "text": chunk_text,
                "page": page["page"],
                "chunk_id": len(chunks),
            })
            start += chunk_size - overlap  # move forward, keeping overlap
    return chunks