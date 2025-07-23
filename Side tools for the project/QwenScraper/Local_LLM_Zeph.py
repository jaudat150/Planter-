from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch

# GPU Info (for debugging)
print("Available GPUs:", torch.cuda.device_count())
if torch.cuda.is_available():
    print("Current GPU:", torch.cuda.current_device())
    print("GPU Name:", torch.cuda.get_device_name(torch.cuda.current_device()))

# Model Setup
#we can either use this or just use the model right from hugging face as model_name = "HuggingFaceH4/zephyr-7b-beta"
#set ur model in here
model_name = r"C:\Users\example\.cache\huggingface\hub\models--HuggingFaceH4--zephyr-7b-beta\snapshots\722c3a7f7q1tf10c7a701c60881cd93df611221c"
tokenizer = AutoTokenizer.from_pretrained(model_name)

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    load_in_4bit=True,
    device_map="auto",
    torch_dtype=torch.float16  # Helps with memory & speed
)

# Pipeline with safer settings
pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=817,
    temperature=0.7,
    top_p=0.9,
    do_sample=True,
    pad_token_id=tokenizer.eos_token_id,
    eos_token_id=tokenizer.eos_token_id
)

def generate_trivia(prompt):

    response = pipe(prompt)
    return response[0]['generated_text']    