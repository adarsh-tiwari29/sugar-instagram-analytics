<div align="center">

# Instagram Performance Analytics – Sugar Cosmetics

**Analysing 50,000 Instagram posts to find out what actually drives engagement and follower growth.**

[![Live Dashboard](https://img.shields.io/badge/Live%20Dashboard-Open%20App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://sugar-instagram-analytics.streamlit.app/)

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=flat-square&logo=plotly&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)

</div>

---

## Live demo

👉 **[sugar-instagram-analytics.streamlit.app](https://sugar-instagram-analytics.streamlit.app/)**

## About the project

This is a data analyst project done for **Labmentrix**. It covers **50,000 Sugar Cosmetics Instagram posts** from 19 Apr 2024 to 19 Apr 2025. The data is cleaned and feature-engineered in Python, then shown in an interactive **Streamlit** dashboard with cross-filtering (Streamlit was approved in place of Tableau). The project also includes a 10-slide stakeholder presentation and a written insights report with strategic recommendations.

## Headline numbers

| Metric | Value |
|---|---|
| Posts analysed | **50,000** |
| Impressions | **1.28B** |
| Reach | **987M** |
| Likes | **147.7M** |
| Comments | **18.5M** |
| Avg. engagement rate | **18.54%** |

## Key insights

- **Likes make up 80.7% of engagement.** Saves (4.8%) and shares (4.4%) are the high-intent actions that matter most to the algorithm, and they are the weakest part of the mix.
- **The profile converts well, but few people reach it.** Only 3% of reached users visit the profile, yet **29.9% of those visitors follow**. The bottleneck is getting people to the profile.
- **Reels and Stories lead** on engagement rate. The best combination is **Story + Tutorial (18.80%)**.
- **Wednesday, Friday and Saturday** are the strongest days. Sunday is the weakest.
- **Posts with 2 hashtags do best.** #VeganBeauty and #BoldLooks are the top-performing tags.
- **Paid posts don't beat organic posts** on engagement rate or reach.
- **Content quality is the real lever.** Every category difference is under 0.4 pp and most aren't statistically significant, so timing, format and hashtags on their own won't move engagement.

Full findings and recommendations: [`reports/insights_summary.md`](reports/insights_summary.md)

## Dashboard features

| # | Section | What it shows |
|---|---|---|
| 🏠 | **Dashboard** | All key charts on one page. Click a bar (Post Type / Weekday / Hashtag) to cross-filter everything |
| 1 | **KPI Overview** | Posts, likes, comments, reach, impressions, shares, saves, follows, avg ER |
| 2 | **Monthly Trend** | Posts per month and monthly engagement rate |
| 3 | **Top 10 by Likes** | Bar chart and table of the most-liked posts |
| 4 | **Top 10 by ER** | Highest-ER posts, a "hidden gem" flag, and a reach vs ER scatter |
| 5 | **Post Type Comparison** | Avg likes, comments, saves and shares, plus ER by format |
| 6 | **Day of Week** | ER by weekday and a Post Type × Weekday heatmap |
| 7 | **Engagement Funnel** | Impressions → Reach → Likes → Comments → Shares → Saves, plus the follower funnel |
| 8 | **Hashtag Analysis** | ER by hashtag, usage, hashtag count and best combinations |
| 10 | **Recommendations** | Strategy, content ideas and data gaps |
| 📈 | **Campaigns & Growth** | Campaign type, paid vs organic, audience emotion, cumulative follower growth |

**Sidebar filters:** Post Type · Month · Hashtag · Campaign Type · Engagement Source · CSV download of the filtered data

## Project structure

```
Sugar Instagram Analytics/
├── app.py                          # Streamlit dashboard (entry point)
├── requirements.txt                # Python dependencies
├── .streamlit/
│   └── config.toml                 # Theme + server config
├── scripts/
│   └── data_prep.py                # Data cleaning + feature engineering
├── data/
│   ├── raw/
│   │   └── sugar_cosmetics_instagram_data.csv
│   └── processed/
│       └── sugar_instagram_preprocessed.xlsx   # Cleaned data + hashtag table + data dictionary
├── reports/
│   └── insights_summary.md         # Business summary & strategic recommendations
└── presentation/
    ├── Sugar_Cosmetics_Instagram_Insights.pptx  # 10-slide stakeholder deck
    └── Sugar_Cosmetics_Instagram_Insights.pdf
```

## Run locally

```bash
# 1. Clone the repo
git clone https://github.com/adarsh-tiwari29/sugar-instagram-analytics.git
cd sugar-instagram-analytics

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Mac / Linux

# 3. Install dependencies and run
pip install -r requirements.txt
streamlit run app.py
```

The dashboard opens at `http://localhost:8501`.

> Optional: `python scripts/data_prep.py` regenerates the cleaned files in `data/processed/`. The app doesn't need this step because it prepares the data itself from the raw CSV.

## Key definitions

- **Total Engagement** = Likes + Comments + Shares + Saves
- **Engagement Rate (%)** = Total Engagement ÷ Reach × 100 (per post; the KPI is the average across posts)
- **Post Label** = Post ID | Post Type | Campaign Type | Date (used in place of a caption, since the dataset has none)

## Data notes

- 50,000 rows × 14 columns, with no missing values or duplicates. Reach ≤ Impressions on every row.
- The post types are **Image, Reel, Story and Video**. There is no Carousel type.
- Hashtags are stored comma-separated (1–3 per post) and are split into one row per hashtag for analysis.
- **Gaps:** the dataset has no captions, posting hour, follower count over time or ad spend. The report suggests how to capture each one.

## Tech stack

**Python** · **Pandas** · **NumPy** · **Plotly** · **Streamlit** · **OpenPyXL** · deployed on **Streamlit Community Cloud**

## Author

**Adarsh Shrikant Tiwari**
Data Analyst Intern @ Labmentrix
GitHub: [@adarsh-tiwari29](https://github.com/adarsh-tiwari29)

---

<div align="center">
⭐ If you found this project useful, consider giving it a star!
</div>
