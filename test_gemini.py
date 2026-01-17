"""
测试 Gemini API 连接状态
检查是配额用完还是暂时限速
"""

import os
import time
from dotenv import load_dotenv
import google.generativeai as genai

def test_gemini():
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("错误：未找到 GEMINI_API_KEY")
        return False

    print(f"API Key: {api_key[:10]}...{api_key[-4:]}")
    print("-" * 50)

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('models/gemini-3-pro-preview')

    # 测试 1: 简单请求
    print("\n[测试 1/3] 发送简单请求...")
    try:
        response = model.generate_content("请用一句话介绍你自己")
        print(f"✓ 成功！响应: {response.text[:100]}...")
    except Exception as e:
        print(f"✗ 失败：{e}")

        # 分析错误类型
        error_str = str(e).lower()
        if "429" in error_str:
            if "quota" in error_str:
                print("\n📊 诊断：配额已用完（需要等待重置或升级）")
            else:
                print("\n⏱️  诊断：暂时限速（可能是请求过快，稍后重试）")
        return False

    # 测试 2: 检查模型列表
    print("\n[测试 2/3] 检查可用模型...")
    try:
        models = genai.list_models()
        gemini_models = [m for m in models if "gemini" in m.name.lower()]
        print(f"✓ 找到 {len(gemini_models)} 个 Gemini 模型")
        for m in gemini_models[:5]:
            print(f"  - {m.name}")
    except Exception as e:
        print(f"✗ 失败：{e}")

    # 测试 3: 连续请求测试限速
    print("\n[测试 3/3] 连续请求测试（检查限流）...")
    for i in range(3):
        try:
            print(f"  请求 {i+1}/3...", end=" ")
            response = model.generate_content(f"测试请求 {i+1}，请回复数字{i+1}")
            print(f"✓")
            time.sleep(1)  # 间隔1秒
        except Exception as e:
            print(f"✗ {e}")
            break

    print("\n" + "=" * 50)
    print("测试完成！")
    return True

if __name__ == "__main__":
    test_gemini()
