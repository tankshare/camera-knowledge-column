#!/usr/bin/env python3
"""
摄像机硬件科普系列 - Markdown 转 HTML 工具
- 批量将系列 Markdown 文章转换为可浏览的 HTML 页面
- 自动按已发布期次计算进度与导航
- 自动生成站点首页（始终指向最新一期）
"""

import os
import re
import shutil
import markdown

# 40 期系列完整规划
SERIES_PLAN = {
    1: {"title": "传感器全解析", "category": "成像基础", "module": "模块一", "status": "completed"},
    2: {"title": "像素与分辨率的真相", "category": "成像基础", "module": "模块一", "status": "completed"},
    3: {"title": "光学变焦vs数字变焦vsAI超分辨率变焦", "category": "成像基础", "module": "模块一", "status": "completed"},
    4: {"title": "帧率的秘密", "category": "成像基础", "module": "模块一", "status": "completed"},
    5: {"title": "光圈与景深", "category": "成像基础", "module": "模块一", "status": "completed"},
    6: {"title": "快门与曝光", "category": "成像基础", "module": "模块一", "status": "completed"},
    7: {"title": "低噪声与高信噪比", "category": "ISP与图像处理", "module": "模块二", "status": "completed"},
    8: {"title": "ISP图像信号处理全解析", "category": "ISP与图像处理", "module": "模块二", "status": "completed"},
    9: {"title": "图像效果评判五大参数", "category": "ISP与图像处理", "module": "模块二", "status": "completed"},
    10: {"title": "图像参数调节实战", "category": "ISP与图像处理", "module": "模块二", "status": "completed"},
    11: {"title": "背光补偿与宽动态", "category": "ISP与图像处理", "module": "模块二", "status": "completed"},
    12: {"title": "自动对焦技术", "category": "ISP与图像处理", "module": "模块二", "status": "completed"},
    13: {"title": "云台与PTZ控制", "category": "云台与电机控制", "module": "模块三", "status": "completed"},
    14: {"title": "预置位与遥控器", "category": "云台与电机控制", "module": "模块三", "status": "completed"},
    15: {"title": "AI人体追踪技术", "category": "云台与电机控制", "module": "模块三", "status": "completed"},
    16: {"title": "视频接口演进史", "category": "接口与传输", "module": "模块四", "status": "completed"},
    17: {"title": "USB2.0 vs USB3.0", "category": "接口与传输", "module": "模块四", "status": "completed"},
    18: {"title": "网络接口与PoE供电", "category": "接口与传输", "module": "模块四", "status": "completed"},
    19: {"title": "无线传输与Wi-Fi摄像机", "category": "接口与传输", "module": "模块四", "status": "pending"},
    20: {"title": "网络传输协议实战", "category": "接口与传输", "module": "模块四", "status": "pending"},
    21: {"title": "视频压缩原理", "category": "编解码与存储", "module": "模块五", "status": "pending"},
    22: {"title": "视频会议协议", "category": "编解码与存储", "module": "模块五", "status": "pending"},
    23: {"title": "摄像机存储方案", "category": "编解码与存储", "module": "模块五", "status": "pending"},
    24: {"title": "音频接口与传输", "category": "音频技术", "module": "模块六", "status": "pending"},
    25: {"title": "麦克风阵列与波束成形", "category": "音频技术", "module": "模块六", "status": "pending"},
    26: {"title": "回声消除与AI降噪", "category": "音频技术", "module": "模块六", "status": "pending"},
    27: {"title": "主控芯片概览", "category": "主控芯片深度解析", "module": "模块七", "status": "pending"},
    28: {"title": "Rockchip RK3588/RK3576", "category": "主控芯片深度解析", "module": "模块七", "status": "pending"},
    29: {"title": "SigmaStar SSU9383/9386", "category": "主控芯片深度解析", "module": "模块七", "status": "pending"},
    30: {"title": "国科GK7608/GK7606", "category": "主控芯片深度解析", "module": "模块七", "status": "pending"},
    31: {"title": "为旌Visinex芯片", "category": "主控芯片深度解析", "module": "模块七", "status": "pending"},
    32: {"title": "镜头厂商生态", "category": "镜头与供应链", "module": "模块八", "status": "pending"},
    33: {"title": "镜头参数深度解析", "category": "镜头与供应链", "module": "模块八", "status": "pending"},
    34: {"title": "镜头选型实战", "category": "镜头与供应链", "module": "模块八", "status": "pending"},
    35: {"title": "UT680一体化智能终端", "category": "智能终端与教育应用", "module": "模块九", "status": "pending"},
    36: {"title": "教育录播解决方案", "category": "智能终端与教育应用", "module": "模块九", "status": "pending"},
    37: {"title": "双模态产品解析", "category": "智能终端与教育应用", "module": "模块九", "status": "pending"},
    38: {"title": "AK030视频会议控制键盘", "category": "控制设备与系统方案", "module": "模块十", "status": "pending"},
    39: {"title": "会议摄像机选型指南", "category": "控制设备与系统方案", "module": "模块十", "status": "pending"},
    40: {"title": "视频会议系统方案", "category": "控制设备与系统方案", "module": "模块十", "status": "pending"},
}

