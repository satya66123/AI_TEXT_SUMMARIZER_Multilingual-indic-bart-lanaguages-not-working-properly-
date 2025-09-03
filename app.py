from fastapi import FastAPI, UploadFile, File, Form
from typing import Optional
from transformers import pipeline
import uvicorn
import PyPDF2
import docx
import langid
import re

# ✅ Load summarizers
print("Loading mBART-50...")
mbart_summarizer = pipeline(
    "summarization",
    model="facebook/mbart-large-50-many-to-many-mmt"
)

print("Loading mT5...")
try:
    mt5_summarizer = pipeline(
        "summarization",
        model="google/mt5-small"
    )
except Exception as e:
    print("⚠️ Could not load mT5:", str(e))
    mt5_summarizer = None

print("Loading IndicBART summarizer...")
try:
    indicbart_summarizer = pipeline(
        "summarization",
        model="ai4bharat/IndicBART"   # ✅ Correct model for Telugu
    )
    print("✅ Using IndicBART model:", indicbart_summarizer.model.config.name_or_path)
except Exception as e:
    print("⚠️ Could not load IndicBART summarizer:", str(e))
    indicbart_summarizer = None

# --- FastAPI app ---
app = FastAPI(
    title="Multilingual Summarizer (Indic Preferred)",
    description="Summarizes text/files in multiple languages. Indic languages (Telugu, Hindi, Tamil, etc.) always use IndicBART for fluency.",
    version="8.0"
)

# --- Supported languages ---
MBART_LANGS = {
    "bn", "hi", "ta", "ur", "en", "fr", "de", "es", "zh_CN", "zh_TW",
    "ja", "ko", "ar", "ru", "tr", "vi", "pl", "nl", "pt", "it", "id",
    "th", "cs", "el", "he", "hu", "ms", "sw"
}
INDIC_LANGS = {"hi", "ta", "te", "bn", "ml", "gu", "kn", "or", "pa", "mr"}

# --- Helpers ---
def detect_language(text: str) -> str:
    lang, _ = langid.classify(text[:500])
    return lang

def ensure_sentence_end(text: str) -> str:
    text = text.strip()
    if not text.endswith(('.', '!', '?', '।')):
        text += '.'
    return text

def chunk_text(text, max_chunk_size=800):
    text = ensure_sentence_end(text)
    sentences = text.split('. ')
    chunks, current_chunk = [], ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) < max_chunk_size:
            current_chunk += sentence + ". "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

def collapse_word_repeats(text: str) -> str:
    return re.sub(r'\b(\w+)(?:\s+\1){2,}\b', r'\1', text)

def collapse_char_repeats(text: str) -> str:
    return re.sub(r'(?:\b(\S+)\b\s+){2,}', r'\1 ', text)

def deduplicate_sentences(text: str) -> str:
    seen, result = set(), []
    for sent in re.split(r'[.।]', text):
        s = sent.strip()
        if s and s not in seen:
            seen.add(s)
            result.append(s)
    return ". ".join(result)

def clean_summary(summary: str) -> str:
    summary = re.sub(r"<extra_id_\d+>", "", summary)
    summary = re.sub(r"http\S+|www\.\S+|\S+\.pdf", "", summary, flags=re.IGNORECASE)
    summary = re.sub(r"[.]{2,}", ".", summary)
    summary = re.sub(r"\s+", " ", summary)
    return summary.strip(" .,'\"-")

def enforce_script(text: str, lang: str) -> str:
    ranges = {
        "hi": r"[^\u0900-\u097F\s.,!?]", "mr": r"[^\u0900-\u097F\s.,!?]",
        "ta": r"[^\u0B80-\u0BFF\s.,!?]", "te": r"[^\u0C00-\u0C7F\s.,!?]",
        "bn": r"[^\u0980-\u09FF\s.,!?]", "kn": r"[^\u0C80-\u0CFF\s.,!?]",
        "ml": r"[^\u0D00-\u0D7F\s.,!?]", "gu": r"[^\u0A80-\u0AFF\s.,!?]",
        "or": r"[^\u0B00-\u0B7F\s.,!?]", "pa": r"[^\u0A00-\u0A7F\s.,!?]"
    }
    if lang in ranges:
        return re.sub(ranges[lang], "", text)
    return text

