import os
import json
import datetime
import urllib.request
import urllib.parse

UA = "Mozilla/5.0"
NEWS_API = "https://api.tianapi.com/generalnews/index"  # 换成你实际用的天聚数行接口地址
TIAN_KEY = os.environ.get("TIAN_API_KEY")
SENDKEY = os.environ.get("SERVERCHAN_KEY")
SCT_API = f"https://sctapi.ftqq.com/{SENDKEY}.send"


def fetch_news():
    url = f"{NEWS_API}?key={TIAN_KEY}&num=15"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def build_markdown(data):
    today = datetime.date.today().isoformat()
    rows = (data.get("result") or {}).get("newslist", [])
    lines = [f"# 每日热点 · {today}", ""]
    n = 0
    for it in rows:
        n += 1
        title = it.get("title", "")
        url = it.get("url", "")
        src = it.get("source", "")
        desc = (it.get("description") or it.get("content") or "").strip()
        line = f"{n}. **{title}**"
        if src:
            line += f" — {src}"
        lines.append(line)
        if desc:
            lines.append(f"   {desc[:80]}")
        if url:
            lines.append(f"   [原文]({url})")
    md = "\n".join(lines)
    if len(md.encode("utf-8")) > 35000:        # Server酱 desp 上限保护
        md = md.encode("utf-8")[:35000].decode("utf-8", "ignore") + "\n\n…(已截断)"
    return md


def push(md):
    today = datetime.date.today().isoformat()
    params = urllib.parse.urlencode({
        "title": f"每日热点 {today}",   # title 不支持 Markdown，用纯文本
        "desp": md,                      # desp 支持 Markdown
    }).encode("utf-8")
    req = urllib.request.Request(
        SCT_API, data=params,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


if __name__ == "__main__":
    if not TIAN_KEY:
        raise SystemExit("缺少 TIAN_API_KEY")
    if not SENDKEY:
        raise SystemExit("缺少 SERVERCHAN_KEY")
    resp = push(build_markdown(fetch_news()))
    print(resp)   # 返回 {"code":0,...} 表示成功
