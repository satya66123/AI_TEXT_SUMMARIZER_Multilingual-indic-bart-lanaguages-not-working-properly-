# AI_TEXT_SUMMARIZER_Multilingual-indic-bart-lanaguages-not-working-properly-
Multilingual AI Summarizer 🚀

This project is a FastAPI-based AI Summarization Tool that supports multiple languages, with a focus on Indic languages (Telugu, Hindi, Tamil, etc.).
It allows users to upload text, PDF, or DOCX files, and generates concise summaries using state-of-the-art Hugging Face models like mBART, mT5, and IndicBART.

✨ Features

📄 File Upload Support → Summarize .txt, .pdf, .docx files.

🌍 Multilingual → Supports English + 10+ Indic languages.

🔄 Automatic Language Detection → Uses langid to choose the right model.

🧹 Post-processing → Removes repetitions (e.g., “మధు మధు మధు”) and ensures clean output.

⚡ FastAPI Backend → REST API ready for deployment.

📊 Customizable Summary Lengths → Short, Medium, Long.

🛠️ Tech Stack

Python 3.12

FastAPI
 → Web framework

Transformers
 → NLP models

PyTorch
 → Model inference

langid
 → Language detection

PyPDF2
 & python-docx
 → File parsing

⚙️ Installation
1️⃣ Clone the Repo
git clone https://github.com/your-username/multilingual-ai-summarizer.git
cd multilingual-ai-summarizer

2️⃣ Create Virtual Environment
python -m venv .venv
.venv\Scripts\activate   # On Windows
source .venv/bin/activate  # On Linux/Mac

3️⃣ Install Dependencies
pip install -r requirements.txt

▶️ Usage
Run the FastAPI server:
uvicorn app:app --reload

Open the API docs:

👉 Go to http://127.0.0.1:8000/docs

Here you can:

Upload files (PDF, DOCX, TXT)

Enter text directly

Select summary length (short/medium/long)

📂 Project Structure
📦 multilingual-ai-summarizer
 ┣ 📜 app.py              # FastAPI backend
 ┣ 📜 requirements.txt    # Dependencies
 ┣ 📜 README.md           # Project documentation
 ┗ 📜 .gitignore          # Ignore venv, cache, etc.

🚀 Deployment

Local server: uvicorn app:app --reload

Cloud (Heroku, Render, etc.) → push repo and add Procfile.

Hugging Face Spaces → deploy directly with Gradio + Transformers.

📌 Challenges Faced

⚖️ Choosing between general models (mBART, mT5) vs fine-tuned Indic models.

🈹 Handling Indic languages with correct tokenizers (sentencepiece, sacremoses).

🔄 Repetitive outputs in Telugu (e.g., “మధు మధు మధు”) → fixed with regex cleaning.

💻 Version conflicts (PyTorch, Transformers, NumPy).

📉 Evaluation of summaries in Indic languages (no strong automatic metrics).

🤝 Contributing

Pull requests are welcome!
If you find bugs or want to add new features (e.g., frontend UI), open an issue.

📜 License

This project is licensed under the MIT License.

⚡ With this README.md, your repo will have:
✔️ Clear description
✔️ Setup + usage instructions
✔️ Challenges explained
