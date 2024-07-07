from dotenv import load_dotenv
import gradio as gr

from graph import run_graph

load_dotenv()

def main():
  ui = gr.Interface(fn=run_graph, inputs="textbox", outputs="textbox")
  ui.launch()

if __name__ == "__main__":
  main()