from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch
import os

MODEL_NAME = "meta-llama/Llama-3.2-3B-Instruct"
HF_TOKEN = os.environ.get("HF_TOKEN")  # or hardcode for testing

_device = "cuda" if torch.cuda.is_available() else "cpu"
_pipe = None

def get_pipeline():
    global _pipe
    if _pipe is None:
        print(f"Loading model {MODEL_NAME} on {_device}...")
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, token=HF_TOKEN)

        if _device == "cuda":
            model = AutoModelForCausalLM.from_pretrained(
                MODEL_NAME,
                dtype=torch.float16,
                device_map="auto",
                token=HF_TOKEN,
            )
            _pipe = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
            )  # no device= when using device_map
        else:
            model = AutoModelForCausalLM.from_pretrained(
                MODEL_NAME,
                dtype=torch.float16,
                token=HF_TOKEN,
            )
            _pipe = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                device=-1,
            )
    return _pipe


def generate(prompt: str, max_new_tokens: int = 64) -> str:
    pipe = get_pipeline()
    out = pipe(
        prompt,
        max_new_tokens=max_new_tokens,
        do_sample=False,
        temperature=0.0,
        pad_token_id=pipe.tokenizer.eos_token_id,
    )
    return out[0]["generated_text"]

if __name__ == "__main__":
    reply = generate("You are a financial IE system. Say 'OK' and nothing else.")
    print("MODEL OUTPUT:\n", reply)
