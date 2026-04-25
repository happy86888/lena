"""
Miss Lena · 主要抓圖腳本（多來源整合）
========================================
自動偵測環境變數有哪些 key，從對應的圖庫抓圖，並把結果合併。

支援：
  - PEXELS_KEY      → 從 Pexels 抓
  - UNSPLASH_KEY    → 從 Unsplash 抓
  - 兩個都沒 → 噴錯
  - 只有一個  → 只抓那一個
  - 兩個都有  → 兩邊都抓，交錯混合

執行：
    PEXELS_KEY=xxx UNSPLASH_KEY=yyy python scripts/fetch_all.py
"""

import os
import sys
import json
from datetime import datetime, timezone
from pathlib import Path

from fetch_pexels import fetch_pexels
from fetch_unsplash import fetch_unsplash

OUTPUT_FILE = Path(__file__).parent.parent / "data" / "trends.json"


def merge_boards(*board_lists):
    """
    合併多個來源的 boards。同 id 的 board 會把 pins 交錯混合，
    這樣畫面看起來會 Pexels / Unsplash 圖混合分布。
    """
    merged = {}
    for boards in board_lists:
        for b in boards:
            bid = b["id"]
            if bid not in merged:
                merged[bid] = {"id": bid, "name": b["name"], "pins": []}
            merged[bid]["pins"].append(b["pins"])  # 暫存成 list of list

    # 交錯每個 board 的 pins
    final = []
    for bid, b in merged.items():
        interleaved = []
        pin_lists = b["pins"]  # 每個元素是一個 source 的 pins
        max_len = max(len(pl) for pl in pin_lists)
        for i in range(max_len):
            for pl in pin_lists:
                if i < len(pl):
                    interleaved.append(pl[i])
        final.append({
            "id": bid,
            "name": b["name"],
            "pin_count": len(interleaved),
            "pins": interleaved,
        })
    return final


def main():
    pexels_key = os.environ.get("PEXELS_KEY")
    unsplash_key = os.environ.get("UNSPLASH_KEY")

    if not pexels_key and not unsplash_key:
        print("❌ ERROR: 至少要設定一個 key（PEXELS_KEY 或 UNSPLASH_KEY）")
        sys.exit(1)

    sources_used = []
    all_boards = []

    if pexels_key:
        print("=" * 50)
        try:
            boards = fetch_pexels(pexels_key)
            all_boards.append(boards)
            sources_used.append("pexels")
        except Exception as e:
            print(f"⚠️  Pexels 抓取失敗：{e}")
    else:
        print("ℹ️  PEXELS_KEY 未設定，跳過 Pexels")

    if unsplash_key:
        print("=" * 50)
        try:
            boards = fetch_unsplash(unsplash_key)
            all_boards.append(boards)
            sources_used.append("unsplash")
        except Exception as e:
            print(f"⚠️  Unsplash 抓取失敗：{e}")
    else:
        print("ℹ️  UNSPLASH_KEY 未設定，跳過 Unsplash")

    if not all_boards:
        print("❌ 沒有任何來源抓取成功，不寫檔")
        sys.exit(1)

    print("=" * 50)
    print(f"🔀 合併 {len(all_boards)} 個來源的結果...")
    merged = merge_boards(*all_boards)

    output = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "sources": sources_used,
        "boards": merged,
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")

    total = sum(b["pin_count"] for b in merged)
    print(f"\n✨ 全部完成！")
    print(f"   來源：{', '.join(sources_used)}")
    print(f"   {len(merged)} 個風格分類, 共 {total} 張圖")
    print(f"   寫入 {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
