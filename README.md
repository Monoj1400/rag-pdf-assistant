# 📄 RAG-Powered Document Assistant

A production-grade, full-stack Retrieval-Augmented Generation (RAG) application. Upload a PDF, and chat with it to get grounded, citation-backed answers.

**🔴 Live Demo:** [huggingface.co/spaces/Manoj1400/rag-pdf-assistant](https://huggingface.co/spaces/Manoj1400/rag-pdf-assistant)

---

## 🚀 Key Features

*   **Semantic Search:** Uses Hugging Face `sentence-transformers` to convert text into vector embeddings, allowing the system to understand the *meaning* of a query, not just keywords.
*   **Anti-Hallucination Guardrails:** The system is strictly prompted and programmatically gated to only answer from the provided document. If the answer isn't there, it explicitly refuses to answer.
*   **Page-Level Citations:** Every answer includes the exact page number(s) the information was retrieved from, preventing AI hallucinations.
*   **Layout-Aware PDF Extraction:** Uses `pdfplumber` to extract text from complex PDF layouts (like resumes) without jumbling the text order.
*   **Zero-Cost Cloud Deployment:** Optimized dependencies and chunking strategies to run smoothly on Hugging Face Spaces' free tier.

## 🛠️ Tech Stack

*   **Backend / UI:** Python, Gradio
*   **AI / LLM:** Groq API (Llama-3), Sentence-Transformers (`all-MiniLM-L6-v2`)
*   **Vector Database:** ChromaDB
*   **PDF Parsing:** `pdfplumber`
*   **Deployment:** Hugging Face Spaces (ZeroGPU)

## ⚙️ Architecture Flow

1.  **Ingestion:** The user uploads a PDF. `pdfplumber` extracts the text, preserving the page metadata. The text is split into overlapping chunks (1000 characters, 250 overlap).
2.  **Embedding:** The chunks are passed through `sentence-transformers` to generate dense vector embeddings.
3.  **Storage:** The vectors, original text, and page numbers are stored locally in ChromaDB.
4.  **Retrieval:** When a user asks a question, the query is embedded using the same model. ChromaDB performs a cosine similarity search to retrieve the top 4 most relevant chunks.
5.  **Generation:** The retrieved chunks are injected into a strict system prompt and sent to the Groq LLM API. The LLM generates a final answer with citations.

## 🧠 Engineering Challenges Overcome

During the development and deployment of this project, several real-world engineering problems were solved:

*   **PDF Extraction Failures:** Standard libraries like `pypdf` jumbled the text of formatted resumes, causing vector search to fail. Switched to `pdfplumber` with `layout=True` to fix spatial text extraction.
*   **RAG Chunking Tuning:** Initial chunk sizes were too small, causing fragmented context and retrieval failures for broad questions (e.g., "What is the education?"). Tuned to `1000` characters with `250` overlap to preserve semantic context.
*   **Dependency Hell:** Resolved complex dependency conflicts between older `torch`, `transformers`, `numpy`, and newer `gradio` versions required by Hugging Face Spaces.
*   **Memory Limits (OOM):** Originally deployed to Render, but the free tier's 512MB RAM caused `SIGKILL` errors when loading PyTorch. Migrated to Hugging Face Spaces (ZeroGPU) to leverage 16GB of RAM.
*   **Guardrail Calibration:** Adjusted the ChromaDB distance threshold and LLM system prompts to prevent hallucinations while ensuring valid answers were not blocked.

## 💻 How to Run Locally

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Manoj1400/rag-pdf-assistant.git
   cd rag-pdf-assistant
