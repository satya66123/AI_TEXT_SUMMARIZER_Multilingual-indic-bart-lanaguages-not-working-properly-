import gradio as gr
import requests

API_URL = "http://127.0.0.1:8000/summarize"

def summarize_gradio(text, file):
    try:
        data = {"text": text}
        files = None
        if file:
            files = {"file": open(file.name, "rb")}
            data = {}

        response = requests.post(API_URL, data=data, files=files)
        if response.status_code == 200:
            result = response.json()
            return f"🌍 Language: {result.get('language')}\n\n📝 Summary:\n{result.get('summary')}"
        else:
            return f"❌ Error: {response.text}"
    except Exception as e:
        return f"❌ Exception: {str(e)}"

demo = gr.Interface(
    fn=summarize_gradio,
    inputs=[
        gr.Textbox(label="Enter text", lines=10, placeholder="Paste text here..."),
        gr.File(label="Upload file (.pdf, .docx, .txt)")
    ],
    outputs="text",
    title="🌍 Multilingual AI Summarizer (Frontend)"
)

if __name__ == "__main__":
    demo.launch()
