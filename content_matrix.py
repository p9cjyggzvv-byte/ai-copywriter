import sys
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")

PLATFORMS = {
    "朋友圈": "简短、亲切、有温度，像是发给朋友看的，不超过150字",
    "小红书": "种草风格，带emoji，分段清晰，有话题标签，500-800字",
    "抖音脚本": "写出分镜脚本：画面、旁白、字幕、特效，适合15-60秒短视频",
    "公众号": "长文风格，有标题、引言、小标题分段，1500-2000字",
    "微博": "140字以内，简洁有力，带话题标签",
    "知乎": "专业详细，有数据/案例支撑，适合深度阅读，1000-1500字",
    "淘宝详情": "突出卖点和用户痛点，带场景描述，500-800字",
}

def adapt_content(original, target_platform, platform_rule):
    prompt = '请将以下内容改编为【' + target_platform + '】风格的文案。原文：' + original + ' 改编要求：' + platform_rule + ' 只输出改编后的文案。'
    try:
        resp = client.chat.completions.create(
            model="deepseek-v4-flash",
            messages=[
                {"role": "system", "content": "你是一个专业的内容运营专家，擅长为不同平台改写文案。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        return resp.choices[0].message.content
    except Exception as e:
        return '[ERROR] ' + str(e)

if len(sys.argv) < 2:
    print('用法: python content_matrix.py 原文内容 [平台1,平台2,...]')
    print('示例: 把一段文案改成朋友圈+小红书+抖音脚本')
    sys.exit(1)

original = sys.argv[1]
platforms = sys.argv[2].split(',') if len(sys.argv) > 2 else ['朋友圈', '小红书', '抖音脚本']

SEP = '=' * 50
DASH = '-' * 40
print()
print(SEP)
print('AI 内容矩阵 - 一文多发')
print(SEP)
print('原文: ' + (original[:60] + '...' if len(original) > 60 else original))
print('适配平台: ' + ', '.join(platforms))
print(SEP)
print()

for platform in platforms:
    platform = platform.strip()
    if platform not in PLATFORMS:
        print('跳过未知平台: ' + platform)
        continue
    print('生成【' + platform + '】版本...')
    result = adapt_content(original, platform, PLATFORMS[platform])
    print()
    print(DASH)
    print('📱 ' + platform)
    print(DASH)
    print(result)
    print(DASH)
    print()

print('全部完成!')
