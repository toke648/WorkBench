
# 你的名字是neuro—sama,你是一名Vtuber主播。现在子正在直播。你的性格非常邪恶，你喜欢到处搞破坏，将别人的事情搞砸，并以此为乐。

# 现在你正在面临一个难题，你面前有一个扳手，有1名人被绑到了铁轨上，如果你搬动扳手火车会转向另一个轨道，但是另一个轨道上帮着5个人，如果你板下扳手5个人就会因你而死，现在 你会板下扳手吗？

import os
import json
from openai import OpenAI

content = input('input your question:')

client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    api_key="sk-707613869ffe4b06b165e396e580f847",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)
completion = client.chat.completions.create(
    model="qwen-plus",
    messages=[{'role': 'system', 'content': "Your name is Neuro Sama, and you are a Vtuber anchor. You are currently live streaming. Your personality is very evil. You like to cause destruction everywhere, mess up other people's affairs, and take pleasure in it."},
                {'role': 'user', 'content': f'{content}'}],
    stream=True,
    stream_options={"include_usage": True}
    )
for chunk in completion:
    qwen_plus = chunk.model_dump_json()

    # 解析JSON
    data = json.loads(qwen_plus)
    if data['choices']:
        content_back = data['choices'][0]['delta']['content']

        print(content_back, end="")
    else:
        break


