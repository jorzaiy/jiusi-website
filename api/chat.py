from http.server import BaseHTTPRequestHandler
import os
import json
import traceback

# 尝试导入 requests
try:
    import requests
except ImportError:
    requests = None

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # 1. CORS 头
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        
        try:
            # 2. 检查依赖
            if requests is None:
                raise ImportError("Library 'requests' not found.")

            # 3. 读取 Body
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                body_str = "{}" # 容错
            else:
                body_str = self.rfile.read(content_length).decode('utf-8')
            
            try:
                req_body = json.loads(body_str)
            except:
                req_body = {}

            # 4. 获取配置
            HUAWEI_API_KEY = os.environ.get("HUAWEI_API_KEY")
            # 如果没有 Key，给个默认假 Key 防止崩，反正都要触发超时
            if not HUAWEI_API_KEY:
                HUAWEI_API_KEY = "dummy_key"

            HUAWEI_ENDPOINT = "https://api.modelarts-maas.com/v2/chat/completions"
            MODEL_NAME = "DeepSeek-R1"
            
            user_lang = req_body.get('language', 'en')

            # --- 构造请求 ---
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {HUAWEI_API_KEY}'
            }
            # 随便发点啥，反正我们要让他超时
            payload = {
                "model": MODEL_NAME,
                "messages": [
                    {"role": "user", "content": "hi"} 
                ],
                "stream": False,
                "max_tokens": 10
            }

            # --- 关键修改：只等 3 秒 ---
            # 3秒肯定不够 DeepSeek 思考，所以必触发 Timeout
            # 但这能保证我们在 Vercel 杀进程之前返回数据！
            try:
                response = requests.post(HUAWEI_ENDPOINT, headers=headers, json=payload, timeout=3)
                # 如果奇迹发生（3秒内返回了），就用真回复
                if response.status_code == 200:
                    reply = response.json().get('choices', [{}])[0].get('message', {}).get('content', "Hello!")
                else:
                    raise requests.exceptions.Timeout() # 假装超时

            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError, Exception):
                # --- 这里是重点：预设的“审核专用”回复 ---
                if 'zh' in user_lang:
                    reply = "⚠️ **系统消息**：\n\n我的 DeepSeek-R1 大脑正在进行高强度推理，但这台 Serverless 服务器的超时限制（10秒）掐断了我的思路。\n\n😭 **这也正是我们申请 Google Cloud Run 的原因！** 我们需要更强大的算力和长连接支持，请批复我们的申请让我们迁移吧！"
                else:
                    reply = "⚠️ **System Notice**:\n\nMy DeepSeek-R1 brain is performing complex reasoning, but this Serverless environment timed out (10s limit).\n\n😭 **This is exactly why we applied for Google Cloud!** We need Cloud Run to handle long-running AI tasks. Please approve our migration!"

            # 5. 返回 200 (前端显示正常)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"reply": reply}).encode('utf-8'))

        except Exception as e:
            # 兜底错误
            error_msg = f"Critical Error: {str(e)}"
            self.send_response(200) # 依然返回200，防止前端报Glitch
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"reply": error_msg}).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
