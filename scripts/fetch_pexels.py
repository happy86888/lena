"""
Miss Lena · Pexels Trends Fetcher
==================================
從 Pexels API 抓婚紗、禮服、小禮服相關圖片，依風格分類。

可以單獨跑：
    PEXELS_KEY=你的key python scripts/fetch_pexels.py

也會被 fetch_all.py 引用，跟 Unsplash 結果合併。
"""

import os
import sys
import time
import json
from datetime import datetime, timezone
from pathlib import Path
import urllib.request
import urllib.error
from urllib.parse import urlencode

API_BASE = "https://api.pexels.com/v1"
PER_QUERY = 12
OUTPUT_FILE = Path(__file__).parent.parent / "data" / "trends.json"

STYLE_QUERIES = [
    {"id": "korean",   "name": "韓系極簡",  "query": "minimalist wedding dress"},
    {"id": "french",   "name": "法式蕾絲",  "query": "lace wedding dress elegant"},
    {"id": "vintage",  "name": "復古風",    "query": "vintage wedding dress"},
    {"id": "ballgown", "name": "公主蓬裙",  "query": "ball gown wedding dress"},
    {"id": "evening",  "name": "晚禮服",    "query": "evening gown formal"},
    {"id": "cocktail", "name": "小禮服",    "query": "cocktail dress elegant"},
    {"id": "satin",    "name": "緞面",      "query": "satin slip dress wedding"},
    {"id": "bohemian", "name": "波希米亞",  "query": "bohemian wedding dress"},
]


def search(key, query, per_page=PER_QUERY):
    """呼叫 Pexels search API。"""
    params = {"query": query, "per_page": per_page, "orientation": "portrait"}
    url = f"{API_BASE}/search?{urlencode(params)}"
    req = urllib.request.Request(url, headers={
        "Authorization": key,
        "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        print(f"   ❌ HTTP {e.code}: {body[:200]}")
        return None


def fetch_pexels(key):
    """主要邏輯：抓所有風格分類，回傳 boards list。"""
    boards = []
    print(f"🎨 從 Pexels 抓 {len(STYLE_QUERIES)} 個風格分類...")
    for style in STYLE_QUERIES:
        print(f"   {style['name']} ({style['query']})")
        result = search(key, style["query"])
        if not result or "photos" not in result:
            print(f"      ⚠️  跳過")
            continue

        pins = []
        for p in result["photos"]:
            pins.append({
                "id": str(p["id"]),
                "title": (p.get("alt") or "").strip()[:80] or style["name"],
                "image": p["src"]["large"],
                "link": p["url"],
                "alt": p.get("alt", ""),
                "photographer": p.get("photographer", ""),
                "photographer_url": p.get("photographer_url", ""),
                "avg_color": p.get("avg_color", ""),
                "source": "pexels",
            })

        if pins:
            boards.append({
                "id": style["id"],
                "name": style["name"],
                "pin_count": len(pins),
                "pins": pins,
            })
            print(f"      ✅ {len(pins)} 張")

        time.sleep(0.3)

    return boards


def main():
    key = os.environ.get("PEXELS_KEY")
    if not key:
        print("❌ ERROR: 環境變數 PEXELS_KEY 沒有設定")
        print("   本機測試：PEXELS_KEY=你的key python scripts/fetch_pexels.py")
        sys.exit(1)

    boards = fetch_pexels(key)

    output = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "source": "pexels",
        "boards": boards,
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    total = sum(b["pin_count"] for b in boards)
    print(f"\n✨ 完成！{len(boards)} 個分類, {total} 張圖")


if __name__ == "__main__":
    main()
