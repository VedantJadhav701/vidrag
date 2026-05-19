"""Gradio web interface for VidRAG."""
import gradio as gr

from ingest import ingest
from query import query_video

def process_video(url: str, question: str, interval: int = 30) -> str:
    """Ingest video if needed and answer question."""
    client, collection = ingest(url)
    answer = query_video(collection, client, question)
    return answer

with gr.Blocks(title="VidRAG – See what you ask") as demo:
    gr.Markdown("# 🎥 VidRAG: Visual Video Q&A")
    with gr.Row():
        url_input = gr.Textbox(label="YouTube URL", placeholder="https://youtu.be/...")
        interval_slider = gr.Slider(10, 60, value=30, label="Frame interval (seconds)")
    question_input = gr.Textbox(label="Your question", placeholder="What is on the whiteboard?")
    answer_output = gr.Textbox(label="Answer", lines=5)
    submit_btn = gr.Button("Ask")
    submit_btn.click(
        fn=process_video,
        inputs=[url_input, question_input, interval_slider],
        outputs=answer_output,
    )

if __name__ == "__main__":
    demo.launch()
