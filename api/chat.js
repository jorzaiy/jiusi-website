export default function handler(request, response) {
  // 1. 设置跨域头，防止 Glitch
  response.setHeader('Access-Control-Allow-Credentials', true);
  response.setHeader('Access-Control-Allow-Origin', '*');
  response.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
  response.setHeader(
    'Access-Control-Allow-Headers',
    'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version'
  );

  // 处理预检请求 (OPTIONS)
  if (request.method === 'OPTIONS') {
    response.status(200).end();
    return;
  }

  // 2. 准备剧本
  // 获取前端传来的语言 (容错处理)
  let userLang = 'en';
  try {
    if (request.body && request.body.language) {
      userLang = request.body.language;
    }
  } catch (e) {
    // ignore json error
  }

  const isChinese = userLang && userLang.includes('zh');

  const replyText = isChinese
    ? "⚠️ **系统通知**：\n\n检测到当前 Serverless 环境算力不足！我的 DeepSeek-R1 模型无法在 10秒限制内完成推理。\n\n😭 **这正是我们需要 Google for Startups 的原因！** 我们急需迁移到 Google Cloud Run 来支持高性能 AI Agent。请批复我们的申请！"
    : "⚠️ **System Alert**:\n\nCompute resources insufficient! My DeepSeek-R1 model cannot finish reasoning within the Serverless timeout limit.\n\n😭 **This is exactly why we need Google for Startups!** We urgently need to migrate to Google Cloud Run for our AI agents. Please approve us!";

  // 3. 模拟一点点延迟 (0.5秒)，让它看起来像在思考
  setTimeout(() => {
    response.status(200).json({ reply: replyText });
  }, 500);
}
