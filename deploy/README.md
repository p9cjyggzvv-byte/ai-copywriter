# 部署指南

## 方式一：Railway（最简单，免费额度）
1. 注册 https://railway.app
2. 连接 GitHub 仓库
3. 选择 Deploy from GitHub repo
4. 设置环境变量 DEEPSEEK_API_KEY
5. 部署完成

## 方式二：阿里云/腾讯云服务器
1. 买一台服务器（最低配 1核2G 约 50元/月）
2. 安装 Python + Git
3. git clone 你的仓库
4. pip install -r requirements.txt
5. streamlit run app.py --server.address=0.0.0.0
6. 用 nginx 配域名

## 环境变量
在部署平台设置：
DEEPSEEK_API_KEY=你的key
