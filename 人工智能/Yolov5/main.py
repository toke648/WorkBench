import json
import requests
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

# Run inference on an image
url = "https://predict.ultralytics.com"
headers = {"x-api-key": "0dc09e936476477f004ebff630b90eda02da064141"}
image = "Leonardo_Anime_XL_Anime_three_views_cat_mother_light_and_beaut_2.jpg"
data = {"model": "https://hub.ultralytics.com/models/CitZEb3uSxzH8NACWutC", "imgsz": 640, "conf": 0.25, "iou": 0.45}
with open(image, "rb") as f:
	response = requests.post(url, headers=headers, data=data, files={"file": f})

# Check for successful response
response.raise_for_status()

# Print inference results
result = json.dumps(response.json(), indent=2)

print(result)
print(type(result))

image = Image.open(image).convert('RGB')

image_array = np.array(image)  # 转换为 NumPy 数组

plt.imshow(image_array)

plt.show()