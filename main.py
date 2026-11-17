from ingest import extract_text_from_pdf, chunk_pages
from vector_store import index_chunks, retrieve
from generate import generate_answer

def ingest(pdf_path: str):
    pages = extract_text_from_pdf(pdf_path)
    chunks = chunk_pages(pages)
    index_chunks(chunks)
    return len(chunks)

def ask(question: str):
    hits = retrieve(question)
    if not hits or hits[0]["distance"] > 1.0:  # weak retrieval guard
        return "I couldn't find that in the provided document.", []
    answer = generate_answer(question, hits)
    sources = sorted({h["page"] for h in hits})
    return answer, sources

if __name__ == "__main__":
    pdf = input("PDF path: ").strip()
    n = ingest(pdf)
    print(f"Ready. Ingested {n} chunks.\n")

    while True:
        q = input("Ask a question (or 'quit'): ").strip()
        if q.lower() == "quit":
            break
        answer, sources = ask(q)
        print(f"\nAnswer: {answer}")
        print(f"Sources: {sources}\n")