import requests

url = "http://127.0.0.1:9872/api/get_speakers"
response = requests.get(url)

if response.status_code == 200:
    speakers = response.json()
    print("可用音色:", speakers)
else:
    print("获取音色失败:", response.text)
