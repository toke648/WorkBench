import os
import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    TrainingArguments, 
    Trainer,
    TextDataset,
    DataCollatorForLanguageModeling
)
from torch.utils.data import Dataset, DataLoader
from tqdm import tqdm
import numpy as np

# 环境配置
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# 超参数配置
class Config:
    # 数据参数
    data_path = "./processed_data.txt"
    max_length = 128
    batch_size = 8  # 对于预训练模型，可以适当减小batch_size
    
    # 模型参数
    model_name = "microsoft/DialoGPT-small"  # 可以选择: "gpt2", "distilgpt2", "microsoft/DialoGPT-medium"
    
    # 训练参数
    epochs = 3
    learning_rate = 5e-5
    warmup_steps = 100
    save_steps = 500
    logging_steps = 100
    eval_steps = 200

# 加载预训练模型和分词器
print("Loading pretrained model and tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(Config.model_name)
model = AutoModelForCausalLM.from_pretrained(Config.model_name).to(device)

# 设置填充token
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

# 数据预处理函数
def format_qa_data(input_file, output_file):
    """将QA数据格式化为训练文本"""
    formatted_lines = []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for line in lines:
        if '\t' in line:
            question, answer = line.strip().split('\t', 1)
            # 多种格式化方式，选择一种
            formatted = f"用户: {question}\n助手: {answer}{tokenizer.eos_token}"
            # 或者: formatted = f"Q: {question}\nA: {answer}{tokenizer.eos_token}"
            # 或者: formatted = f"{question} {answer}{tokenizer.eos_token}"
            formatted_lines.append(formatted)
    
    # 保存格式化后的数据
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(formatted_lines))
    
    print(f"Formatted {len(formatted_lines)} QA pairs")
    return formatted_lines

# 准备训练数据
print("Preparing training data...")
formatted_train_file = "formatted_train_data.txt"
format_qa_data(Config.data_path, formatted_train_file)

# 创建数据集类
class QADataset(Dataset):
    def __init__(self, tokenizer, file_path, block_size=128):
        self.examples = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # 按行分割
        lines = text.split('\n')
        for line in lines:
            if line.strip():
                # 对每个样本进行编码
                encoding = tokenizer(
                    line, 
                    max_length=block_size, 
                    padding='max_length', 
                    truncation=True,
                    return_tensors='pt'
                )
                self.examples.append({
                    'input_ids': encoding['input_ids'].flatten(),
                    'attention_mask': encoding['attention_mask'].flatten()
                })
    
    def __len__(self):
        return len(self.examples)
    
    def __getitem__(self, idx):
        return self.examples[idx]

# 创建数据收集器
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False,  # 使用因果语言建模而不是掩码语言建模
)

# 加载数据集
train_dataset = QADataset(tokenizer, formatted_train_file, Config.max_length)

# 训练参数设置
training_args = TrainingArguments(
    output_dir="./fine-tuned-model",
    overwrite_output_dir=True,
    num_train_epochs=Config.epochs,
    per_device_train_batch_size=Config.batch_size,
    save_steps=Config.save_steps,
    save_total_limit=2,
    prediction_loss_only=True,
    learning_rate=Config.learning_rate,
    warmup_steps=Config.warmup_steps,
    logging_dir="./logs",
    logging_steps=Config.logging_steps,
    evaluation_strategy="no",  # 如果没有验证集，设为"no"
    # 如果数据量大，可以开启以下选项
    # dataloader_pin_memory=False,
    # dataloader_num_workers=2,
)

# 创建Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    data_collator=data_collator,
    train_dataset=train_dataset,
    tokenizer=tokenizer,
)

# 开始训练
print("Starting training...")
trainer.train()

# 保存微调后的模型
print("Saving fine-tuned model...")
trainer.save_model()
tokenizer.save_pretrained("./fine-tuned-model")

# 生成回复函数
def generate_response(model, tokenizer, input_text, max_length=50, temperature=0.7):
    """生成回复"""
    model.eval()
    
    # 格式化输入
    prompt = f"用户: {input_text}\n助手:"
    
    # 编码输入
    inputs = tokenizer.encode(prompt, return_tensors='pt').to(device)
    
    # 生成回复
    with torch.no_grad():
        outputs = model.generate(
            inputs,
            max_length=inputs.shape[1] + max_length,
            temperature=temperature,
            do_sample=True,
            top_k=50,
            top_p=0.9,
            pad_token_id=tokenizer.eos_token_id,
            no_repeat_ngram_size=2,
        )
    
    # 解码并提取回复部分
    full_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # 提取助手回复部分
    if "助手:" in full_text:
        response = full_text.split("助手:")[-1].strip()
    else:
        response = full_text.replace(prompt, "").strip()
    
    return response

# 加载微调后的模型进行测试
print("Loading fine-tuned model for testing...")
fine_tuned_model = AutoModelForCausalLM.from_pretrained("./fine-tuned-model").to(device)
fine_tuned_tokenizer = AutoTokenizer.from_pretrained("./fine-tuned-model")

# 交互测试
def interactive_chat():
    print("开始对话测试（输入 'exit' 退出）")
    print("=" * 50)
    
    while True:
        try:
            user_input = input("你: ").strip()
            if user_input.lower() in ['exit', 'quit', '退出']:
                break
            
            if not user_input:
                continue
            
            response = generate_response(fine_tuned_model, fine_tuned_tokenizer, user_input)
            print(f"助手: {response}")
            print("-" * 30)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"生成错误: {e}")
            continue

# 测试一些示例问题
def test_examples():
    test_questions = [
        "你好",
        "你叫什么名字？",
        "1+1等于多少？",
        "你会做什么？",
        "今天的天气怎么样？"
    ]
    
    print("测试示例问题:")
    print("=" * 50)
    
    for question in test_questions:
        response = generate_response(fine_tuned_model, fine_tuned_tokenizer, question)
        print(f"Q: {question}")
        print(f"A: {response}")
        print("-" * 30)

# 运行测试
if __name__ == "__main__":
    # 测试示例问题
    test_examples()
    
    # 开始交互对话
    interactive_chat()