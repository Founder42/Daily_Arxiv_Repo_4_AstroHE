## arXiv 每日同步版日报生成器 --- 作者：朱柏铖 (author:Bocheng Zhu bochengzhu@outlook.com)
## Github: https://github.com/PiggyDreamer95/arxiv_gal_DailyRep_Gen_ai
## Modified by Fangzheng Shi
## Modify log:
## - Changed to be based on Gemini API.


## Task list
## - Control token budget of thinking.

import arxiv
import datetime
#from openai import OpenAI
from google import genai
from google.genai import types
from datetime import timedelta
import pytz
# ==========================================
MY_API_KEY = "Your Gemini API here~"
#MY_BASE_URL = "https://api.deepseek.com/v1"
MY_MODEL = "gemini-3-flash-preview" # Or other model you like
client = genai.Client(api_key=MY_API_KEY)
# ==========================================
def get_arxiv_sync_window():
    """精确计算 arXiv 今日公布批次的提交时间窗口"""
    tz_et = pytz.timezone('US/Eastern')
    now_et = datetime.datetime.now(tz_et)
    
    # arXiv 更新规则：周四的 New 列表来自周三 14:00 前的 24 小时提交
    # 周一的 New 列表来自上周五 14:00 前的提交
    weekday = now_et.weekday() 
    if weekday == 0: # Monday
        days_back = 3
    elif weekday in [5, 6]: # Weekend
        days_back = 0
    else:
        days_back = 1
        
    # 窗口结束点：昨天 14:00 ET
    end_time = now_et.replace(hour=14, minute=0, second=0, microsecond=0) - timedelta(days=1)
    # 窗口起始点：再往前推 24h (或周一对应的 72h)
    start_time = end_time - timedelta(days=days_back)
    
    return start_time, end_time

def fetch_arxiv_papers_HE():
    start_t, end_t = get_arxiv_sync_window()
    print(f"Synchronizing arXiv Reports (Submission Time Window: {start_t.strftime('%m-%d %H:%M')} -> {end_t.strftime('%m-%d %H:%M')} ET)")

    arxiv_client = arxiv.Client()
    search = arxiv.Search(query="cat:astro-ph.HE", max_results=60, sort_by=arxiv.SortCriterion.SubmittedDate)
    
    papers = []
    for r in arxiv_client.results(search):
        pub_et = r.published.astimezone(pytz.timezone('US/Eastern'))
        if start_t <= pub_et < end_t:
            papers.append({
                "title": r.title,
                "authors": ", ".join([a.name for a in r.authors]),
                "summary": r.summary,
                "url": r.entry_id
            })
    
    print(f"Synchronization successful! Fetched {len(papers)} papers (should match the official New list).")
    return papers

######## Multiple topics ##########

