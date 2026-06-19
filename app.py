import streamlit as st
import csv
import io
import os
from time import sleep
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# ── 页面配置 ──
st.set_page_config(
    page_title="AI 文案工坊",
    page_icon="✍️",
    layout="wide"
)

# ── 自定义样式 ──
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0 1rem;
        background: linear-gradient(135deg, #2563eb, #7c3aed);
        border-radius: 16px;
        margin-bottom: 2rem;
        color: white;
    }
    .main-header h1 {
        font-size: 2.5rem;
        margin: 0;
        color: white;
    }
    .main-header p {
        font-size: 1rem;
        opacity: 0.9;
        margin-top: 0.5rem;
    }
    .pricing-badge {
        display: inline-block;
        background: #f0fdf4;
        color: #166534;
        border: 1px solid #86efac;
        border-radius: 999px;
        padding: 0.25rem 0.75rem;
        font-size: 0.75rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .success-box {
        background: #f0fdf4;
        border: 1px solid #86efac;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .stApp footer { display: none; }
    footer {
        text-align: center;
        color: #94a3b8;
        font-size: 0.8rem;
        padding: 2rem 0 1rem;
        border-top: 1px solid #e2e8f0;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# ── 页眉 ──
st.markdown("""
<div class="main-header">
    <h1>✍️ AI 文案工坊</h1>
    <p>输入产品名，一键生成朋友圈 · 小红书 · 抖音 · 淘宝文案</p>
</div>
""", unsafe_allow_html=True)

# ── 提示：在线演示版限制 ──
if "DEEPSEEK_API_KEY" not in os.environ:
    st.info("⚠️ 在线演示版 · 如需使用请部署时设置 DEEPSEEK_API_KEY 环境变量")

# ── API 客户端 ──
@st.cache_resource
def get_client():
    key = os.getenv("DEEPSEEK_API_KEY")
    if not key:
        return None
    return OpenAI(api_key=key, base_url="https://api.deepseek.com")


def generate(product, style, audience, selling_point, tone, count):
    client = get_client()
    if not client:
        return "[ERROR] API Key 未配置"

    prompt = f"为「{product}」写{count}条{style}推广文案。目标人群：{audience}。核心卖点：{selling_point}。语气风格：{tone}。直接输出文案，不要序号。"
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
        return f"[ERROR] {str(e)}"


# ── 侧边栏 ──
with st.sidebar:
    st.markdown("### ⚙️ 设置")
    default_style = st.selectbox(
        "文案风格",
        ["朋友圈", "小红书", "抖音脚本", "淘宝商品描述", "公众号", "微博", "知乎"],
        index=0
    )
    default_audience = st.text_input("目标人群（选填）", placeholder="如：25-40岁女性")
    default_selling = st.text_input("核心卖点（选填）", placeholder="如：真皮手工、耐用")
    default_tone = st.text_input("语气风格（选填）", placeholder="如：温暖治愈、简洁专业")
    default_count = st.number_input("生成条数", 1, 10, 3)

    st.divider()
    st.markdown("### 📤 批量导入")
    uploaded = st.file_uploader("上传 CSV 文件", type=["csv"])

    st.divider()
    st.markdown("### 💡 使用提示")
    st.caption("""
    **方式一：手动输入**
    下方输入产品名（每行一个）

    **方式二：上传 CSV**
    上传含"项目名称"列的 CSV

    **免费试写？**
    私信我，免费帮您写 3 条
    """)

# ── 主区域 ──
st.markdown("### 📋 产品列表")

if uploaded:
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
    st.success(f"✅ 已加载 {len(projects)} 个项目")
else:
    st.info("在下方输入产品名称，或左侧上传 CSV 文件")
    projects = []
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        names = st.text_area("项目名称（每行一个）", "手工皮具钱包\nAI写作助手\n手冲咖啡豆", height=150)
    with col2:
        styles = st.text_area("风格（每行一个，留空用默认）", "", height=150)
    with col3:
        audiences = st.text_area("目标人群", "", height=150)
    with col4:
        sellings = st.text_area("核心卖点", "", height=150)
    with col5:
        tones = st.text_area("语气", "", height=150)

    lines = names.strip().split("\n") if names.strip() else []
    s_lines = styles.strip().split("\n") if styles.strip() else []
    a_lines = audiences.strip().split("\n") if audiences.strip() else []
    sell_lines = sellings.strip().split("\n") if sellings.strip() else []
    t_lines = tones.strip().split("\n") if tones.strip() else []

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
    st.markdown(f"<small style='color: #64748b;'>共 {len(projects)} 个项目</small>", unsafe_allow_html=True)
    preview = [{"项目": p["name"], "风格": p["style"], "条数": p["count"]} for p in projects]
    st.dataframe(preview, use_container_width=True, hide_index=True)

# ── 生成 ──
col_a, col_b, col_c = st.columns([1, 2, 1])
with col_b:
    generate_btn = st.button("🚀 开始批量生成", type="primary", use_container_width=True, disabled=not projects)

if generate_btn:
    results = []
    progress = st.progress(0, text="准备中...")
    status = st.empty()

    for i, p in enumerate(projects):
        status.info(f"⏳ [{i+1}/{len(projects)}] 正在生成 {p['name']}...")
        content = generate(p["name"], p["style"], p["audience"],
                          p["selling_point"], p["tone"], p["count"])
        results.append([p["name"], p["style"], content.replace(chr(10), " | ")])
        progress.progress((i + 1) / len(projects), text=f"{i+1}/{len(projects)}")
        sleep(0.3)

    progress.empty()
    status.success("✅ 全部生成完成！")

    # 结果展示
    st.markdown("### 📄 生成结果")
    for r in results:
        with st.expander(f"✨ {r[0]}（{r[1]}）"):
            lines = r[2].split(" | ")
            for line in lines:
                if line.strip():
                    st.write("• " + line.strip())

    # 下载
    csv_output = io.StringIO()
    writer = csv.writer(csv_output)
    writer.writerow(["项目名称", "风格", "文案"])
    writer.writerows(results)
    st.download_button(
        label="📥 下载 CSV",
        data=csv_output.getvalue().encode("utf-8-sig"),
        file_name="ai_results.csv",
        mime="text/csv",
        use_container_width=True
    )

# ── 页脚 ──
st.markdown("""
<footer>
    Powered by DeepSeek API ·
    <a href="https://github.com/p9cjyggzvv-byte/ai-copywriter" target="_blank">GitHub</a> ·
    有问题？私信我
</footer>
""", unsafe_allow_html=True)
