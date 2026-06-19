"""
更多 API 集成
============
DeepSeek 之外的 AI API 调用示例
"""

import os
import requests

def text_to_speech(text, voice="default"):
    """文字转语音（使用免费 TTS API）"""
    try:
        resp = requests.post(
            "https://api.openspeech.com/tts",
            json={"text": text, "voice": voice},
            timeout=30
        )
        if resp.status_code == 200:
            return resp.content
        return None
    except Exception as e:
        print(f"TTS 错误：{e}")
        return None


def search_image(query):
    """搜索图片（示例：使用 Unsplash 免费 API）"""
    try:
        resp = requests.get(
            f"https://api.unsplash.com/search/photos?query={query}&per_page=3",
            headers={"Authorization": f"Client_ID {os.getenv('UNSPLASH_KEY', 'demo')}"},
            timeout=10
        )
        if resp.status_code == 200:
            urls = [r["urls"]["small"] for r in resp.json()["results"]]
            return urls
        return []
    except Exception as e:
        print(f"图片搜索错误：{e}")
        return []


def extract_url_content(url):
    """提取网页内容"""
    try:
        resp = requests.get(url, timeout=10, headers={
            "User-Agent": "Mozilla/5.0 (compatible; AIBot/1.0)"
        })
        if resp.status_code == 200:
            return resp.text[:2000]
        return None
    except Exception as e:
        print(f"网页提取错误：{e}")
        return None


if __name__ == "__main__":
    print("📡 更多 API 集成示例")
    print("=" * 40)
    print("本模块演示如何调用 DeepSeek 之外的 API")
    print()
    print("支持的 API 类型：")
    print("  • TTS（文字转语音）")
    print("  • 图片搜索")
    print("  • 网页内容提取")
    print()
    print("使用前需要申请相应 API Key 并设为环境变量")
