from tokenizers import Tokenizer, models, trainers, pre_tokenizers

# 1. 创建 BPE Tokenizer
tokenizer = Tokenizer(models.BPE())
# 2. 训练 Tokenizer+
trainer = trainers.BpeTrainer(special_tokens=["<pad>", "<bos>", "<eos>"], vocab_size=10000)
tokenizer.pre_tokenizer = pre_tokenizers.Whitespace()
tokenizer.train(['wiki_cleaned.txt'], trainer)

# 3. 保存 Tokenizer
tokenizer.save("bpe_tokenizer.json")

# 4. 测试 Tokenizer
encoded = tokenizer.encode("hi")
print("编码:", encoded.tokens)
print("解码:", tokenizer.decode(encoded.ids))