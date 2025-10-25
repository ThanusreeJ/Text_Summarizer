import time
import re
from io import BytesIO
from typing import List, Tuple, Dict
import os
import requests
import json
from datetime import datetime

import streamlit as st
from pypdf import PdfReader
from docx import Document
from gtts import gTTS

st.set_page_config(
    page_title="Advanced Text Summarizer",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    .feature-card {
        background: #f0f2f6;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .summary-box {
        background: #e8f4f8;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #0F766E;
    }
</style>
""", unsafe_allow_html=True)

# ---------- Header / Hero ----------
st.markdown("""
<div class="main-header">
    <h1>📝 Text Summarizer Pro</h1>
    <p>Summarize, translate, and interact with your documents in multiple ways.</p>
</div>
""", unsafe_allow_html=True)

MODEL_NAME = "sshleifer/distilbart-cnn-12-6"

# ---------- Helper Functions ----------
def extract_text_from_pdf(file) -> str:
    try:
        reader = PdfReader(file)
        pages = []
        for p in reader.pages:
            txt = p.extract_text() or ""
            pages.append(txt)
        return "\n".join(pages)
    except Exception as e:
        st.error(f"Failed to read PDF: {e}")
        return ""

def extract_text_from_docx(file) -> str:
    try:
        doc = Document(file)
        return "\n".join(p.text for p in doc.paragraphs if p.text)
    except Exception as e:
        st.error(f"Failed to read DOCX: {e}")
        return ""

def clean_text(text: str) -> str:
    text = text.replace("\r", " ").strip()
    text = re.sub(r"\s+", " ", text)
    return text

def hf_api_summarize(
    text: str,
    max_length: int,
    min_length: int,
    num_beams: int,
    timeout: int = 60,
) -> str:
    token = _get_hf_token()
    if not token:
        raise RuntimeError(
            "HF_API_TOKEN not set. Add it as an environment variable to use the API."
        )
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "inputs": text,
        "parameters": {
            "max_length": max_length,
            "min_length": min_length,
            "do_sample": False,
            "num_beams": num_beams,
        },
        "options": {"wait_for_model": True},
    }
    url = "https://api-inference.huggingface.co/models/sshleifer/distilbart-cnn-12-6"
    r = requests.post(url, headers=headers, json=payload, timeout=timeout)
    r.raise_for_status()
    out = r.json()
    if isinstance(out, list) and out and isinstance(out[0], dict) and "summary_text" in out[0]:
        return out[0]["summary_text"]
    if isinstance(out, dict) and "error" in out:
        raise RuntimeError(out["error"])
    raise RuntimeError(f"Unexpected response from HF API: {out}")

def summarize_long_text_api(
    text: str,
    target_words: int = 150,
    quality: str = "Balanced",
) -> tuple[str, list[str]]:
    approx_tokens = max(30, min(int(target_words / 0.75), 260))
    max_len = approx_tokens
    min_len = max(15, int(max_len * 0.4))
    num_beams = 1 if quality == "Fast" else 4 if quality == "High quality" else 2

    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    chunks, current, curr_len = [], [], 0
    max_words = 675
    for s in sentences:
        words = s.split()
        l = len(words)
        if l > max_words:
            for i in range(0, l, max_words):
                part = " ".join(words[i:i+max_words])
                if current:
                    chunks.append(" ".join(current))
                    current, curr_len = [], 0
                chunks.append(part)
            continue
        if curr_len + l <= max_words:
            current.append(s)
            curr_len += l
        else:
            chunks.append(" ".join(current))
            current, curr_len = [s], l
    if current:
        chunks.append(" ".join(current))

    partial_summaries = []
    for ch in chunks:
        out = hf_api_summarize(ch, max_len, min_len, num_beams)
        partial_summaries.append(out)
    combined = " ".join(partial_summaries).strip()
    if len(chunks) > 1 and len(combined.split()) > target_words * 1.2:
        final = hf_api_summarize(combined, max_len, min_len, num_beams).strip()
        return final, chunks
    return combined, chunks

def hf_api_translate(text: str, source_lang: str, target_lang: str) -> str:
    token = _get_hf_token()
    if not token:
        raise RuntimeError("HF_API_TOKEN not set.")
    
    lang_map = {
        "English": "en",
        "Spanish": "es",
        "French": "fr",
        "German": "de",
        "Hindi": "hi",
        "Chinese": "zh",
        "Japanese": "ja",
        "Portuguese": "pt",
    }
    
    src = lang_map.get(source_lang, "en")
    tgt = lang_map.get(target_lang, "en")
    
    headers = {"Authorization": f"Bearer {token}"}
    model_name = f"Helsinki-NLP/opus-mt-{src}-{tgt}"
    payload = {"inputs": text, "options": {"wait_for_model": True}}
    
    url = f"https://api-inference.huggingface.co/models/{model_name}"
    r = requests.post(url, headers=headers, json=payload, timeout=60)
    r.raise_for_status()
    out = r.json()
    
    if isinstance(out, list) and out and isinstance(out[0], dict) and "translation_text" in out[0]:
        return out[0]["translation_text"]
    raise RuntimeError(f"Translation failed: {out}")

def generate_audio_summary(text: str, lang: str = "en") -> bytes:
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        audio_buffer = BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        return audio_buffer.getvalue()
    except Exception as e:
        st.error(f"Audio generation failed: {e}")
        return None

def hf_api_qa(context: str, question: str) -> str:
    token = _get_hf_token()
    if not token:
        raise RuntimeError("HF_API_TOKEN not set.")
    
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"inputs": {"question": question, "context": context}}
    url = "https://api-inference.huggingface.co/models/deepset/roberta-base-squad2"
    
    r = requests.post(url, headers=headers, json=payload, timeout=60)
    r.raise_for_status()
    out = r.json()
    
    # Hugging Face returns a dict with 'answer' field
    if isinstance(out, dict) and "answer" in out:
        ans = out["answer"].strip()
        return ans if ans and ans.lower() != "empty" else "No relevant answer found."
    else:
        return "No answer found."


def render_copy_button(text_to_copy: str):
    from streamlit.components.v1 import html
    safe = text_to_copy.replace("\\", "\\\\").replace("`", "\\`")
    html(
        f"""
        <div style="display:flex;justify-content:flex-end;margin-top:0.25rem;">
          <button id="copy-btn" style="
            background:#0F766E;color:white;border:none;padding:8px 12px;
            border-radius:6px;cursor:pointer;">Copy summary</button>
        </div>
        <script>
          const btn = document.getElementById('copy-btn');
          btn.addEventListener('click', async () => {{
            try {{
              await navigator.clipboard.writeText(`{safe}`);
              btn.innerText = 'Copied!';
              setTimeout(() => btn.innerText = 'Copy summary', 1200);
            }} catch(e) {{
              btn.innerText = 'Copy failed';
              setTimeout(() => btn.innerText = 'Copy summary', 1200);
            }}
          }});
        </script>
        """,
        height=48,
    )

def _get_hf_token() -> str | None:
    return os.getenv("HF_API_TOKEN") or os.getenv("HUGGINGFACEHUB_API_TOKEN")

# ---------- Sidebar Controls ----------
with st.sidebar:
    st.header("Settings & Features")
    
    # Basic settings
    st.subheader("Summarization")
    target_words = st.slider("Desired summary length (words)", min_value=50, max_value=400, value=150, step=10)
    quality = st.selectbox("Quality vs. speed", ["Fast", "Balanced", "High quality"], index=1)
    
    st.markdown("---")
    
    st.subheader("Features")
    enable_translation = st.checkbox("Enable Translation", value=False)
    enable_audio = st.checkbox("Enable Audio Summary", value=False)

    
    st.markdown("---")
    st.caption("Engine: Hugging Face Inference API")
    
    help_exp = st.expander("Help & Setup")
    help_exp.markdown(
        "**Setup:**\n"
        "- Set `HF_API_TOKEN` environment variable with your Hugging Face token.\n"
        "- Get a free token: https://huggingface.co/settings/tokens\n\n"
        "**Features:**\n"
        "- Translation: Translate summary to another language.\n"
        "- Audio: Convert summary to speech.\n"
        "- Q&A: Ask detailed questions about the document."
    )

tabs = st.tabs(["Summarize", "Translate", "Audio"])

# TAB 1: SUMMARIZE
with tabs[0]:
    st.subheader("Summarize Your Document")
    
    input_mode = st.radio("Input method", ["Paste Text", "Upload File"], horizontal=True)
    
    input_text = ""
    if input_mode == "Paste Text":
        input_text = st.text_area(
            "Your text",
            placeholder="Paste or type your article, notes, or document content here...",
            height=220,
        )
    else:
        uploaded = st.file_uploader("Choose a file", type=["pdf", "docx"])
        if uploaded:
            ext = uploaded.name.lower().split(".")[-1]
            if ext == "pdf":
                input_text = extract_text_from_pdf(uploaded)
            elif ext == "docx":
                input_text = extract_text_from_docx(uploaded)
            if input_text:
                st.info(f"Loaded {len(input_text.split())} words from {uploaded.name}")
    
    col1, col2 = st.columns([0.2, 0.8])
    with col1:
        run_btn = st.button("Summarize", type="primary", use_container_width=True)
    with col2:
        st.caption("Supports long inputs by chunking automatically.")
    
    if run_btn:
        if not input_text or len(input_text.strip()) < 20:
            st.warning("Please provide at least a few sentences.")
        else:
            with st.spinner("Summarizing..."):
                s_time = time.time()
                cleaned = clean_text(input_text)
                summary, chunks = summarize_long_text_api(cleaned, target_words, quality)
                duration = time.time() - s_time
            
            st.success(f"Done in {duration:.1f}s (chunks: {len(chunks)})")
            
            st.markdown('<div class="summary-box">', unsafe_allow_html=True)
            st.text_area("Summary", summary, height=220, disabled=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            render_copy_button(summary)
            st.download_button("Download .txt", data=summary.encode("utf-8"), file_name="summary.txt")
            
            # Store in session for other tabs
            st.session_state.last_summary = summary
            st.session_state.last_text = cleaned

# TAB 2: TRANSLATE
with tabs[1]:
    st.subheader("Translate Summary")
    
    if not enable_translation:
        st.info("Enable 'Translation' in the sidebar to use this feature.")
    else:
        if "last_summary" not in st.session_state:
            st.warning("Please summarize a document first in the 'Summarize' tab.")
        else:
            col1, col2 = st.columns(2)
            with col1:
                source_lang = st.selectbox("From", ["English", "Spanish", "French", "German", "Hindi", "Chinese", "Japanese", "Portuguese"], index=0)
            with col2:
                target_lang = st.selectbox("To", ["Spanish", "French", "German", "Hindi", "Chinese", "Japanese", "Portuguese", "English"], index=0)
            
            if st.button("Translate", type="primary"):
                with st.spinner("Translating..."):
                    try:
                        translated = hf_api_translate(st.session_state.last_summary, source_lang, target_lang)
                        st.markdown('<div class="summary-box">', unsafe_allow_html=True)
                        st.text_area("Translated Summary", translated, height=220, disabled=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                        st.download_button("Download Translation", data=translated.encode("utf-8"), file_name="translated_summary.txt")
                    except Exception as e:
                        st.error(f"Translation error: {e}")

# TAB 3: AUDIO
with tabs[2]:
    st.subheader("Audio Summary")
    
    if not enable_audio:
        st.info("Enable 'Audio Summary' in the sidebar to use this feature.")
    else:
        if "last_summary" not in st.session_state:
            st.warning("Please summarize a document first in the 'Summarize' tab.")
        else:
            audio_lang = st.selectbox("Audio language", ["English", "Spanish", "French", "German", "Hindi"], index=0)
            
            if st.button("Generate Audio", type="primary"):
                with st.spinner("Generating audio..."):
                    try:
                        lang_code = {"English": "en", "Spanish": "es", "French": "fr", "German": "de", "Hindi": "hi"}[audio_lang]
                        audio_data = generate_audio_summary(st.session_state.last_summary, lang_code)
                        if audio_data:
                            st.audio(audio_data, format="audio/mp3")
                            st.download_button("Download Audio", data=audio_data, file_name="summary.mp3", mime="audio/mp3")
                    except Exception as e:
                        st.error(f"Audio error: {e}")



# ---------- Footer ----------
st.divider()
st.caption("Advanced Text Summarizer Pro | Powered by Streamlit + Hugging Face Inference API | Model: sshleifer/distilbart-cnn-12-6")
