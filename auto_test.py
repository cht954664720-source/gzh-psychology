"""
自动测试不同模型，找到可用的
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=api_key)

# 按优先级测试不同模型
models_to_try = [
    ("Gemini 3 Pro Preview", "models/gemini-3-pro-preview"),
    ("Gemini 2.5 Pro", "models/gemini-2.5-pro"),
    ("Gemini 2.0 Flash", "models/gemini-2.0-flash-001"),
    ("Gemini 2.0 Flash Lite", "models/gemini-2.0-flash-lite-001"),
    ("Gemini Pro Latest", "models/gemini-pro-latest"),
]

print("=" * 60)
print("Testing Available Models")
print("=" * 60)
print()

working_models = []

for name, model_id in models_to_try:
    print(f"Testing {name} ({model_id})...", end=" ")

    try:
        model = genai.GenerativeModel(model_id)
        response = model.generate_content("Say OK")
        result = response.text.strip()

        print(f"[OK] - Response: {result[:50]}")
        working_models.append((name, model_id))

    except Exception as e:
        error_msg = str(e)

        if "429" in error_msg:
            print(f"[QUOTA EXCEEDED]")
        elif "404" in error_msg:
            print(f"[NOT FOUND]")
        else:
            print(f"[ERROR: {error_msg[:50]}]")

print()
print("=" * 60)

if working_models:
    print("Working Models Found:")
    print("-" * 60)
    for name, model_id in working_models:
        print(f"[OK] {name}")
        print(f"     ID: {model_id}")
        print()
else:
    print("No working models found.")
    print()
    print("Recommendations:")
    print("1. Create a new API Key at: https://aistudio.google.com/apikey")
    print("2. Check quota at: https://ai.dev/rate-limit")
    print("3. Wait for quota to reset (usually daily)")

print("=" * 60)
