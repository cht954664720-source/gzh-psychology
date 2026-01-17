"""
列出所有可用的 Gemini 模型
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

# 加载环境变量
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("[ERROR] GEMINI_API_KEY not found in .env")
    exit(1)

print(f"API Key loaded: {api_key[:10]}...\n")

# 配置 API
genai.configure(api_key=api_key)

# 列出所有模型
print("Available Gemini models:")
print("=" * 60)

try:
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"- {model.name}")
            print(f"  Display Name: {model.display_name}")
            print(f"  Description: {model.description}")
            print()

except Exception as e:
    print(f"Error listing models: {e}")
    print("\nTrying alternative method...")

    # 尝试直接使用常见模型名称
    common_models = [
        "gemini-2.0-flash-exp",
        "gemini-2.0-flash-thinking-exp",
        "gemini-1.5-pro-latest",
        "gemini-1.5-flash-latest",
        "gemini-exp-1206",
    ]

    print("\nTrying common model names:")
    for model_name in common_models:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Hi")
            print(f"[OK] {model_name} - {response.text[:50]}...")
        except Exception as e2:
            print(f"[FAIL] {model_name} - {str(e2)[:50]}...")