MODULES = {
    "模块一": {"name": "成像基础", "range": (1, 6)},
    "模块二": {"name": "ISP与图像处理", "range": (7, 12)},
    "模块三": {"name": "云台与电机控制", "range": (13, 15)},
    "模块四": {"name": "接口与传输", "range": (16, 20)},
    "模块五": {"name": "编解码与存储", "range": (21, 23)},
    "模块六": {"name": "音频技术", "range": (24, 26)},
    "模块七": {"name": "主控芯片深度解析", "range": (27, 31)},
    "模块八": {"name": "镜头与供应链", "range": (32, 34)},
    "模块九": {"name": "智能终端与教育应用", "range": (35, 37)},
    "模块十": {"name": "控制设备与系统方案", "range": (38, 40)},
}


def collect_markdown_files(workspace_dir):
    """查找所有系列 Markdown 文件，并按期数去重。"""
    md_files_by_issue = {}

    for file_name in os.listdir(workspace_dir):
        if not (file_name.startswith('摄像机硬件科普_') and file_name.endswith('.md')):
            continue

        match = re.search(r'第(\d+)期', file_name)
        if not match:
            continue

        issue_num = int(match.group(1))
        if issue_num not in SERIES_PLAN:
            continue

        current_path = os.path.join(workspace_dir, file_name)
        preferred_name = f"摄像机硬件科普_第{issue_num:03d}期_{SERIES_PLAN[issue_num]['title']}.md"
        existing_path = md_files_by_issue.get(issue_num)

        if existing_path is None or os.path.basename(current_path) == preferred_name:
            md_files_by_issue[issue_num] = current_path

    return {issue: md_files_by_issue[issue] for issue in sorted(md_files_by_issue)}


def sync_series_progress(published_issues):
    """根据已发布期次动态更新系列与模块状态。"""
    published_set = set(published_issues)

    for issue_num, issue_info in SERIES_PLAN.items():
        issue_info['status'] = 'completed' if issue_num in published_set else 'pending'

    module_progress = {}
    for module_name, module_info in MODULES.items():
        start, end = module_info['range']
        completed = sum(1 for issue_num in range(start, end + 1) if issue_num in published_set)
        module_progress[module_name] = completed

    return module_progress


