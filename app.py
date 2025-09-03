from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import langid
import PyPDF2
import docx
import io

# --------------------
# Load mT5 XLSum Model
# --------------------
print("Loading mT5 XLSum...")
model_name = "csebuetnlp/mT5_multilingual_XLSum"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
summarizer = pipeline("summarization", model=model, tokenizer=tokenizer)

# --------------------
# Helpers
# --------------------
def detect_language(text: str) -> str:
    lang, _ = langid.classify(text)
    return lang

def extract_text_from_file(file: UploadFile) -> str:
    if file.filename.endswith(".pdf"):
        reader = PyPDF2.PdfReader(file.file)
        return " ".join([page.extract_text() or "" for page in reader.pages])
    elif file.filename.endswith(".docx"):
        doc = docx.Document(io.BytesIO(file.file.read()))
        return " ".join([para.text for para in doc.paragraphs])
    elif file.filename.endswith(".txt"):
        return file.file.read().decode("utf-8")
    else:
        raise ValueError("Unsupported file format. Use PDF, DOCX, or TXT.")

# --------------------
# FastAPI App
# --------------------
app = FastAPI(title="Multilingual AI Summarizer")

@app.post("/summarize")
async def summarize_api(
    text: str = Form(None),
    file: UploadFile = None,
    max_length: int = Form(150),
    min_length: int = Form(40),
):
    try:
        if file:
            text_content = extract_text_from_file(file)
        elif text:
            text_content = text
        else:
            return JSONResponse({"error": "No input provided"}, status_code=400)

        lang = detect_language(text_content)
        outputs = summarizer(
            "summarize: " + text_content,
            max_length=max_length,
            min_length=min_length,
            do_sample=False
        )
        summary = outputs[0]["summary_text"]

        return {"language": lang, "summary": summary}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
