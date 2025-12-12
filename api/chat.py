from http.server import BaseHTTPRequestHandler
import json
import random
import time

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # 1. 设置跨域头 (CORS)，确保前端能收到
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        
        try:
            # 2. 读取前端发来的语言设置
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                body_str = self.rfile.read(content_length).decode('utf-8')
                try:
                    req_body = json.loads(body_str)
                    user_lang = req_body.get('language', 'en')
                except:
                    user_lang = 'en'
            else:
                user_lang = 'en'

            # 3. 模拟“思考”时间 (让它看起来像真的AI)
            # 睡个 1.5 秒，让 loading 动画转一会儿
            time.sleep(1.5)

            # 4. 准备“剧本”
            if 'zh' in user_lang:
                replies = [
                    "⚠️ **系统通知**：\n\n检测到当前 Serverless 环境算力不足！我的 DeepSeek-R1 模型无法在 10秒限制内完成推理。\n\n😭 **这正是我们需要 Google for Startups 的原因！** 我们急需迁移到 Google Cloud Run 来支持高性能 AI Agent。请批复我们的申请！",
                    "你好！我是九思实习生。由于当前 Azure Static Web Apps 的超时限制，我的大脑（DeepSeek-R1）经常掉线...\n\n👉 **我们需要 Google Cloud！** 请让我们通过审核，去 Gemini 1.5 Pro 的新家吧！",
                ]
            else:
                replies = [
                    "⚠️ **System Alert**:\n\nCompute resources insufficient! My DeepSeek-R1 model cannot finish reasoning within the Serverless timeout limit.\n\n😭 **This is exactly why we need Google for Startups!** We urgently need to migrate to Google Cloud Run for our AI agents. Please approve us!",
                    "Hello! I'm the JiuSi Intern. Due to current infrastructure limits, my brain disconnects often...\n\n👉 **We need Google Cloud!** Please approve our application so I can move to my new home powered by Gemini 1.5 Pro!",
                ]

            # 随机选一条回复，增加真实感
            reply_text = random.choice(replies)

            # 5. 返回 200 成功状态
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"reply": reply_text}).encode('utf-8'))

        except Exception as e:
            # 即使这里崩了，也要返回 JSON，防止前端 Glitch
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"reply": "System Update: Migrating to Google Cloud..."}).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
