import os
import tempfile
from flask import Flask, request, jsonify, render_template
from ingest import extract_text_from_pdf, chunk_pages
from vector_store import index_chunks, retrieve
from generate import generate_answer

app = Flask(__name__)
@app.route('/')
def home():
    return render_template('index.html')

# 1. ENDPOINT: Upload and Ingest a PDF
@app.route('/upload', methods=['POST'])
def upload_pdf():
    # Check if a file was sent in the request
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if not file.filename.endswith('.pdf'):
        return jsonify({"error": "File must be a PDF"}), 400

    try:
        # Save the file temporarily so pypdf can read it
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, file.filename)
        file.save(temp_path)

        # Run our Phase 1 logic
        pages = extract_text_from_pdf(temp_path)
        chunks = chunk_pages(pages)
        index_chunks(chunks)

        # Clean up the temp file
        os.remove(temp_path)

        return jsonify({
            "status": "success",
            "message": f"Successfully ingested {len(chunks)} chunks.",
            "filename": file.filename
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 2. ENDPOINT: Ask a question
@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.get_json()
    
    if not data or 'question' not in data:
        return jsonify({"error": "Please provide a 'question' in the JSON body"}), 400
    
    question = data['question']

    try:
        # Run our Phase 1 logic
        hits = retrieve(question)
        
        # Guardrail: if the best match is too far, don't call the LLM
        if not hits or hits[0]["distance"] > 1.0:
            return jsonify({
                "answer": "I couldn't find that in the provided document.",
                "sources": []
            }), 200
            
        answer = generate_answer(question, hits)
        sources = sorted({h["page"] for h in hits})
        
        return jsonify({
            "answer": answer,
            "sources": sources
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # Run the Flask app on port 5000
    app.run(debug=True, port=5000)