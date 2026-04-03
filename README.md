# 摄像机硬件科普系列

这是一个可持续更新的知识专栏仓库，源文件为 Markdown，发布形态为 GitHub Pages 静态站点。

## 现在已经具备的能力

- Markdown 源稿持续积累
- `template/md_to_html.py` 自动批量转换 HTML
- 站点首页自动指向**最新一期**
- 推送到 `main` 后，GitHub Actions 自动部署到 GitHub Pages

## 仓库结构

```text
.
├─ template/                 # HTML 模板与构建脚本
├─ .github/workflows/        # GitHub Pages 自动部署工作流
├─ 摄像机硬件科普_第XXX期_*.md  # 系列源稿
├─ requirements.txt          # 构建依赖
└─ html_output/              # 本地构建产物（已加入 .gitignore）
```

## 首次上线步骤

### 1）在 GitHub 创建空仓库
建议仓库名：`camera-knowledge-column`

### 2）将本地项目关联到远程仓库
在项目根目录执行：

```bash
git init -b main
git remote add origin https://github.com/<你的用户名>/camera-knowledge-column.git
git add .
git commit -m "init: 摄像机硬件科普系列站点"
git push -u origin main
```

> 如果本地已经是 Git 仓库，只需要补 `git remote add origin ...` 和首次 push。

### 3）开启 GitHub Pages
进入 GitHub 仓库：

- `Settings`
- `Pages`
- 在 `Build and deployment` 中选择 **GitHub Actions**

之后每次推送到 `main`，都会自动：

1. 安装 Python 依赖
2. 运行 `python template/md_to_html.py .`
3. 生成 `html_output/`
4. 发布到 GitHub Pages

## 站点访问方式

部署成功后，站点通常会是：

```text
https://<你的用户名>.github.io/<仓库名>/
```

这个根链接会始终打开**最新一期**，团队成员只记住这一个链接就够了。

## 后续更新流程

每新增一期，保持当前自动化流程即可：

1. 检查已发布文章
2. 生成下一期 Markdown
3. 本地转换 HTML
4. 推送到 GitHub
5. GitHub Pages 自动更新线上站点

## 推荐的下一步

等你把 GitHub 仓库创建好之后，我可以继续帮你做两件事：

1. 关联远程仓库并完成首次推送
2. 把每日自动任务补成“生成后自动提交并推送”，实现真正的持续同步
