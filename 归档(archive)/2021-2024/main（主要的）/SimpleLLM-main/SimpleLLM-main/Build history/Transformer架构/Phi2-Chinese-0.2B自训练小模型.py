from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig
import torch

device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

tokenizer = AutoTokenizer.from_pretrained('charent/Phi2-Chinese-0.2B')
model = AutoModelForCausalLM.from_pretrained('charent/Phi2-Chinese-0.2B').to(device)

txt = '感冒了要怎么办？'
prompt = f"##提问:\n{txt}\n##回答:\n"

# greedy search
gen_conf = GenerationConfig(
    num_beams=1,
    do_sample=False,
    max_length=320,
    max_new_tokens=256,
    no_repeat_ngram_size=4,
    eos_token_id=tokenizer.eos_token_id,
    pad_token_id=tokenizer.pad_token_id,
)

tokend = tokenizer.encode_plus(text=prompt)
input_ids, attention_mask = torch.LongTensor([tokend.input_ids]).to(device), \
    torch.LongTensor([tokend.attention_mask]).to(device)

outputs = model.generate(
    inputs=input_ids,
    attention_mask=attention_mask,
    generation_config=gen_conf,
)

outs = tokenizer.decode(outputs[0].cpu().numpy(), clean_up_tokenization_spaces=True, skip_special_tokens=True,)
print(outs)
