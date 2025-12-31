import requests

url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

payload = {
    "model": "glm-4.5-flash",
    "messages": [
        {
            "role": "system",
            "content": "你是一个有用的AI助手。"
        },
        {
            "role": "user",
            "content": "请介绍一下人工智能的发展历程。"
        }
    ],
    "temperature": 1,
    "max_tokens": 65536,
    "stream": False
}
headers = {
    "Authorization": "Bearer fec3a7656a9947c3aacf333eff2f0480.OrnWK7pqcCd16RO8",
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)
print(response.status_code)
print(response.json())