import streamlit as st
import csv
import io
import os
from time import sleep
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="AI 文案批量生成工具",
    page_icon="✍️",
    layout="wide"
)

# 标题
st.title("✍️ AI 文案批量生成工具")
st.markdown("上传你的产品列表，一键生成朋友圈/小红书/淘宝文案")


@st.cache_resource
def get_client():
    return OpenAI(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com"
    )


def generate(product, style, audience, selling_point, tone, count):
    prompt = f"""为「{product}」写{count}条{style}推广文案。
目标人群：{audience}
核心卖点：{selling_point}
语气风格：{tone}
直接输出文案，不要序号。"""
    try:
        client = get_client()
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
        return f"[ERROR] {str(e)}"


# ── 侧边栏设置 ──
with st.sidebar:
    st.header("⚙️ 全局设置")
    default_style = st.selectbox("默认文案风格", ["朋友圈", "小红书", "抖音脚本", "淘宝商品描述", "公众号"])
    default_audience = st.text_input("默认目标人群", "")
    default_selling = st.text_input("默认核心卖点", "")
    default_tone = st.text_input("默认语气", "")
    default_count = st.number_input("默认生成条数", 1, 10, 3)

    st.divider()
    st.markdown("**📤 上传 CSV**")
    uploaded = st.file_uploader("上传产品列表", type=["csv"])

# ── 输入区域 ──
st.subheader("📋 产品列表")

if uploaded:
    # 从上传的 CSV 读取
    content = uploaded.getvalue().decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(content))
    projects = []
    for row in reader:
        projects.append({
            "name": row.get("项目名称", "").strip(),
            "style": row.get("风格", default_style).strip() or default_style,
            "audience": row.get("目标人群", default_audience).strip() or default_audience,
            "selling_point": row.get("核心卖点", default_selling).strip() or default_selling,
            "tone": row.get("语气", default_tone).strip() or default_tone,
            "count": int(row.get("文案条数", default_count).strip() or default_count)
        })
    st.success(f"已加载 {len(projects)} 个项目")
else:
    # 手动输入
    st.info("👆 左侧可以上传 CSV 文件，或者在下方手动输入")
    projects = []
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        names = st.text_area("项目名称（每行一个）", "手工皮具钱包
AI写作助手
手冲咖啡豆订阅", height=150)
    with col2:
        styles = st.text_area("风格（每行一个）", "", height=150, placeholder="留空则使用默认风格")
    with col3:
        audiences = st.text_area("目标人群（每行一个）", "", height=150)
    with col4:
        sellings = st.text_area("核心卖点（每行一个）", "", height=150)
    with col5:
        tones = st.text_area("语气（每行一个）", "", height=150)

    lines = names.strip().split("
") if names.strip() else []
    s_lines = styles.strip().split("
") if styles.strip() else []
    a_lines = audiences.strip().split("
") if audiences.strip() else []
    sell_lines = sellings.strip().split("
") if sellings.strip() else []
    t_lines = tones.strip().split("
") if tones.strip() else []

    for i, name in enumerate(lines):
        projects.append({
            "name": name.strip(),
            "style": s_lines[i].strip() if i < len(s_lines) else default_style,
            "audience": a_lines[i].strip() if i < len(a_lines) else default_audience,
            "selling_point": sell_lines[i].strip() if i < len(sell_lines) else default_selling,
            "tone": t_lines[i].strip() if i < len(t_lines) else default_tone,
            "count": default_count
        })

# ── 预览 ──
if projects:
    st.write(f"共 {len(projects)} 个项目，预览：")
    preview = []
    for p in projects:
        preview.append({"项目": p["name"], "风格": p["style"], "目标人群": p["audience"], "卖点": p["selling_point"], "语气": p["tone"], "条数": p["count"]})
    st.dataframe(preview, use_container_width=True)

# ── 生成按钮 ──
if st.button("🚀 开始批量生成", type="primary", disabled=not projects):
    results = []
    progress = st.progress(0)
    status = st.empty()

    for i, p in enumerate(projects):
        status.info(f"⏳ [{i+1}/{len(projects)}] 正在生成 {p['name']}...")
        content = generate(p["name"], p["style"], p["audience"],
                          p["selling_point"], p["tone"], p["count"])
        results.append([p["name"], p["style"], p["audience"],
                       p["selling_point"], p["tone"], str(p["count"]),
                       content.replace(chr(10), " | ")])
        progress.progress((i + 1) / len(projects))
        sleep(0.3)

    status.success("✅ 生成完成！")

    # 显示结果
    st.subheader("📄 生成结果")
    for r in results:
        with st.expander(f"{r[0]}（{r[1]}）"):
            lines = r[6].split(" | ")
            for line in lines:
                if line.strip():
                    st.write("• " + line.strip())
            st.caption(f"目标人群：{r[2]}  |  卖点：{r[3]}  |  语气：{r[4]}")

    # 下载按钮
    csv_output = io.StringIO()
    writer = csv.writer(csv_output)
    writer.writerow(["项目名称", "风格", "目标人群", "核心卖点", "语气", "条数", "文案"])
    writer.writerows(results)
    st.download_button(
        label="📥 下载 CSV 文件",
        data=csv_output.getvalue().encode("utf-8-sig"),
        file_name="ai_results.csv",
        mime="text/csv"
    )

# ── 底部说明 ──
st.divider()
st.caption("Powered by DeepSeek API  |  有问题？在 Claude 对话中问我")
