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
MY_API_KEY = "Your Gemini API Key~"
#MY_BASE_URL = "https://api.deepseek.com/v1"
MY_MODEL = "gemini-3-flash-preview"
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
    Authors: Full names (Highlight any world-renowned experts in the field with <strong style="color:#f95b17;">Name ★(Famous Scholar)</strong>)
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
    
def generate_report_gemini_backup(papers):
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
    For every paper identified in the Index Section, provide details in the following strict format (put each paper detail into  <div class="paper-item"></div>):

    [n] Paper Title (in English)
    Authors: Full names (Highlight any world-renowned experts in the field with <strong style="color:#f95b17;">Name ★(Famous Scholar)</strong>)
    Link: URL to the paper (include the url with <a href="URL"> and </a>)
    Methodology: [Observation / Simulation / Theory / Methods] (...) (Put the Methodology line into <span class="method-tag"></span>)
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
        body {{ font-family: -apple-system, sans-serif; line-height: 1.6; color: #e4e4e4; max-width: 900px; margin: auto; padding: 20px; background-color: #312e2c; }}
        .header {{ background: #219fc0; color: #e4e4e4; padding: 20px; border-radius: 10px; text-align: center; }}
        .index-box {{ background: #484949; border: 1px solid #2b2b2b; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .paper-item {{ border-bottom: 1px solid #312e2c; padding: 15px 0; }}
        .method-tag {{ background: #73243a; color: #e4e4e4; font-size: 0.9em; }}
        h3 {{ color: #219fc0; border-left: 5px solid #219fc0; padding-left: 10px; margin-top: 40px; }}
        a {{color: #219fc0;}}
        p {{font-weight: bold;}}
    </style>
</head>
<body>
    <div class="header">
        <h2 style="margin:0;">Daily Report for High Energy Astrophysics</h2>
        <p>{date_str} | Today's update: {lenpapers} papers</p>
    </div>
    <section class="index-box">
    {content.replace('```html', '').replace('```', '')}
    </section>
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
    