
# Daily Arxiv Report for Astro.HE
- This tool is forked and modified from [PiggyDreamer95/arxiv_gal_DailyRep_Gen_ai](https://github.com/PiggyDreamer95/arxiv_gal_DailyRep_Gen_ai)
- Many thanks to the original author: Bocheng Zhu 朱柏铖 (bochengzhu@outlook.com)
- License: MIT

# Purpose
- This AI-based tool aims to scan, filter, categorize, summarize daily Arxiv papers majoring in **High-Energy astrophysics**, and generate an easy-to-read report for researchers interested in this regime.
- **Timing**: the tool extracts the exact daily updated papers matching the time window of offical arxiv website.
- **Categorizing**: Indexing all the papers and categorizing into sub-topics to help you locate your interested ones.
- **Labeling**: Label all the papers on 'observation', 'simulation' and 'theory'.
- **Summarizing**: 2-3 sentences to address the core scientific outcome for each paper.

# New features:
Compared to the original version, this modified version can:
- Focus on **high-energy astrophysics**
- **Filter** out those papers of pure cosmology and particle astrophysics. (With no offense\_(:з」∠)\_)
- **Wavelength**: For observation papers, label them with wavelength (X-ray/UV/gamma-ray/...) they use and also the targets they observe.

# Warning
- **This tool is powered by AI LLM. The generated contents are not guarenteed to be accurate or complete. Users are solely responsible for independently verification. The developers shall not be liable for any loss arising from any failure to perform manual check.**

# Content
- `HE_Sync_Report_2026-03-16.html`: an example of daily report on astro.HE papers for 2026-3-16.
- `arxiv_daily_for_HE_noAPI.py`: the script based on OpenAI API (or similar LLM)
- `arxiv_daily_for_HE_gemini_noAPI.py`: the script based on Gemini API, with counts on tokens

# Usage
## Preparation
- python >=3.9
- use `pip` to install these packages:
    - arxiv
    - datetime
    - openai
    - pytz
    - `pip install -q -U google-genai`
- Prepare your own LLM API keys

## Running
- `python arxiv_daily_for_HE_noAPI.py`

# Ongoing Tasks
- Keep polishing the prompt
- Connecting to Wechat platform API for automatically push.
- ..... 

