import csv
import os
from time import sleep
from src.utils import ask_llm


def generate_copy(product, style="朋友圈", audience="", selling_point="", tone="", count=3):
    prompt = (
        f'为「{product}」写{count}条{style}推广文案。\n'
        f'目标人群：{audience}\n'
        f'核心卖点：{selling_point}\n'
        f'语气风格：{tone}\n'
        f'直接输出文案，不要序号。'
    )
    return ask_llm(
        [{"role": "user", "content": prompt}],
        system="你是一个专业营销文案写手。",
        temp=0.8,
        max_tokens=800
    )


def batch_generate(input_file, output_file, style="朋友圈", audience="", selling_point="", tone="", count=3):
    projects = []
    with open(input_file, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            projects.append({
                "name": row.get("项目名称", "").strip(),
                "style": row.get("风格", style).strip(),
                "audience": row.get("目标人群", audience).strip(),
                "selling_point": row.get("核心卖点", selling_point).strip(),
                "tone": row.get("语气", tone).strip(),
                "count": int(row.get("文案条数", str(count)).strip())
            })

    results = []
    print(f"\n📂 读取到 {len(projects)} 个项目\n")
    for i, p in enumerate(projects, 1):
        print(f"⏳ [{i}/{len(projects)}] {p['name']}...")
        content = generate_copy(
            p["name"], p["style"], p["audience"],
            p["selling_point"], p["tone"], p["count"]
        )
        results.append([p["name"], p["style"], content.replace(chr(10), " | ")])
        print("   ✅ 完成")
        sleep(0.3)

    with open(output_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["项目", "风格", "文案"])
        writer.writerows(results)
    print(f"\n✅ 结果已保存到 {output_file}")
    return results


def content_matrix(original, platforms):
    PLATFORMS = {
        "朋友圈": "简短亲切，不超过150字",
        "小红书": "种草风格，带emoji和话题标签，500-800字",
        "抖音脚本": "分镜脚本：画面、旁白、字幕",
        "公众号": "长文风格，有标题小标题，1500字",
        "微博": "140字以内，带话题标签",
        "知乎": "专业详细，1000-1500字",
    }
    results = {}
    for p in platforms:
        p = p.strip()
        if p not in PLATFORMS:
            continue
        prompt = f"改编为【{p}】风格。原文：{original}\n要求：{PLATFORMS[p]}\n只输出改编后文案。"
        r = ask_llm(
            [{"role": "user", "content": prompt}],
            system="内容运营专家",
            temp=0.7,
            max_tokens=2000
        )
        results[p] = r
        print(f"✅ {p} 完成")
        sleep(0.3)
    return results


def ask_document(filepath, question):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    prompt = (
        f"基于以下文档回答问题：\n---\n{content[:3000]}\n---\n"
        f"问题：{question}\n文档没提到就说'文档中没有提到'。"
    )
    return ask_llm(
        [{"role": "user", "content": prompt}],
        system="文档分析师",
        temp=0.3,
        max_tokens=1000
    )
