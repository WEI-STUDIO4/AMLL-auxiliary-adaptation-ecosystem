#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Your Music Statistics for amll-music-monitor
日志格式：[时间] 作者 - 歌名 (第 N 次)
仅统计“第 1 次”去重，用最后一次“第 M 次”作为真实累计
"""
import re
import datetime as dt
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from jinja2 import Template

# ---------- 配置 ----------
PLAYBACK_LOG = Path(r"C:\Users\Administrator\Desktop\AMLL auxiliary adaptation ecosystem\amll-music-monitor\music_playback.log")
STATS_DIR    = Path("stats")
TOP_N        = 10
RECENT_DAYS  = 30
# 中文字体
for font in fm.findSystemFonts(fontpaths=None, fontext='ttf'):
    if "SimHei" in font or "PingFang" in font or "NotoSansCJK" in font:
        plt.rcParams["font.family"] = fm.FontProperties(fname=font).get_name()
        break
else:
    plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["axes.unicode_minus"] = False

# ---------- 解析日志（含作者） ----------
LOG_RE = re.compile(r"\[(?P<time>.+?)\] (?P<artist>.+?) - (?P<title>.+?) \(第 (?P<count>\d+) 次\)")
raw_lines = PLAYBACK_LOG.read_text(encoding="utf-8").splitlines()

# 1. 同一首歌最后一次出现的“第 M 次”
last_count = {}
for line in raw_lines:
    m = LOG_RE.search(line)
    if not m:
        continue
    key = f"{m['artist']} - {m['title']}"  # 用“作者 - 歌名”做 key
    last_count[key] = int(m["count"])      # 最后留下的就是最大次数

# 2. 只取“第 1 次”作为去重记录，但用 M 作为权重
records = []
for line in raw_lines:
    m = LOG_RE.search(line)
    if not m:
        continue
    if int(m["count"]) != 1:      # 只拿第 1 次
        continue
    t      = dt.datetime.strptime(m["time"], "%Y-%m-%d %H:%M:%S")
    artist = m["artist"].strip()
    title  = m["title"].strip()
    key    = f"{artist} - {title}"
    real_count = last_count[key]  # 真实累计
    records.append({"artist": artist, "title": title,
                    "key": key, "count": real_count, "dt": t})

if not records:
    print("❌ 未解析到任何播放记录，请确认日志格式正确！")
    exit(1)

# ---------- 指标（按真实累计） ----------
total_plays = sum(r["count"] for r in records)
first_day   = min(r["dt"] for r in records).date()
last_day    = max(r["dt"] for r in records).date()
valid_days  = len({r["dt"].date() for r in records})
total_duration = total_plays * 240 / 3600   # 估算小时

# ---------- TOP 榜单（按真实累计） ----------
artist_cnt = Counter()   # 歌手维度
song_cnt   = Counter()   # 歌曲维度
for r in records:
    artist_cnt[r["artist"]] += r["count"]
    song_cnt[r["key"]]      += r["count"]
top_artists = artist_cnt.most_common(TOP_N)
top_songs   = song_cnt.most_common(TOP_N)

# ---------- 每日/24h 分布（权重=真实累计） ----------
date_end   = last_day
date_start = date_end - dt.timedelta(days=RECENT_DAYS - 1)
daily = Counter()
for r in records:
    if date_start <= r["dt"].date() <= date_end:
        daily[r["dt"].date()] += r["count"]
daily_x = [date_start + dt.timedelta(days=i) for i in range(RECENT_DAYS)]
daily_y = [daily[d] for d in daily_x]

hour_cnt = Counter()
for r in records:
    hour_cnt[r["dt"].hour] += r["count"]
hour_x = list(range(24))
hour_y = [hour_cnt[h] for h in hour_x]

# ---------- 绘图 ----------
STATS_DIR.mkdir(exist_ok=True)

# 1. 每日趋势
plt.figure(figsize=(12, 4))
plt.plot(daily_x, daily_y, marker="o", linewidth=2)
plt.title(f"最近 {RECENT_DAYS} 天播放趋势（真实累计）")
plt.xlabel("日期"); plt.ylabel("播放次数")
plt.tight_layout()
plt.savefig(STATS_DIR / "trend.png", dpi=160)
plt.close()

# 2. 24h 分布
plt.figure(figsize=(6, 4))
plt.bar(hour_x, hour_y, color="skyblue")
plt.title("24 小时播放分布（真实累计）")
plt.xlabel("小时"); plt.ylabel("次数")
plt.tight_layout()
plt.savefig(STATS_DIR / "hour.png", dpi=160)
plt.close()

# 3. 歌手词云
try:
    from wordcloud import WordCloud
    wc = WordCloud(width=800, height=400, background_color="white",
                   font_path=plt.rcParams["font.family"])
    wc.generate_from_frequencies(artist_cnt)
    wc.to_file(STATS_DIR / "wordcloud.png")
    wordcloud_ok = True
except Exception:
    wordcloud_ok = False

# ---------- HTML ----------
TMPL = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>Your Music Statistics</title>
  <style>
    body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,"Noto Sans",sans-serif,"Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol","Noto Color Emoji";margin:0;background:#fafafa;color:#333}
    .container{max-width:900px;margin:auto;padding:30px 20px}
    h1{text-align:center;margin-bottom:10px}
    .sub{text-align:center;color:#666;margin-bottom:40px}
    .card{background:#fff;border-radius:8px;padding:20px;margin-bottom:25px;box-shadow:0 2px 6px rgba(0,0,0,.05)}
    .card h2{margin-top:0}
    .grid{display:flex;gap:20px;flex-wrap:wrap}
    .grid>div{flex:1 1 400px}
    ol{margin:0;padding-left:20px}
    ol li{margin:4px 0}
    img{max-width:100%}
  </style>
</head>
<body>
<div class="container">
  <h1>🎵 Your Music Statistics</h1>
  <p class="sub">数据来源：amll-music-monitor &nbsp;&nbsp; 生成时间：{{gen_time}}</p>

  <div class="card">
    <h2>📊 总体概览（真实累计）</h2>
    <ul>
      <li>累计播放 <strong>{{total_plays}}</strong> 次</li>
      <li>有效收听天数 <strong>{{valid_days}}</strong> 天</li>
      <li>估算累计收听 <strong>{{"%0.1f"|format(total_duration)}}</strong> 小时</li>
      <li>记录时间跨度 {{first_day}} 至 {{last_day}}</li>
    </ul>
  </div>

  <div class="grid">
    <div class="card">
      <h2>🎤 最爱歌手 TOP10（真实累计）</h2>
      <ol>
        {% for a,c in top_artists %}
          <li>{{a}} <span style="color:#999">({{c}} 次)</span></li>
        {% endfor %}
      </ol>
    </div>
    <div class="card">
      <h2>🎶 最爱歌曲 TOP10（真实累计）</h2>
      <ol>
        {% for s,c in top_songs %}
          <li>{{s}} <span style="color:#999">({{c}} 次)</span></li>
        {% endfor %}
      </ol>
    </div>
  </div>

  <div class="card">
    <h2>📈 最近 {{recent_days}} 天播放趋势</h2>
    <img src="trend.png" alt="trend">
  </div>

  <div class="card">
    <h2>🕑 24 小时播放分布</h2>
    <img src="hour.png" alt="hour">
  </div>

  {% if wordcloud_ok %}
  <div class="card">
    <h2>☁️ 歌手词云</h2>
    <img src="wordcloud.png" alt="wordcloud">
  </div>
  {% endif %}
</div>
</body>
</html>"""

html = Template(TMPL).render(
    gen_time      = dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
    total_plays   = total_plays,
    valid_days    = valid_days,
    total_duration= total_duration,
    first_day     = first_day,
    last_day      = last_day,
    top_artists   = top_artists,
    top_songs     = top_songs,
    recent_days   = RECENT_DAYS,
    wordcloud_ok  = wordcloud_ok
)

(STATS_DIR / "index.html").write_text(html, encoding="utf-8")
print(f"✅ 统计报告已生成：{STATS_DIR.resolve() / 'index.html'}")