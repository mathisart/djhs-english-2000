# 每月 Supabase → Google Drive CSV 備份

此工具備份 `players` 與 `learning_events`，每 1,000 筆分頁讀取，輸出 UTF-8 BOM CSV，避免 Excel 中文亂碼。

## Drive 結構

```
指定的備份根資料夾/
├─ backup-log.csv
├─ 2026-10/
│  ├─ players-20261001-030000.csv
│  ├─ learning_events-20261001-030000.csv
│  └─ manifest-20261001-030000.json
└─ 2026-11/
   └─ ...
```

每次執行都建立有時間戳的新檔，不覆蓋舊備份。

## 一次性設定

1. 在 Google Drive 建立一個備份資料夾，例如「DJHS English 2000 備份」，從網址複製資料夾 ID。
2. 建立 Google Apps Script 專案，將 `Code.gs` 與 `appsscript.json` 貼入。
3. Apps Script → Project Settings → Script Properties 新增：
   - `SUPABASE_URL`: Supabase Project URL
   - `SUPABASE_SECRET_KEY`: Supabase Secret key（或 legacy service_role）
   - `BACKUP_FOLDER_ID`: Google Drive 備份資料夾 ID
4. **Secret key 只放 Script Properties，絕對不要放 GitHub、前端 app.js 或試算表。**
5. 手動執行 `testConnection()`，第一次需授權。
6. 手動執行 `backupNow()`，確認 Drive 產生兩份 CSV + manifest。
7. 執行一次 `installMonthlyTrigger()`。之後每月 1 日約凌晨 3 時自動執行。

## 成功／失敗紀錄

根資料夾的 `backup-log.csv` 記錄：
- timestamp
- status: SUCCESS / FAILED
- month
- total_rows
- error

每次成功備份也會在月份資料夾建立 manifest JSON。

## 還原注意

這是「資料快照」備份，不是 PostgreSQL 完整 dump。CSV 很適合統計、稽核與人工復原；若未來需要一鍵完整還原資料庫，應再增加 PostgreSQL dump 備份。
