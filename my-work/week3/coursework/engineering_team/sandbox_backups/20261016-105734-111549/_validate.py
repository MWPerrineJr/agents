import gradio as gr
import app

assert isinstance(app.demo, gr.Blocks), (
    "app.demo must be a Gradio Blocks instance"
)
print("Pass: app imports and constructs a Gradio Blocks UI")