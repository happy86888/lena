# Miss Lena · Bridal Atelier Website

Miss Lena 婚紗品牌官方網站。線上預購 + 自動趨勢牆（支援 Pexels & Unsplash 雙來源，可自由切換）。

---

## 📁 專案結構

```
miss-lena-site/
├── index.html                          # 網站本體
├── data/
│   └── trends.json                     # 抓回來的圖（GitHub Actions 自動更新）
├── scripts/
│   ├── fetch_pexels.py                 # 抓 Pexels（可單跑）
│   ├── fetch_unsplash.py               # 抓 Unsplash（可單跑）
│   └── fetch_all.py                    # 主腳本，自動偵測有哪些 key
├── .github/workflows/
│   └── update-trends.yml               # GitHub Actions（每天自動跑）
├── .gitignore
└── README.md
```

---

## 🎯 你現在的狀態

✅ 已拿到 Pexels API Key
✅ 已拿到 Unsplash Access Key（先存著）
🚀 **建議先只設 Pexels，跑通流程後再加 Unsplash**

---

## 🚀 第一階段：先跑 Pexels（10 分鐘）

### Step 1 — 上傳到 GitHub

```bash
cd miss-lena-site
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/你的帳號/miss-lena-site.git
git push -u origin main
```

### Step 2 — ⭐️ 設定 GitHub Secret（最重要）

1. Repo → **Settings** → **Secrets and variables** → **Actions**
2. **New repository secret**
3. 填：
   - **Name**: `PEXELS_KEY`（一字不差，全大寫）
   - **Secret**: 貼你的 Pexels key
4. **Add secret**

> ⚠️ 不要把 key 寫在程式碼裡 push 上去。

### Step 3 — 手動跑一次 Actions

1. Repo → **Actions** → **Update Trends**
2. **Run workflow** → 綠色 **Run workflow** 按鈕
3. 等 30 秒～1 分鐘
4. ✅ 綠勾 = 成功

### Step 4 — 啟用 GitHub Pages

1. **Settings** → **Pages**
2. **Source**: `Deploy from a branch`
3. **Branch**: `main` / `/ (root)` → **Save**
4. 等 1-2 分鐘 → 開上面顯示的網址

🎉 完成！趨勢牆會顯示 8 個風格分類，每類 12 張 = 共 96 張婚紗圖。

---

## 🎨 第二階段：之後想加 Unsplash（30 秒）

當你想要更多更豐富的圖、想結合 Unsplash 編輯感強的攝影：

### 唯一要做的事

1. Repo → **Settings** → **Secrets and variables** → **Actions**
2. **New repository secret**
3. 填：
   - **Name**: `UNSPLASH_KEY`
   - **Secret**: 貼你的 Unsplash **Access Key**（不是 Secret Key）
4. **Add secret**
5. 去 **Actions** → **Run workflow** 重跑一次

完成。**完全不用碰程式碼**。

從此以後每天 trend wall 會：
- 每個分類抓 12 張 Pexels + 12 張 Unsplash = **24 張**
- 兩個來源**交錯混合**呈現
- 自動署名「Photo by 攝影師 on Pexels/Unsplash」

### 之後想換回只用 Pexels？

去 GitHub Secrets 把 `UNSPLASH_KEY` 刪掉就好。腳本會自動偵測、跳過 Unsplash。

### 兩個 Key 都不想用？換成 Pinterest？

Pinterest 那份腳本還在我電腦裡，跟我說一聲我給你。架構支援多來源混合，三個一起也行。

---

## 🎨 自訂風格分類

打開 `scripts/fetch_pexels.py` 或 `scripts/fetch_unsplash.py`，找到這段：

```python
STYLE_QUERIES = [
    {"id": "korean",   "name": "韓系極簡",  "query": "minimalist wedding dress"},
    {"id": "french",   "name": "法式蕾絲",  "query": "lace wedding dress elegant"},
    # ... 想改就改
]
```

| 欄位 | 說明 |
|---|---|
| `id` | 內部 ID，**兩個檔案要保持一致**才能正確合併 |
| `name` | 顯示在網站 tab 上的名字 |
| `query` | 搜尋關鍵字（**英文比較多結果**） |

> 💡 **小技巧**：兩個圖庫的 STYLE_QUERIES 可以用**不同的 query 但同樣的 id**。例如同一個「韓系極簡」分類，Pexels 用 `minimalist wedding dress`、Unsplash 用 `simple bride white`，這樣抓到的圖會更不同更豐富。

---

## ⚠️ 兩個圖庫的限制

| 項目 | Pexels | Unsplash |
|---|---|---|
| 速率限制 | 每月幾千次沒問題 | **Demo: 50 次/小時** |
| 署名要求 | 不強制（前端還是會放） | **強制**，前端已處理 |
| 商業使用 | ✅ | ✅ |
| 升級需求 | 不用 | 想要 5000/hr 要申請 Production |

對你的用途（一天跑一次 = 每次 16 次呼叫），Demo mode 完全夠用。

---

## 🔄 維運速查

| 想做什麼 | 怎麼做 |
|---|---|
| 改風格分類 | 改 `STYLE_QUERIES` |
| 改網站樣式 | 改 `index.html` |
| 加 Unsplash 來源 | 加 `UNSPLASH_KEY` Secret |
| 移除 Unsplash 來源 | 刪 `UNSPLASH_KEY` Secret |
| 改自動跑時間 | 改 workflow 的 cron |
| key 換新 | 直接 Update secret |
| 連 miss-lena.com | Settings → Pages → Custom domain |

---

## 🧪 本機測試（選用）

```bash
brew install python

# 只跑 Pexels
PEXELS_KEY=xxx python3 scripts/fetch_pexels.py

# 只跑 Unsplash
UNSPLASH_KEY=xxx python3 scripts/fetch_unsplash.py

# 兩個都跑（合併輸出）
PEXELS_KEY=xxx UNSPLASH_KEY=yyy python3 scripts/fetch_all.py

# 預覽網站
python3 -m http.server 8000   # 開 http://localhost:8000
```

---

## ❓ 常見問題

**Q1: Actions 401 / Unauthorized**
A: Secret 名稱打錯（要全大寫 `PEXELS_KEY` `UNSPLASH_KEY`），或 key 過期。

**Q2: trends.json 是空的**
A: 看 Actions log，檢查 secret 名稱跟 key 內容。

**Q3: 想要更多／更少圖**
A: 改腳本最上方 `PER_QUERY = 12`。Pexels 最多 80，Unsplash 最多 30。

**Q4: Pages 404**
A: 第一次啟用要等 5-10 分鐘。

**Q5: 我想要把整個風格分類改成英文**
A: 改 STYLE_QUERIES 的 `name` 欄位即可，例如 `"name": "Korean Minimal"`。

---

Built with ❤️ for Miss Lena · Tainan, Taiwan
