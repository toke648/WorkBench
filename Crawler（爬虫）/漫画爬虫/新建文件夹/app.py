# app.py
import gradio as gr
from manga_utils import search_manga, download_manga

search_log = gr.State("")

def do_search(keyword, max_results):
    results = search_manga(keyword, max_results=max_results)
    if not results:
        return [], "❌ 没有找到任何结果，请换个关键词试试。"

    gallery_data = []
    for item in results:
        gallery_data.append(
            (item['cover'], f"{item['title']}\n{item['desc']}")
        )
    return gallery_data, results

def handle_download(evt: gr.SelectData, results):
    selected_title = evt.value.split("\n")[0].strip()
    selected = next((r for r in results if r['title'] == selected_title), None)
    if selected:
        log = download_manga(selected)
        return log
    return "❌ 无法找到该漫画信息。"

with gr.Blocks(title="漫画爬虫神器") as demo:
    gr.Markdown("## 🔍 搜索漫画并下载")
    
    with gr.Row():
        keyword_input = gr.Textbox(label="漫画名称", placeholder="请输入关键词")
        max_slider = gr.Slider(1, 20, value=10, step=1, label="最多显示多少结果")
        search_btn = gr.Button("搜索")

    results_output = gr.Gallery(label="搜索结果（点击封面下载）", show_label=True, columns=5)
    log_output = gr.Textbox(label="下载日志", lines=20)

    results_state = gr.State([])

    search_btn.click(
        fn=do_search,
        inputs=[keyword_input, max_slider],
        outputs=[results_output, results_state]
    )

    results_output.select(fn=handle_download, inputs=results_state, outputs=log_output)

demo.launch()
