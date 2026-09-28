# Streamlit Item Manager

以 Streamlit 和 SQLite 製作的單頁 CRUD 示範專案，可新增、查看、修改及刪除商品。

## 功能

- 商品欄位：商品名稱、整數價格、整數數量
- 新增、顯示、編輯與刪除商品
- 刪除前二次確認
- 一鍵重設成三筆範例資料，重設前也會再次確認
- SQLite 本機持久化儲存

## 安裝與啟動

建議先建立並啟用 Python 虛擬環境，再執行：

```powershell
python -m pip install -r requirements.txt
python -m streamlit run streamlit_app.py
```

第一次啟動會自動建立 `items.db`，並加入以下範例：

| 商品名稱 | 價格 | 數量 |
| --- | ---: | ---: |
| 礦泉水 | 20 | 15 |
| 咖啡 | 45 | 8 |
| 筆記本 | 60 | 12 |

之後即使刪除全部商品，重新啟動也不會自動補回。需要恢復範例時，請使用畫面中的「重設範例資料」。

## 測試

```powershell
python -m pytest -v
```

測試使用獨立的暫存資料庫，不會修改實際操作所使用的 `items.db`。
