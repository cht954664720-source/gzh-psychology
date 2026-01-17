"""
检查 Gemini API 配额和账号状态
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

# 加载环境变量
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

print("=" * 60)
print("Gemini API Status Check")
print("=" * 60)
print()

# 检查 API Key
if not api_key:
    print("[ERROR] GEMINI_API_KEY not found")
    exit(1)

print(f"[OK] API Key loaded: {api_key[:15]}...")
print(f"[OK] API Key length: {len(api_key)} characters")
print()

# 尝试不同的 API 端点
print("Testing different approaches...")
print("-" * 60)

# 方式 1: 尝试列出模型（不消耗配额）
print("\n[Test 1] Listing models (should not consume quota)...")
try:
    genai.configure(api_key=api_key)
    models = list(genai.list_models())
    print(f"[OK] Found {len(models)} models")
    print("[INFO] API Key is valid and has access")
except Exception as e:
    print(f"[ERROR] {e}")

# 方式 2: 尝试使用免费模型（gemini-2.0-flash-lite）
print("\n[Test 2] Trying free model (gemini-2.0-flash-lite-001)...")
try:
    model = genai.GenerativeModel('models/gemini-2.0-flash-lite-001')
    response = model.generate_content("Hi")
    print(f"[OK] Response: {response.text[:100]}")
    print("[INFO] Free tier works!")
except Exception as e:
    print(f"[ERROR] {e}")

# 方式 3: 尝试 Gemini 3 Pro
print("\n[Test 3] Trying Gemini 3 Pro Preview...")
try:
    model = genai.GenerativeModel('models/gemini-3-pro-preview')
    response = model.generate_content("Hi")
    print(f"[OK] Response: {response.text[:100]}")
except Exception as e:
    print(f"[ERROR] {e}")

print()
print("=" * 60)
print("Check Complete")
print("=" * 60)
print()
print("If you see 429 errors:")
print("1. Visit: https://ai.dev/rate-limit")
print("2. Check if you have free quota remaining")
print("3. Verify your API key is for the correct project")
print("4. Consider creating a new API key")
