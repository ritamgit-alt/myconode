import streamlit as st
import subprocess
import whisper
import os
import tempfile

st.title("ForageVault Diagnostic Mode")

uploaded_file = st.file_uploader("Upload recipe audio", type=["m4a", "mp3", "wav"])

if uploaded_file is not None:
    st.audio(uploaded_file)
    
    if st.button("Run Real Pipeline"):
        try:
            with st.spinner("1/2: Running real Whisper transcription..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    tmp_path = tmp_file.name
                
                model = whisper.load_model("base")
                result = model.transcribe(tmp_path)
                raw_transcript = result["text"]
                
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
                    
                st.success("Whisper Success!")
                st.info(raw_transcript)

            with st.spinner("2/2: Running real Gemma 2 extraction..."):
                prompt = f"""Extract structured data from this raw transcript:
                "{raw_transcript}"
                """
                res = subprocess.run(
                    ['ollama', 'run', 'gemma2:2b', prompt], 
                    capture_output=True, 
                    text=True, 
                    check=True
                )
                structured_output = res.stdout
                
                st.success("Gemma 2 Success!")
                st.markdown(structured_output)
                
        except subprocess.CalledProcessError as e:
            st.error("❌ Ollama Error: Make sure the Ollama app is running in your Mac menu bar.")
            st.code(e.stderr)
        except Exception as e:
            st.error("❌ General Error:")
            st.code(str(e))