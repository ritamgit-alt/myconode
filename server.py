from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import whisper
import subprocess
import tempfile
import os
import re
import uuid
import chromadb
import sqlite3

app = Flask(__name__)
CORS(app)

def init_db():
    conn = sqlite3.connect('myconode.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS field_logs (
            id TEXT PRIMARY KEY,
            transcript TEXT,
            structured TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    try:
        c.execute("ALTER TABLE field_logs ADD COLUMN lat REAL")
        c.execute("ALTER TABLE field_logs ADD COLUMN lng REAL")
    except sqlite3.OperationalError:
        pass
    
    conn.commit()
    conn.close()

init_db()

print("Initializing Air-Gapped RAG Memory (ChromaDB)...")
chroma_client = chromadb.PersistentClient(path="./myconode_memory")
collection = chroma_client.get_or_create_collection(name="foraging_logs")

print("Loading Whisper base model... (This takes a moment on your M2)")
whisper_model = whisper.load_model("base")
print("System Online. MycoNode is actively listening on port 5000.")

# --- PWA STATIC FILE ROUTING ---
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)
# -------------------------------

@app.route('/api/process', methods=['POST'])
def process_audio():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    audio_file = request.files['file']
    lat = request.form.get('lat', type=float, default=54.1119)
    lng = request.form.get('lng', type=float, default=24.3045)
    
    ext = os.path.splitext(audio_file.filename)[1] or '.m4a'
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        audio_file.save(tmp.name)
        tmp_path = tmp.name

    try:
        result = whisper_model.transcribe(tmp_path)
        raw_transcript = result.get("text", "").strip()

        prompt = f"""You are an offline botanical field extraction AI. 
        Analyze this field log and extract the details into a clean, professional markdown format.
        Use these exact headers: ### Species Identified, ### Harvest Condition, ### Habitat Clues.
        Use concise bullet points or short paragraphs. Do NOT use tables.

        Field log: "{raw_transcript}"
        """
        gemma_res = subprocess.run(
            ['ollama', 'run', 'gemma2:2b', prompt],
            capture_output=True, text=True, check=True
        )
        
        clean_structured = re.sub(r'\x1B\[[0-9;]*[a-zA-Z]', '', gemma_res.stdout)
        clean_structured = re.sub(r'\[\d+[A-Za-z]', '', clean_structured).replace('[K', '').strip()

        log_id = f"log_{uuid.uuid4().hex[:8]}"
        document_text = f"Raw Log: {raw_transcript}\n\nExtracted Data:\n{clean_structured}"
        
        collection.add(
            documents=[document_text],
            metadatas=[{"type": "field_log"}],
            ids=[log_id]
        )

        conn = sqlite3.connect('myconode.db')
        c = conn.cursor()
        c.execute("INSERT INTO field_logs (id, transcript, structured, lat, lng) VALUES (?, ?, ?, ?, ?)", 
                  (log_id, raw_transcript, clean_structured, lat, lng))
        conn.commit()
        conn.close()

        return jsonify({
            'transcript': raw_transcript,
            'structured': clean_structured,
            'lat': lat,
            'lng': lng
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    try:
        results = collection.query(query_texts=[user_message], n_results=3)
        context = "\n\n---\n\n".join(results['documents'][0]) if results['documents'] and results['documents'][0] else "No previous field logs found."

        prompt = f"""You are a highly intelligent botanical field assistant.
        Answer the user's question using ONLY the information provided in the 'Past Field Logs' below. Keep your answer concise.
        Past Field Logs:\n{context}\n\nUser Question: {user_message}\nAssistant:"""

        gemma_res = subprocess.run(['ollama', 'run', 'gemma2:2b', prompt], capture_output=True, text=True, check=True)
        clean_reply = re.sub(r'\x1B\[[0-9;]*[a-zA-Z]', '', gemma_res.stdout)
        clean_reply = re.sub(r'\[\d+[A-Za-z]', '', clean_reply).replace('[K', '').strip()

        return jsonify({'reply': clean_reply})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/logs', methods=['GET'])
def get_logs():
    try:
        conn = sqlite3.connect('myconode.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT id, transcript, structured, lat, lng, timestamp FROM field_logs ORDER BY timestamp DESC")
        logs = [dict(row) for row in c.fetchall()]
        conn.close()
        return jsonify(logs)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000)
