# MycoNode 🍄🌿
### Air-Gapped AI Botanical Field Journal

**MycoNode** is a privacy-first, 100% offline botanical and foraging field journal designed for extreme wilderness environments where cellular service or cloud connectivity is unavailable. It runs entirely on local hardware (optimized for Apple Silicon M2 chips), allowing field researchers and foragers to ingest audio voice memos, automatically extract structured botanical spec sheets using local AI, query past logs via a vector database, and map harvest coordinates without leaking location data to the cloud.

---

## 🚀 Key Features

* **Air-Gapped Processing:** Zero cloud dependence. Runs locally via Python, Flask, and local hardware execution.
* **Local ASR Transcription:** Leverages OpenAI Whisper (Base model) to transcribe rough voice memos from the trail.
* **Botanical Intelligence (NPU-Powered):** Automatically parses unstructured text into structured markdown spec sheets (*Species Identified, Harvest Condition, Habitat Clues*) using **Gemma 2 (2B)** via Ollama.
* **RAG Local Memory (ChromaDB):** Permanent vector database vectorizes past logs so you can query your history offline (*"Where did I find Chanterelles last month?"*).
* **SQLite Persistence:** Automatically saves all logs, transcripts, and metadata into a local lightweight database (`myconode.db`) with a built-in historical library sidebar.
* **Offline Topography & Geolocation:** Automatically captures device GPS coordinates and renders local harvest pins on an interactive Leaflet topographic map.
* **Progressive Web App (PWA):** Fully cacheable and installable as a standalone native app on desktop or mobile.

---

## 🛠️ Tech Stack

* **Frontend:** HTML5, Tailwind CSS, Three.js (interactive pollen/spore background particles), Marked.js, Leaflet.js.
* **Backend Bridge:** Python, Flask, Flask-CORS.
* **Local AI & Database Engines:** 
  * Ollama (`gemma2:2b`)
  * OpenAI Whisper (`base`)
  * ChromaDB (Vector RAG store)
  * SQLite3 (Relational data persistence)

---

## ⚙️ Local Installation & Setup

Ensure you have **Ollama** installed and running on your machine with the Gemma 2 model downloaded before launching.

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/ritamgit-alt/myconode.git](https://github.com/ritamgit-alt/myconode.git)
   cd myconode