def generate_sidebar(current_issue, published_issues, module_progress):
    """生成左侧导航栏 HTML。"""
    published_set = set(published_issues)
    html = '<div class="sidebar-content">\n'

    for module_name, module_info in MODULES.items():
        start, end = module_info['range']
        total = end - start + 1
        completed = module_progress[module_name]

        if completed == total:
            status_class = ''
            status_text = f'已完成 {completed}/{total}'
        elif completed > 0:
            status_class = 'progress'
            status_text = f'进行中 {completed}/{total}'
        else:
            status_class = 'pending'
            status_text = f'待开始 0/{total}'

        html += '                <div class="module-section">\n'
        html += '                    <div class="module-header">\n'
        html += f'                        <span>{module_name} · {module_info["name"]}</span>\n'
        html += f'                        <span class="module-status {status_class}">{status_text}</span>\n'
        html += '                    </div>\n'
        html += '                    <ul class="article-list">\n'

        for issue_num in range(start, end + 1):
            issue_info = SERIES_PLAN[issue_num]
            filename = f"摄像机硬件科普_第{issue_num:03d}期_{issue_info['title']}.html"

            if issue_num == current_issue:
                link_class = 'active'
            elif issue_num in published_set:
                link_class = 'completed'
            else:
                link_class = ''

            href = filename if issue_num in published_set else '#'

            html += '                        <li class="article-item">\n'
            html += f'                            <a href="{href}" class="article-link {link_class}">\n'
            html += f'                                <span class="article-number">{issue_num:03d}</span>\n'
            html += f'                                <span class="article-title-short">{issue_info["title"]}</span>\n'
            html += '                            </a>\n'
            html += '                        </li>\n'

        html += '                    </ul>\n'
        html += '                </div>\n'

    html += '            </div>'
    return html


def md_to_html(md_content):
    """将 Markdown 转换为 HTML。"""
    extensions = [
        'markdown.extensions.fenced_code',
        'markdown.extensions.tables',
        'markdown.extensions.toc',
        'markdown.extensions.nl2br',
    ]

    md = markdown.Markdown(extensions=extensions)
    return md.convert(md_content)


def extract_subtitle(md_content):
    """从文章标题中提取副标题。"""
    for line in md_content.splitlines():
        if line.startswith('# ') and '第' in line and '期' in line:
            parts = line.replace('# ', '').split('——', 1)
            if len(parts) > 1:
                return parts[1].strip()
            break
    return ''


def get_adjacent_issues(current_issue, published_issues):
    """仅在已发布期次中查找上一篇/下一篇。"""
    try:
        index = published_issues.index(current_issue)
    except ValueError:
        return None, None

    prev_issue = published_issues[index - 1] if index > 0 else None
    next_issue = published_issues[index + 1] if index < len(published_issues) - 1 else None
    return prev_issue, next_issue


def inject_sidebar(template, sidebar_html):
    """用动态导航替换模板中的静态侧边栏。"""
    return re.sub(
        r'(<aside class="sidebar">\s*)(.*?)(\s*</aside>)',
        lambda match: f"{match.group(1)}{sidebar_html}{match.group(3)}",
        template,
        count=1,
        flags=re.S,
    )


