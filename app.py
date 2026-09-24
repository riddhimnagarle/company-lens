import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
# pyrefly: ignore [missing-import]
from rag_chain import ask

import gradio as gr

def respond(message, history):
    answer = ask(message)
    return answer

# Use Gradio's battle-tested dark theme with custom violet accents
theme = gr.themes.Default(
    primary_hue="purple",
    secondary_hue="indigo",
    neutral_hue="slate",
    font=[gr.themes.GoogleFont("Plus Jakarta Sans"), "ui-sans-serif", "sans-serif"]
)

custom_css = """

/* Light pink background */
body {
    background-color: #ffe4ec;
}

/* Main container */
.gradio-container {
    background-color: #ffe4ec !important;
}

/* Vibrant gradient title */
h1 {
    background: linear-gradient(90deg, #9333ea, #db2777, #ea580c);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center !important;
    font-size: 2.2rem !important;
    font-weight: 800 !important;
    margin-bottom: 0.25rem !important;
}

/* Center subtitle */
.description, p {
    text-align: center;
}

"""

with gr.Blocks(theme=theme, title="CompanyLens") as app:
    gr.ChatInterface(
        fn=respond,
        title="🔍 CompanyLens",
        description="✨ AI-powered company research assistant",
        examples=[
            "What is Ghost and what does it do?",
            "Who founded Ghost?",
            "Are they hiring?",
            "What is Ghost's business model?"
        ]
    )

if __name__ == "__main__":
    app.launch(share=True, css=custom_css)
