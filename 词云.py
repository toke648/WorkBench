import random
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# 生成100个随机词汇
random_words = ['word' + str(random.randint(1, 100)) for _ in range(100)]

# 将词汇列表转换为一个长字符串
text = ' '.join(random_words)

# 生成词云
wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)

# 显示词云
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.show()