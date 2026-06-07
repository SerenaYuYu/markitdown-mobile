import os
import tempfile
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_file

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50MB


def convert_to_markdown(file_path: str, ext: str) -> str:
    if ext in (".txt", ".md", ".csv", ".json", ".xml"):
        with open(file_path, encoding="utf-8", errors="replace") as f:
            content = f.read()
        if ext == ".csv":
            lines = content.splitlines()
            if not lines:
                return ""
            headers = lines[0].split(",")
            md = "| " + " | ".join(headers) + " |\n"
            md += "| " + " | ".join(["---"] * len(headers)) + " |\n"
            for line in lines[1:]:
                md += "| " + " | ".join(line.split(",")) + " |\n"
            return md
        return content

    if ext == ".html":
        from markdownify import markdownify
        with open(file_path, encoding="utf-8", errors="replace") as f:
            html = f.read()
        return markdownify(html)

    if ext == ".pdf":
        from pypdf import PdfReader
        reader = PdfReader(file_path)
        lines = []
        for i, page in enumerate(reader.pages, 1):
            text = page.extract_text() or ""
            if text.strip():
                lines.append(f"## 第 {i} 頁\n\n{text.strip()}")
        return "\n\n---\n\n".join(lines)

    if ext in (".docx",):
        from docx import Document
        doc = Document(file_path)
        lines = []
        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue
            style = para.style.name.lower()
            if "heading 1" in style:
                lines.append(f"# {text}")
            elif "heading 2" in style:
                lines.append(f"## {text}")
            elif "heading 3" in style:
                lines.append(f"### {text}")
            else:
                lines.append(text)
        return "\n\n".join(lines)

    if ext in (".jpg", ".jpeg", ".png", ".gif", ".webp"):
        return f"![圖片]({Path(file_path).name})\n\n> 圖片已嵌入，OCR 功能需要額外設定。"

    raise ValueError(f"不支援的格式：{ext}")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/convert", methods=["POST"])
def convert():
    if "file" not in request.files:
        return jsonify({"error": "未選擇檔案"}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "未選擇檔案"}), 400

    ext = Path(file.filename).suffix.lower()
    supported = {".pdf", ".docx", ".txt", ".md", ".csv",
                 ".html", ".json", ".xml", ".jpg", ".jpeg", ".png", ".gif", ".webp"}

    if ext not in supported:
        return jsonify({"error": f"不支援的格式：{ext}"}), 400

    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
        file.save(tmp.name)
        tmp_path = tmp.name

    try:
        result = convert_to_markdown(tmp_path, ext)
        return jsonify({"markdown": result, "filename": Path(file.filename).stem})
    except Exception as e:
        return jsonify({"error": f"轉換失敗：{str(e)}"}), 500
    finally:
        os.unlink(tmp_path)


@app.route("/download", methods=["POST"])
def download():
    data = request.get_json()
    markdown = data.get("markdown", "")
    filename = data.get("filename", "output") + ".md"

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", delete=False, encoding="utf-8"
    ) as tmp:
        tmp.write(markdown)
        tmp_path = tmp.name

    return send_file(
        tmp_path,
        as_attachment=True,
        download_name=filename,
        mimetype="text/markdown",
    )


if __name__ == "__main__":
    print("MarkItDown 行動版已啟動！")
    print("請用 Safari 開啟：http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
