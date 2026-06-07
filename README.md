# MarkItDown 行動版

在 iPhone / iPad 上透過瀏覽器使用 MarkItDown 轉換工具。

## 使用方式

### 第一次安裝（只需做一次）

1. 從 App Store 下載 **a-Shell**
2. 開啟 a-Shell，執行：

```bash
lg2 clone https://github.com/SerenaYuYu/markitdown-mobile
cd markitdown-mobile
pip install flask pypdf markdownify python-docx
```

### 每次使用

1. 開啟 a-Shell，執行：

```bash
cd markitdown-mobile
python app.py
```

2. 開啟 **Safari**，輸入：`http://localhost:5000`
3. 選擇檔案 → 開始轉換 → 複製或儲存結果

### 結束使用

在 a-Shell 按 `Ctrl+C` 停止伺服器。

## 支援格式

PDF、Word、PowerPoint、Excel、圖片（JPG/PNG）、HTML、TXT、CSV、EPUB、ZIP

## 更新

```bash
cd markitdown-mobile
lg2 pull
```
