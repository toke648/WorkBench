from openai import OpenAI
import json
import time

# Function to get response from the language model
def large_language_model(content,conversation_history):
    client = OpenAI(
        api_key="sk-707613869ffe4b06b165e396e580f847",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    # Requesting completion from the conversation history
    completion = client.chat.completions.create(
        model="qwen-plus",
        messages=conversation_history
    )
    qwen_plus = completion.model_dump_json()
    data = json.loads(qwen_plus)
    result = data['choices'][0]['message']['content']
    return result

