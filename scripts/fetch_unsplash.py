"""
Miss Lena · Unsplash Trends Fetcher
====================================
從 Unsplash API 抓婚紗、禮服、小禮服相關圖片，依風格分類。

可以單獨跑：
    UNSPLASH_KEY=你的key python scripts/fetch_unsplash.py

也會被 fetch_all.py 引用，跟 Pexels 結果合併。

注意：Unsplash API 強制要署名攝影師＋連回 Unsplash，這在前端 index.html
已經處理好（會顯示 photographer 名字＋ utm_source 連結）。
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

API_BASE = "https://api.unsplash.com"
PER_QUERY = 12
OUTPUT_FILE = Path(__file__).parent.parent / "data" / "trends.json"

# 跟 Pexels 一致的風格分類；id 一樣，方便合併
STYLE_QUERIES = [
    {"id": "korean",   "name": "韓系極簡",  "query": "minimalist wedding dress"},
    {"id": "french",   "name": "法式蕾絲",  "query": "lace wedding dress"},
    {"id": "vintage",  "name": "復古風",    "query": "vintage wedding dress"},
    {"id": "ballgown", "name": "公主蓬裙",  "query": "ball gown bride"},
    {"id": "evening",  "name": "晚禮服",    "query": "evening gown formal"},
    {"id": "cocktail", "name": "小禮服",    "query": "cocktail dress elegant"},
    {"id": "satin",    "name": "緞面",      "query": "satin slip dress"},
    {"id": "bohemian", "name": "波希米亞",  "query": "bohemian bride"},
]


def search(key, query, per_page=PER_QUERY):
    """呼叫 Unsplash search API。"""
    params = {
        "query": query,
        "per_page": per_page,
        "orientation": "portrait",
        "content_filter": "high",  # 過濾不適合內容
    }
    url = f"{API_BASE}/search/photos?{urlencode(params)}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Client-ID {key}",
        "Accept-Version": "v1",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        print(f"   ❌ HTTP {e.code}: {body[:200]}")
        return None


def fetch_unsplash(key):
    """主要邏輯：抓所有風格分類，回傳 boards list。"""
    boards = []
    print(f"📷 從 Unsplash 抓 {len(STYLE_QUERIES)} 個風格分類...")
    for style in STYLE_QUERIES:
        print(f"   {style['name']} ({style['query']})")
        result = search(key, style["query"])
        if not result or "results" not in result:
            print(f"      ⚠️  跳過")
            continue

        pins = []
        for p in result["results"]:
            user = p.get("user", {})
            photographer = user.get("name", "Unknown")
            # Unsplash 規定圖片連結必須加 utm_source 與 utm_medium
            photographer_url = f"{user.get('links', {}).get('html', '')}?utm_source=miss_lena&utm_medium=referral"
            photo_url = f"{p.get('links', {}).get('html', '')}?utm_source=miss_lena&utm_medium=referral"

            pins.append({
                "id": p["id"],
                "title": (p.get("alt_description") or p.get("description") or style["name"])[:80],
                "image": p["urls"]["regular"],  # ~1080px 寬，trend wall 剛好
                "link": photo_url,
                "alt": p.get("alt_description", ""),
                "photographer": photographer,
                "photographer_url": photographer_url,
                "avg_color": p.get("color", ""),
                "source": "unsplash",
            })

            # Unsplash 規定：每次顯示要 trigger download tracking（這個 endpoint 不算 rate limit）
            try:
                dl_url = p.get("links", {}).get("download_location")
                if dl_url:
                    req = urllib.request.Request(dl_url, headers={"Authorization": f"Client-ID {key}"})
                    urllib.request.urlopen(req, timeout=10).close()
            except Exception:
                pass  # tracking 失敗不影響主功能

        if pins:
            boards.append({
                "id": style["id"],
                "name": style["name"],
                "pin_count": len(pins),
                "pins": pins,
            })
            print(f"      ✅ {len(pins)} 張")

        time.sleep(0.5)  # Unsplash demo mode 限制 50/hr，保險慢一點

    return boards


def main():
    key = os.environ.get("UNSPLASH_KEY")
    if not key:
        print("❌ ERROR: 環境變數 UNSPLASH_KEY 沒有設定")
        print("   本機測試：UNSPLASH_KEY=你的key python scripts/fetch_unsplash.py")
        sys.exit(1)

    boards = fetch_unsplash(key)

    output = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "source": "unsplash",
        "boards": boards,
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    total = sum(b["pin_count"] for b in boards)
    print(f"\n✨ 完成！{len(boards)} 個分類, {total} 張圖")


if __name__ == "__main__":
    main()