def convert_article(md_file_path, output_dir, published_issues, module_progress):
    """转换单篇文章。"""
    filename = os.path.basename(md_file_path)
    match = re.search(r'第(\d+)期', filename)
    if not match:
        print(f'无法解析期数: {filename}')
        return None

    issue_num = int(match.group(1))
    issue_info = SERIES_PLAN.get(issue_num)
    if not issue_info:
        print(f'未知的期数: {issue_num}')
        return None

    with open(md_file_path, 'r', encoding='utf-8') as file:
        md_content = file.read()

    title = issue_info['title']
    subtitle = extract_subtitle(md_content)
    article_html = md_to_html(md_content)
    sidebar_html = generate_sidebar(issue_num, published_issues, module_progress)

    progress_percent = (issue_num / 40) * 100
    prev_issue, next_issue = get_adjacent_issues(issue_num, published_issues)

    prev_link = f"摄像机硬件科普_第{prev_issue:03d}期_{SERIES_PLAN[prev_issue]['title']}.html" if prev_issue else '#'
    next_link = f"摄像机硬件科普_第{next_issue:03d}期_{SERIES_PLAN[next_issue]['title']}.html" if next_issue else '#'
    prev_title = SERIES_PLAN[prev_issue]['title'] if prev_issue else '无'
    next_title = SERIES_PLAN[next_issue]['title'] if next_issue else '敬请期待'
    prev_disabled = '' if prev_issue else 'disabled'
    next_disabled = '' if next_issue else 'disabled'

    template_path = os.path.join(os.path.dirname(__file__), 'index.html')
    with open(template_path, 'r', encoding='utf-8') as file:
        template = file.read()

    html_output = template
    html_output = html_output.replace('{{ISSUE_NUMBER}}', f'{issue_num:03d}')
    html_output = html_output.replace('{{CURRENT_ISSUE}}', str(issue_num))
    html_output = html_output.replace('{{PROGRESS_PERCENT}}', f'{progress_percent:.1f}')
    html_output = html_output.replace('{{CATEGORY}}', issue_info['category'])
    html_output = html_output.replace('{{ARTICLE_TITLE}}', title)
    html_output = html_output.replace('{{ARTICLE_SUBTITLE}}', subtitle)
    html_output = html_output.replace('{{SERIES_NAME}}', '摄像机硬件科普系列')
    html_output = html_output.replace('{{DIFFICULTY}}', '无需电路基础')
    html_output = html_output.replace('{{ARTICLE_CONTENT}}', article_html)
    html_output = html_output.replace('{{PREV_LINK}}', prev_link)
    html_output = html_output.replace('{{NEXT_LINK}}', next_link)
    html_output = html_output.replace('{{PREV_TITLE}}', prev_title)
    html_output = html_output.replace('{{NEXT_TITLE}}', next_title)
    html_output = html_output.replace('{{PREV_DISABLED}}', prev_disabled)
    html_output = html_output.replace('{{NEXT_DISABLED}}', next_disabled)
    html_output = inject_sidebar(html_output, sidebar_html)

    output_filename = f'摄像机硬件科普_第{issue_num:03d}期_{title}.html'
    output_path = os.path.join(output_dir, output_filename)

    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(html_output)

    print(f'已生成: {output_filename}')
    return output_path


def create_site_entry(output_dir, latest_issue):
    """生成站点入口文件，让根链接始终打开最新一期。"""
    latest_title = SERIES_PLAN[latest_issue]['title']
    latest_filename = f'摄像机硬件科普_第{latest_issue:03d}期_{latest_title}.html'
    latest_path = os.path.join(output_dir, latest_filename)
    index_path = os.path.join(output_dir, 'index.html')
    nojekyll_path = os.path.join(output_dir, '.nojekyll')

    shutil.copyfile(latest_path, index_path)
    with open(nojekyll_path, 'w', encoding='utf-8') as file:
        file.write('')

    print(f'站点首页已更新为最新一期: {latest_filename}')


def batch_convert(workspace_dir):
    """批量转换所有文章。"""
    md_files_by_issue = collect_markdown_files(workspace_dir)
    published_issues = sorted(md_files_by_issue)

    if not published_issues:
        print('未找到可转换的 Markdown 文件。')
        return []

    module_progress = sync_series_progress(published_issues)

    output_dir = os.path.join(workspace_dir, 'html_output')
    os.makedirs(output_dir, exist_ok=True)

    generated_files = []
    for issue_num in published_issues:
        md_file = md_files_by_issue[issue_num]
        result = convert_article(md_file, output_dir, published_issues, module_progress)
        if result:
            generated_files.append(result)

    create_site_entry(output_dir, published_issues[-1])

    print(f'\n共生成 {len(generated_files)} 个文章页面')
    print(f'输出目录: {output_dir}')
    return generated_files


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        workspace = sys.argv[1]
    else:
        workspace = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    batch_convert(workspace)
