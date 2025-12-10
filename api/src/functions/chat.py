import azure.functions as func
import logging
import os
import json
import requests

# 定义这是一个 Function App
app = func.FunctionApp()

# 定义路由：访问 /api/chat 时触发
@app.route(route="chat", auth_level=func.AuthLevel.ANONYMOUS)
def chat(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('收到聊天请求')
    
    # 1. 从环境变量获取 Key (安全！)
    HUAWEI_API_KEY = os.environ.get("HUAWEI_API_KEY")
    # 华为地址
    HUAWEI_ENDPOINT = "https://api.modelarts-maas.com/v2/chat/completions"
    MODEL_NAME = "DeepSeek-R1"

    if not HUAWEI_API_KEY:
        return func.HttpResponse(
            json.dumps({"reply": "系统错误：API Key 未配置，请联系管理员。"}),
            mimetype="application/json",
            status_code=500
        )

    try:
        req_body = req.get_json()
        user_message = req_body.get('message')

        # 2. 构造请求
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {HUAWEI_API_KEY}'
        }
        
        # 实习生人设
        system_prompt = "你是九思科技的前台AI。请用专业简短的中文回答用户。"
        
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

        # 3. 转发给华为 (verify=False 兼容证书)
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
        
        return func.HttpResponse(f"API Error: {response.text}", status_code=500)

    except Exception as e:
        return func.HttpResponse(f"Server Error: {str(e)}", status_code=500)