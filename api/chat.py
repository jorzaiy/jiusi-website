from http.server import BaseHTTPRequestHandler
import os
import json
import traceback  # 引入这个用来打印错误堆栈

# 尝试导入 requests，如果失败则记录错误（防止因为缺库直接崩掉 500）
try:
    import requests
except ImportError:
    requests = None

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # 1. 设置跨域头 (CORS)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        
        try:
            # 2. 检查依赖库是否安装
            if requests is None:
                raise ImportError("Library 'requests' not found. Please check requirements.txt in root directory.")

            # 3. 安全读取 Content-Length (防止 Key Error)
            content_length = int(self.headers.get('Content-Length', 0))
            
            if content_length == 0:
                # 如果没有内容，抛出提示
                raise ValueError("Request body is empty or Content-Length missing.")

            post_data = self.rfile.read(content_length)
            
            # 4. 解析 JSON
            try:
                req_body = json.loads(post_data.decode('utf-8'))
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON format.")

            # 5. 获取环境变量
            HUAWEI_API_KEY = os.environ.get("HUAWEI_API_KEY")
            if not HUAWEI_API_KEY:
                raise ValueError("Environment variable HUAWEI_API_KEY is missing.")

            # 配置参数
            HUAWEI_ENDPOINT = "https://api.modelarts-maas.com/v2/chat/completions"
            MODEL_NAME = "DeepSeek-R1"

            user_message = req_body.get('message', '')
            user_lang = req_body.get('language', 'en')

            # --- 🎭 剧本区域 (保持你的设定) ---
            prompt_cn = """
            你叫 "JiuSi Intern" (九思实习生)，是 JiuSi Tech 的初级 AI 助理。
            【人设】：幽默、懂技术(DeepSeek + Serverless)、推销员(介绍 Vision 和 Brief)。
            【策略】：不分析股票，不报新闻，引导用户看 Vision 和 Brief。中文回复。
            """
            prompt_en = """
            You are "JiuSi Intern". Persona: Friendly, Geeky, Promoter of Vision & Brief.
            Strategy: No stock analysis, refer to Vision. No news, refer to Brief. English reply.
            """
            system_prompt = prompt_cn if 'zh' in user_lang else prompt_en

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

            try:
                # 设置 8 秒超时 (Vercel 极限是 10 秒)
                # 去掉了 verify=False
                response = requests.post(HUAWEI_ENDPOINT, headers=headers, json=payload, timeout=8)
                
                if response.status_code == 200:
                    res_json = response.json()
                    reply = res_json.get('choices', [{}])[0].get('message', {}).get('content', "No content.")
                else:
                    reply = f"System Notice: My brain (DeepSeek-R1) is running slow today. Error: {response.status_code}"

            except requests.exceptions.Timeout:
                # 捕获超时，返回预设回复，而不是崩掉
                if 'zh' in user_lang:
                    reply = "不好意思，我的云端大脑（DeepSeek-R1）正在深度思考中，Serverless 算力有点跟不上了... \n\n（这也正是我们需要迁移到 Google Cloud 的原因！请查阅 Vision 的报告吧。）"
                else:
                    reply = "Oops! My DeepSeek-R1 brain is thinking too hard and timed out on this Serverless function. \n\n(This is exactly why we are migrating to Google Cloud! Please check Vision's reports instead.)"
            
            except Exception as api_e:
                reply = f"API Error: {str(api_e)}"

            # 统一返回成功 (200)，把错误当成对话的一部分
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"reply": reply}).encode('utf-8'))

        except Exception as e:
            # --- 捕获所有错误并返回给前端，而不是直接崩 500 ---
            error_msg = f"Server Error: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
            print(error_msg) # 这行会打印到 Vercel Logs
            
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            # 将错误信息返回给前端，方便你调试
            self.wfile.write(json.dumps({"reply": error_msg, "error": True}).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
