from http.server import BaseHTTPRequestHandler
import os
import json
import requests

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # 1. 简单的 CORS 处理 (防止跨域报错)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        
        # 2. 读取前端发来的数据
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            req_body = json.loads(post_data.decode('utf-8'))
        except Exception:
            self.send_error(400, "Invalid JSON")
            return

        # 3. 获取配置
        HUAWEI_API_KEY = os.environ.get("HUAWEI_API_KEY")
        # 注意：这里继续用你的华为/DeepSeek接口，审核时这是完美的“迁移理由”
        HUAWEI_ENDPOINT = "https://api.modelarts-maas.com/v2/chat/completions" 
        MODEL_NAME = "DeepSeek-R1"

        if not HUAWEI_API_KEY:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"reply": "System Error: Brain disconnected (Key Missing)."}).encode('utf-8'))
            return

        user_message = req_body.get('message')
        user_lang = req_body.get('language', 'en')

        # --- 🎭 剧本保持不变 (直接复用你的) ---
        prompt_cn = """
        你叫 "JiuSi Intern" (九思实习生)，是 JiuSi Tech 的初级 AI 助理。
        【你的人设】：
        1. **好脾气 & 幽默**：说话轻松、有礼貌，偶尔自嘲（"我只是个跑在 Serverless 上的实习生，算力有限"）。
        2. **懂技术**：知道自己基于 DeepSeek 模型。
        3. **推销员**：核心任务是介绍两位“大佬”同事：Vision (首席股票分析) 和 Brief (新闻舆情)。
        【回复策略】：
        *   问股票：不要分析，引导去看 Vision 的报告。
        *   问新闻：推荐 Brief。
        请用**中文**回复。
        """

        prompt_en = """
        You are "JiuSi Intern", a junior AI assistant at JiuSi Tech.
        [Persona]: Friendly, Geeky, Promoter of Vision (Stock Analyst) and Brief (News Agent).
        [Strategy]: Do not analyze stocks yourself, refer to Vision. Refer news to Brief.
        Please reply in **English**.
        """

        system_prompt = prompt_cn if 'zh' in user_lang else prompt_en

        # --- 发送请求给 DeepSeek/华为 ---
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

        try:
            # Vercel 环境下 verify=False 可能不是必须的，但为了兼容性保留
            response = requests.post(HUAWEI_ENDPOINT, headers=headers, json=payload, verify=False)
            
            if response.status_code == 200:
                res_json = response.json()
                reply = "Error parsing response"
                if 'choices' in res_json:
                    reply = res_json['choices'][0]['message']['content']
                
                # 成功返回
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"reply": reply}).encode('utf-8'))
            else:
                # API 报错
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f"Upstream API Error: {response.text}".encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Server Error: {str(e)}".encode('utf-8'))

    # 处理 OPTIONS 请求 (解决跨域预检)
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