def generate_report_gemini(papers):
    if not papers: return "<p>No updates today. Happy Happy Happy~</p>"
    
    input_text = ""
    for i, p in enumerate(papers):
        input_text += f"[{i+1}] Title: {p['title']}\nAuthors: {p['authors']}\nAbstract: {p['summary']}\nURL: {p['url']}\n\n"

    prompt = f"""
    # Role
    You are an elite Science Editor and Senior Astrophysicist specializing in High-Energy Astrophysics, with world-class expertise in X-ray observations of Active Galactic Nuclei (AGN), SMBH outflows, and AGN feedback. 

    # Task
    Process the following {len(papers)} arXiv papers and generate a professional daily briefing in HTML format. Focus exclusively on the user's core interests: X-ray astronomy, Black Hole outflow, AGN feedback and high-resolution X-ray spectroscopy.

    # Output Requirements (Strict HTML)
    - Only returns content within the <body> tag.
    - Use ONLY <body> internal tags (<h3>, <ul>, <li>, <p>, <strong>, <span>).
    - Prohibit all Markdown syntax (no ##, no **).
    - Language: Professional Academic English.

    # Logical Sections
    
    I. Index Section
    Filter and Categorize papers into the following specific sub-fields. List the paper indices [n] for each. 
    Note: A paper can belong to multiple categories.
    Catagories:
    - Black hole accretion physics: (e.g. accretion disk, corona, disk wind))
    - AGN Outflows and Feedback: (e.g. supermassive black holes,UFOs, warm absorbers, molecular outflows, feedback on ISM)
    - Galaxy evolution: (e.g. star formation, quenching, galaxy-SMBH co-evolution)
    - stellar mass black hole: (e.g. X-ray binaries, microquasars)
    - Transients and variability: (e.g. TDEs, changing-look AGN, QPEs)
    - Clusters and Intra-cluster medium: (e.g. cooling flows, AGN heating, warm-hot intergalactic medium)
    Filter rule: Only include papers that fall into at least one of the above categories. Discard unrelated particle physics or pure cosmology papers.

    II Details Section
    For every paper identified in the Index Section, provide details in the following strict format:

    [n] Paper Title (in English)
    Authors: Full names (Highlight any world-renowned experts in the field with <strong style="color:#d35400;">Name ★(Famous Scholar)</strong>)
    Link: URL to the paper
    Methodology: [Observation / Simulation / Theory / Methods] (...)
        (If catorizied as [Observation], then further specify:
        - Energy band: e.g. X-ray, UV, Optical, Radio, Gamma-ray, Infrared
        - Key Targets/Sample: list the source or the sample name.)
    Core Results: Provide 2-3 concise, high-impact sentences.
        - MANDATORY: Extract specific physical parameters where available
        - Preserve all special symbols (like α, β, σ, M☉).
        - Avoid filler phrases like "This paper presents...". Start directly with the discovery (e.g., "The XRISM/Resolve spectrum reveals a multi-phase outflow with velocity components at...").

    # Input papers to Process:
    {input_text}
    """

    print("Gemini is Generating minutes ...")
    try:
        response = client.models.generate_content(
            model=MY_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_level="medium")
            ),
        )
        print("Thoughts tokens:",response.usage_metadata.thoughts_token_count)
        print("Output tokens:",response.usage_metadata.candidates_token_count)
        return response.text
    except Exception as e:
        return f"Error: {e}"
    
#def generate_report_Xread(papers):
    ### Require modifying .....
    # I want the link to the paper appera too
    #if not papers: return "<p>No updates today.</p>"
    
    #input_text = ""
    #for i, p in enumerate(papers):
    #    input_text += f"[{i+1}] Title: {p['title']}\nAuthors: {p['authors']}\nAbstract: {p['summary']}\nURL: {p['url']}\n\n"

    #prompt = f"""
    #你是一名专业的天文学公众号主编且资深天文学家。请处理以下 {len(papers)} 篇论文，严格按以下格式输出语言为英文的HTML：

    #一、领域归类 (Index Section)
    #按领域（如：Active galactic nuclei, Black holes, Dark matter, Intracluster medium, Jets, Neutrino astronomy, particle astrophysics, plasma physics, Relativistic binary stars, Seyfert galaxies, Transient source, Warm-hot intergalactic medium）分类，在每个类别后列出对应的论文编号。
    #注意：同一个论文可能涉及多个领域，请在所有相关领域下列出其编号。
    #格式示例：领域名称：[1], [5], [12]
    #用户关注领域：Active galactic nuclei, Black holes, Seyfert galaxies, Intracluster medium, Warm-hot intergalactic medium, Transient source
    #只需列出属于【用户关注领域】的论文，其他领域的论文不需要列出。

    #二、论文条目 (Details Section)
    #按编号顺序排列所有属于【用户关注领域】的论文。
    #每篇格式：
    #[编号] 论文英文标题
    #作者：姓名全称（若有天文模拟、观测、理论、方法等领域的著名学者，请用 <strong style="color:#d35400;">姓名 ★(Famous Scholar)</strong>）
    #研究方法：[需判定为 Observation / Simulation / Theory / Technology 之一]。判定标准：若文章核心是对于观测数据的分析，请标为 [Observation]；若核心是算法改进或软件评测或统计学讨论，请标为 [Methods]。若核心是进行了数值模拟，请标为 [Simulation]；若核心是提出理论分析或模型构建，请标为 [Theory]。
    #研究波段：对于判定为[Observation]，请进一步判定其主要研究波段（如：X-ray, Optical, Radio, Gamma-ray, Multi-wavelength等）。如果论文涉及多个波段，请列出所有相关波段。
    #核心物理结果：严禁使用‘本文研究了...’这种废话。请直接描述物理发现，例如：‘发现星系旋转曲线在 R > 20kpc 处依然平坦，暗示暗物质晕比例高于预期。’，使用 2-3 句准确、简洁的英文学术表达。保留希腊字母(α, β, σ)和太阳符号(M☉)，保留天体名称。

    #要求：
    #- 严禁 Markdown 符号（如 ##, **），必须使用纯 HTML 标签 (<h3>, <ul>, <li>, <p>, <strong>)。
    #- 只返回 <body> 内部内容。

    #待处理论文：
    #{input_text}
    #"""

    #print("Deepseek is deeply seeking ...")
    #try:
    #    response = client.chat.completions.create(
    #        model=MY_MODEL,
    #        messages=[{"role": "user", "content": prompt}]
    #    )
    #    return response.choices[0].message.content
    #except Exception as e:
    #    return f"Error: {e}"
    
