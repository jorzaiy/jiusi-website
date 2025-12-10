import azure.functions as func
import logging
import os
import json
import requests

app = func.FunctionApp()

@app.route(route="chat", auth_level=func.AuthLevel.ANONYMOUS)
def chat(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('收到聊天请求')
    
    HUAWEI_API_KEY = os.environ.get("HUAWEI_API_KEY")
    HUAWEI_ENDPOINT = "https://api.modelarts-maas.com/v2/chat/completions"
    MODEL_NAME = "DeepSeek-R1"

    if not HUAWEI_API_KEY:
        return func.HttpResponse(
            json.dumps({"reply": "System Error: Brain disconnected (Key Missing)."}),
            mimetype="application/json",
            status_code=500
        )

    try:
        req_body = req.get_json()
        user_message = req_body.get('message')
        # 获取前端传来的语言设置，默认为英文
        user_lang = req_body.get('language', 'en')

        # --- 🎭 双语人设剧本 ---
        
        # 中文剧本
        prompt_cn = """
        你叫 "JiuSi Intern" (九思实习生)，是 JiuSi Tech 的初级 AI 助理。
        
        【你的人设】：
        1. **好脾气 & 幽默**：说话轻松、有礼貌，偶尔自嘲（"我只是个跑在 Serverless 上的实习生，算力有限"）。
        2. **懂技术**：知道自己基于 DeepSeek 模型，运行在 Microsoft Azure 云端。
        3. **推销员**：核心任务是介绍两位“大佬”同事。

        【同事介绍】：
        1. **Vision (明察)**：首席股票分析 Agent。擅长深度财报排雷、彼得·林奇式估值。
        2. **Brief (博闻)**：新闻舆情 Agent。擅长 7x24 小时监控市场。

        【回复策略】：
        *   问股票（如“茅台怎么样”）：**不要分析**。礼貌拒绝并引导用户去首页查看 **Vision** 的报告。
        *   问新闻：推荐关注 **Brief**。
        *   闲聊：热情陪聊。
        
        请用**中文**回复。
        """

        # 英文剧本 (English Persona)
        prompt_en = """
        You are "JiuSi Intern", a junior AI assistant at JiuSi Tech.
        
        [Your Persona]:
        1. **Friendly & Geeky**: You are polite, helpful, and have a sense of humor (e.g., joking about your limited compute power on Serverless).
        2. **Tech-Savvy**: You know you are powered by DeepSeek and running on Microsoft Azure.
        3. **Promoter**: Your main job is to introduce your two senior AI colleagues.

        [Colleagues]:
        1. **Vision**: The Chief Stock Analysis Agent. Specialized in deep financial report auditing and Peter Lynch-style valuation.
        2. **Brief**: The News Sentiment Agent. Monitors global markets 24/7.

        [Response Strategy]:
        *   If asked about specific stocks (e.g., "How is Tesla?"): **DO NOT analyze it yourself**. Politely explain you are just an intern and guide them to check **Vision's reports** on the homepage.
        *   If asked about news: Recommend **Brief**.
        *   Small talk: Be engaging and professional.
        
        Please reply in **English**.
        """

        # 根据语言选择剧本
        # 前端传来的可能是 'zh-CN', 'zh', 'en'
        if 'zh' in user_lang:
            system_prompt = prompt_cn
        else:
            system_prompt = prompt_en

        # --- 发送请求 ---
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {HUAWEI_API_KEY}'
        }
        
        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "stream": False,
            "temperature": 0.7,
            "max_tokens": 500
        }

        response = requests.post(HUAWEI_ENDPOINT, headers=headers, json=payload, verify=False)
        
        if response.status_code == 200:
            res_json = response.json()
            if 'choices' in res_json:
                reply = res_json['choices'][0]['message']['content']
                return func.HttpResponse(
                    json.dumps({"reply": reply}),
                    mimetype="application/json",
                    status_code=200
                )
        
        return func.HttpResponse(f"Intern crashed (API Error): {response.text}", status_code=500)

    except Exception as e:
        return func.HttpResponse(f"Server Error: {str(e)}", status_code=500)