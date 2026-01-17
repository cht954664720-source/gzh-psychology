"""
检查 Google AI 账号状态和配额信息
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

print("=" * 60)
print("Google AI Account Status")
print("=" * 60)
print()

# 检查 API Key
print(f"API Key: {api_key[:20]}...")
print(f"Key Length: {len(api_key)} characters")
print()

genai.configure(api_key=api_key)

# 尝试获取账户信息
print("Checking account information...")
print("-" * 60)

try:
    # 列出模型
    models = list(genai.list_models())
    print(f"[OK] Account is valid")
    print(f"[INFO] Total models available: {len(models)}")
    print()

    # 尝试最简单的请求
    print("Testing basic request...")
    try:
        model = genai.GenerativeModel('models/gemini-2.0-flash-lite-001')
        response = model.generate_content("Hi")
        print(f"[OK] Request successful!")
        print(f"[INFO] Response: {response.text[:100]}")
    except Exception as e:
        error = str(e)
        print(f"[ERROR] Request failed")

        if "429" in error:
            print()
            print("=" * 60)
            print("QUOTA EXCEEDED")
            print("=" * 60)
            print()
            print("This means:")
            print("1. Your Google AI account has exceeded the free tier limit")
            print("2. Free tier limits: 15 requests/minute, 1500 requests/day")
            print("3. You need to either:")
            print("   - Wait for quota to reset (usually daily)")
            print("   - Enable billing on your Google Cloud project")
            print("   - Use a different Google account")
            print()
            print("To enable billing (for paid usage):")
            print("1. Visit: https://aistudio.google.com/app/pricing")
            print("2. Link your Google Cloud project with billing enabled")
            print("3. Or use Google AI Studio with your account")
            print()
            print("To check current quota:")
            print("https://ai.dev/rate-limit")
            print("=" * 60)

except Exception as e:
    print(f"[ERROR] Account check failed: {e}")

print()
