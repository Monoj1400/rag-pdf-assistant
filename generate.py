import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv(override=True)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are a document assistant. Answer the user's question using ONLY the context provided below.
Rules:
- If the answer is not in the context, reply exactly: "I couldn't find that in the provided document."
- Do not use outside knowledge.
- Always cite the page number(s) your answer comes from, like (Page 3).
"""

def build_context(hits: list[dict]) -> str:
    return "\n\n".join(
        f"[Page {h['page']}]\n{h['text']}" for h in hits
    )

def generate_answer(question: str, hits: list[dict]) -> str:
    context = build_context(hits)
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",  # free & fast on Groq
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
        temperature=0.1,  # low = deterministic, grounded answers
    )
    return response.choices[0].message.content