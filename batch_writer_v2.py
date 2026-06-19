import csv
import sys
import os
from time import sleep
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")

def generate_with_requirements(product, style, audience, selling_point, tone, count):
    prompt = '为「' + product + '」写' + str(count) + '条' + style + '推广文案。'
    prompt += '目标人群：' + audience + '。'
    prompt += '核心卖点：' + selling_point + '。'
    prompt += '语气风格：' + tone + '。直接输出文案，不要序号。'
    try:
        resp = client.chat.completions.create(
            model="deepseek-v4-flash",
            messages=[
                {"role": "system", "content": "你是一个专业营销文案写手。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=800
        )
        return resp.choices[0].message.content
    except Exception as e:
        return '[ERROR] ' + str(e)

import_file = sys.argv[1] if len(sys.argv) > 1 else "projects.csv"
output_file = sys.argv[2] if len(sys.argv) > 2 else "results.csv"

projects = []
with open(import_file, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        projects.append({
            'name': row['项目名称'].strip(),
            'style': row.get('风格', '朋友圈').strip(),
            'audience': row.get('目标人群', '').strip(),
            'selling_point': row.get('核心卖点', '').strip(),
            'tone': row.get('语气', '').strip(),
            'count': int(row.get('文案条数', '3').strip())
        })

SEP = '=' * 50
print()
print(SEP)
print('📂 读取到 ' + str(len(projects)) + ' 个项目')
print(SEP)
print()

results = []
for i, p in enumerate(projects, 1):
    print('⏳ [' + str(i) + '/' + str(len(projects)) + '] ' + p['name'] + ' (' + p['style'] + ')...')
    print('   人群：' + p['audience'])
    print('   卖点：' + p['selling_point'])
    print('   语气：' + p['tone'])

    content = generate_with_requirements(
        p['name'], p['style'], p['audience'],
        p['selling_point'], p['tone'], p['count']
    )

    results.append([
        p['name'], p['style'], p['audience'],
        p['selling_point'], p['tone'], str(p['count']),
        content.replace(chr(10), ' | ')
    ])
    print('   ✅ 生成完成')
    print()
    sleep(0.5)

with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    writer.writerow(['项目名称', '风格', '目标人群', '核心卖点', '语气', '条数', '文案'])
    writer.writerows(results)

print(SEP)
print('✅ 全部完成！结果已保存到 ' + output_file)
print('用 Excel 打开看看效果吧！')
print(SEP)
