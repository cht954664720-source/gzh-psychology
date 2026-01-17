"""
测试环境变量是否正确加载
"""

import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 检查 API Key
api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    print(f"[OK] GEMINI_API_KEY loaded")
    print(f"  Key length: {len(api_key)} chars")
    print(f"  Key prefix: {api_key[:10]}...")
else:
    print("[ERROR] GEMINI_API_KEY not found")
    print("\nPlease check .env file exists and contains GEMINI_API_KEY")

# 测试 Gemini 连接
if api_key:
    print("\nTesting Gemini connection...")
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Hello")
        print(f"[OK] Gemini connected!")
        print(f"  Response: {response.text[:100]}...")
    except Exception as e:
        print(f"[ERROR] Gemini connection failed: {e}")