def stronger_telugu_cleaning(text: str) -> str:
    text = re.sub(r'(మధు\s*){2,}', "మధుమేహం ", text)
    text = re.sub(r'(క్యాన్సర్\s*){2,}', "క్యాన్సర్ ", text)
    text = re.sub(r'(ఆరోగ్యం\s*){2,}', "ఆరోగ్యం ", text)
    return text

def summarize_large_text(text, final_max_length=200, model="mbart", lang="en"):
    if model == "indicbart" and indicbart_summarizer:
        summarizer = indicbart_summarizer
    elif model == "mbart":
        summarizer = mbart_summarizer
    else:
        summarizer = mt5_summarizer if mt5_summarizer else mbart_summarizer

    chunks = chunk_text(text)
    chunk_summaries = []
    for i, chunk in enumerate(chunks, 1):
        print(f"[{model.upper()}] Summarizing chunk {i}/{len(chunks)}...")
        summary = summarizer(
            chunk,
            max_length=200,
            min_length=80,
            do_sample=False,
            num_beams=6,
            no_repeat_ngram_size=4,
            repetition_penalty=3.0,
            length_penalty=1.2
        )
        clean = collapse_word_repeats(summary[0]['summary_text'])
        clean = collapse_char_repeats(clean)
        clean = deduplicate_sentences(clean)
        clean = clean_summary(clean)
        clean = enforce_script(clean, lang)
        if lang == "te":
            clean = stronger_telugu_cleaning(clean)
        chunk_summaries.append(clean)

    combined_summary = " ".join(chunk_summaries)
    final_summary = summarizer(
        combined_summary,
        max_length=final_max_length,
        min_length=100,
        do_sample=False,
        num_beams=6,
        no_repeat_ngram_size=4,
        repetition_penalty=3.0,
        length_penalty=1.2
    )
    result = final_summary[0]['summary_text']
    result = collapse_word_repeats(result)
    result = collapse_char_repeats(result)
    result = deduplicate_sentences(result)
    result = clean_summary(result)
    result = enforce_script(result, lang)
    if lang == "te":
        result = stronger_telugu_cleaning(result)

    return result

def extract_text_from_file(file: UploadFile):
    if file.filename.endswith(".pdf"):
        reader = PyPDF2.PdfReader(file.file)
        text = "".join([page.extract_text() or "" for page in reader.pages])
    elif file.filename.endswith(".docx"):
        doc = docx.Document(file.file)
        text = "\n".join([para.text for para in doc.paragraphs])
    elif file.filename.endswith(".txt"):
        text = file.file.read().decode("utf-8")
    else:
        raise ValueError("Unsupported file format. Please upload PDF, DOCX, or TXT.")
    return text

# --- API Endpoint ---
@app.post("/summarize")
def summarize(
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
    length: str = Form("medium")
):
    try:
        if file:
            text_content = extract_text_from_file(file)
            source = file.filename
        elif text:
            text_content = text
            source = "textarea"
        else:
            return {"error": "Please provide either a file or text."}

        lang = detect_language(text_content)
        print(f"Detected language: {lang}")

        # ✅ Telugu and all Indic → IndicBART
        if lang == "te" and indicbart_summarizer:
            model_choice = "indicbart"
        elif lang in INDIC_LANGS and indicbart_summarizer:
            model_choice = "indicbart"
        elif lang in MBART_LANGS:
            model_choice = "mbart"
        else:
            model_choice = "mt5"

        if length == "short":
            final_len = 120
        elif length == "long":
            final_len = 300
        else:
            final_len = 200

        summary = summarize_large_text(
            text_content,
            final_max_length=final_len,
            model=model_choice,
            lang=lang
        )

        return {
            "source": source,
            "detected_language": lang,
            "model_used": model_choice,
            "summary_length": length,
            "summary": summary
        }

    except Exception as e1:
        return {"error": str(e1)}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
