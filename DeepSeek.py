import os
import torch
from modelscope import AutoModelForCausalLM, AutoTokenizer

# 设置环境变量（可选，仅用于调试）
# os.environ['CUDA_LAUNCH_BLOCKING'] = '1'


class DeepSeekLocalChat:
    def __init__(self, model_path="deepseek-r1:7b"):
        self.model, self.tokenizer = self.init_model(model_path)

    def init_model(self, path):
        # 加载模型和分词器
        model = AutoModelForCausalLM.from_pretrained(
            path,
            device_map="auto",
            trust_remote_code=True
        ).eval()
        tokenizer = AutoTokenizer.from_pretrained(path, trust_remote_code=True)
        return model, tokenizer

    def chat(self, question):
        try:
            # 使用 generate 方法生成回答
            inputs = self.tokenizer.encode(question, return_tensors="pt").to(self.model.device)
            outputs = self.model.generate(inputs)
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return response
        except Exception as e:
            return f"Error: {e}"

    def chat1(self, question):
        try:
            # 使用 generate 方法生成回答
            inputs = self.tokenizer.encode(question, return_tensors="pt").to(self.model.device)
            outputs = self.model.generate(inputs)
            return outputs
        except Exception as e:
            return f"Error: {e}"

def test():
    # 模型路径
    model_path = r"D:\AI\deepseek_rag\_internal\deepseek-fine-tuning0\models\DeepSeek-R1-Distill-Qwen-1.5B"

    llm = DeepSeekLocalChat(model_path=model_path)
    answer = llm.chat(question="如何应对压力？")
    print(answer)

if __name__ == '__main__':
    test()