#################
# Translation from English to Chinese with super prompts here .... (Under construction)
def translate_report_to_chinese(english_report):
    if not english_report: return "<p>今日无事。巧妇难为无米之炊。</p>"


##################

def save_html_English(content, lenpapers):
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    html_layout = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: -apple-system, sans-serif; line-height: 1.6; color: #333; max-width: 900px; margin: auto; padding: 20px; }}
        .header {{ background: #004085; color: white; padding: 20px; border-radius: 10px; text-align: center; }}
        .index-box {{ background: #f8f9fa; border: 1px solid #dee2e6; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .paper-item {{ border-bottom: 1px solid #eee; padding: 15px 0; }}
        .method-tag {{ color: #28a745; font-weight: bold; font-size: 0.9em; }}
        h3 {{ color: #004085; border-left: 5px solid #004085; padding-left: 10px; margin-top: 40px; }}
    </style>
</head>
<body>
    <div class="header">
        <h2 style="margin:0;">Daily Report for High Energy Astrophysics</h2>
        <p>{date_str} | Today's update: {lenpapers} papers</p>
    </div>
    {content.replace('```html', '').replace('```', '')}
</body>
</html>"""
    
    filename = f"HE_Sync_Report_{date_str}.html"
    with open(filename, "w", encoding="utf-8-sig") as f:
        f.write(html_layout)
    print(f"Daily Report Generated: {filename}")



def save_html(content, lenpapers):
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    html_layout = f"""<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: -apple-system, sans-serif; line-height: 1.6; color: #333; max-width: 900px; margin: auto; padding: 20px; }}
        .header {{ background: #004085; color: white; padding: 20px; border-radius: 10px; text-align: center; }}
        .index-box {{ background: #f8f9fa; border: 1px solid #dee2e6; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .paper-item {{ border-bottom: 1px solid #eee; padding: 15px 0; }}
        .method-tag {{ color: #28a745; font-weight: bold; font-size: 0.9em; }}
        h3 {{ color: #004085; border-left: 5px solid #004085; padding-left: 10px; margin-top: 40px; }}
    </style>
</head>
<body>
    <div class="header">
        <h2 style="margin:0;">🌌 星系物理与动力学日报</h2>
        <p>{date_str} | 今日同步更新 {lenpapers} 篇</p>
    </div>
    {content.replace('```html', '').replace('```', '')}
</body>
</html>"""
    
    filename = f"HE_Sync_Report_{date_str}_Gemini.html"
    with open(filename, "w", encoding="utf-8-sig") as f:
        f.write(html_layout)
    print(f"Daily Report Generated: {filename}")

if __name__ == "__main__":
    # Ensure pytz is installed: !pip install pytz
    data = fetch_arxiv_papers_HE()
    report_eng = generate_report_gemini(data)
    save_html_English(report_eng, len(data))
    # translate to Chinese
    #.....on going 
    # Output Chinese version
    #......on going
    