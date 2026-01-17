"""
测试智谱 API 是否正常工作
"""

import os
from dotenv import load_dotenv
from zhipuai import ZhipuAI

# 加载环境变量
load_dotenv()

api_key = os.getenv("ZHIPU_API_KEY")

if not api_key:
    print("[ERROR] ZHIPU_API_KEY not found in .env")
    exit(1)

print("=" * 60)
print("Zhipu GLM API Test")
print("=" * 60)
print()

print(f"API Key: {api_key[:20]}...")
print()

try:
    client = ZhipuAI(api_key=api_key)

    print("[Test 1] Testing basic connection...")
    response = client.chat.completions.create(
        model="glm-4-flash",
        messages=[
            {"role": "user", "content": "你好，请用一句话介绍你自己"}
        ],
        max_tokens=50
    )

    result = response.choices[0].message.content
    print(f"[OK] Response: {result[:100]}")
    print()

    print("[Test 2] Testing article generation...")
    response = client.chat.completions.create(
        model="glm-4-flash",
        messages=[
            {"role": "user", "content": "请写一段50字关于AI的介绍"}
        ]
    )

    result = response.choices[0].message.content
    print(f"[OK] Generated {len(result)} characters")
    print(f"Content preview: {result[:100]}...")
    print()

    print("=" * 60)
    print("[SUCCESS] All tests passed!")
    print("=" * 60)
    print()
    print("You can now use the web interface:")
    print("1. Run: python app.py")
    print("2. Open: http://localhost:5000")
    print("3. Select: Zhipu GLM")
    print("4. Click: Start generating")

except Exception as e:
    print(f"[ERROR] {e}")
    print()
    print("Possible issues:")
    print("1. API Key is invalid")
    print("2. Network connection problem")
    print("3. API service is down")
