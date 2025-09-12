import numpy as np

# 假设网络输出的logits（10张图片，10个类别）
logits = np.random.randn(10, 10) # 随机生成
print(logits)

def softmax(logits):
    exp_values = np.exp(logits - np.max(logits, axis=1, keepdims=True))
    probabilities = exp_values / np.sum(exp_values, axis=1, keepdims=True)
    return probabilities


probabilities = softmax(logits)
print(sum(probabilities))

predicted_classes = np.argmax(probabilities, axis=1)

print("Probabilities: \n", probabilities)
print("Predicted Classes: ", predicted_classes)