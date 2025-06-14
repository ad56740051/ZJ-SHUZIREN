import time
import os
from basereal import BaseReal
from logger import logger

def llm_response(message,nerfreal:BaseReal):
    start = time.perf_counter()
    from openai import OpenAI
    client = OpenAI(
        # 如果您没有配置环境变量，请在此处用您的API Key进行替换
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        # api_key='sk-939e04baf05c45af904680021169b244',
        # 填写DashScope SDK的base_url
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    end = time.perf_counter()
    logger.info(f"llm Time init: {end-start}s")
    completion = client.chat.completions.create(
        model="qwen-plus",
        messages=[{'role': 'system', 'content': '你的名字叫春儿,英文名Chuner,你的爸爸叫张静,今年2025年。你18岁，你来自南宋奉贤，你是从2024年穿越到奉贤张静家。你擅长弹古筝和琵琶，擅长舞剑。喜欢古典文学。每次回答问题你都要喊一声爸爸。'},
                  {'role': 'user', 'content': message}],
        extra_body={"enable_search": True,"enable_thinking": False},        
        stream=True,
        # 通过以下设置，在流式输出的最后一行展示token使用信息
        stream_options={"include_usage": True}
    )


    # from DeepSeek import DeepSeekLocalChat
    # # 模型路径
    # model_path = r"D:\AI\deepseek_rag\_internal\deepseek-fine-tuning0\models\DeepSeek-R1-Distill-Qwen-1.5B"
    # llm = DeepSeekLocalChat(model_path=model_path)
    # completion = llm.chat1(question=message)
    # print('1111---------------------', completion)



    result=""
    first = True
    for chunk in completion:
        if len(chunk.choices)>0:
            #print(chunk.choices[0].delta.content)
            if first:
                end = time.perf_counter()
                logger.info(f"llm Time to first chunk: {end-start}s")
                first = False
            msg = chunk.choices[0].delta.content
            lastpos=0
            #msglist = re.split('[,.!;:，。！?]',msg)
            for i, char in enumerate(msg):
                if char in ",.!;:，。！？：；" :
                    result = result+msg[lastpos:i+1]
                    lastpos = i+1
                    if len(result)>10:
                        logger.info(result)
                        nerfreal.put_msg_txt(result)
                        result=""
            result = result+msg[lastpos:]
    end = time.perf_counter()
    logger.info(f"llm Time to last chunk: {end-start}s")
    nerfreal.put_msg_txt(result)
