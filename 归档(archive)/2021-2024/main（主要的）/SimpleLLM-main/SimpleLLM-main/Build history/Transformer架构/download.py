from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

model_id = 'charent/ChatLM-mini-Chinese'

# 如果无法连接huggingface，打开以下两行代码的注释，将从modelscope下载模型文件，模型文件保存到'./model_save'目录
from modelscope import snapshot_download
model_id = snapshot_download(model_id, cache_dir='./model_save')

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

"""
Model

(shared): Embedding(29298, 768)
(embed_tokens): Embedding(29298, 768)
(encoder): T5Stack(
  (block): ModuleList(
    (0): T5Block(
      (layer): ModuleList(
        (0): T5LayerSelfAttention(
          (SelfAttention):
            (q): Linear(in_features=768, out_features=768, bias=False)
        )
      )
    )
  )
)

嵌入层（Embedding）

(shared): Embedding(29298, 768)
(embed_tokens): Embedding(29298, 768)
词嵌入层：将文本转换为 768 维向量（即 Embedding(29298, 768)）。
29298 是词表大小（vocabulary size），表示该模型支持的单词或 token 数量。
768 是嵌入向量的维度，每个 token 被映射到 768 维的表示。

你的模型是 T5（Text-To-Text Transfer Transformer），它是一种Seq2Seq（序列到序列）模型，常用于文本生成、翻译、摘要等任务。T5 结构包含：

Encoder（编码器）：处理输入文本，提取特征。
Decoder（解码器）：根据编码器的输出，生成目标文本。
lm_head（输出层）：将解码器的输出映射回词表（Vocabulary），生成最终文本。
"""
tokenizer = AutoTokenizer.from_pretrained(model_id)
print(tokenizer.model_input_names)
model = AutoModelForSeq2SeqLM.from_pretrained(model_id, trust_remote_code=True).to(device)
print(model)

txt = '你是谁？'

encode_ids = tokenizer([txt])
input_ids, attention_mask = torch.LongTensor(encode_ids['input_ids']), torch.LongTensor(encode_ids['attention_mask'])

outs = model.my_generate(
    input_ids=input_ids.to(device),
    attention_mask=attention_mask.to(device),
    max_seq_len=256,
    search_type='beam',
)

outs_txt = tokenizer.batch_decode(outs.cpu().numpy(), skip_special_tokens=True, clean_up_tokenization_spaces=True)
print(outs_txt[0])