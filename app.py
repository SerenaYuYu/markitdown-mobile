import os
import tempfile
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_file
from markitdown import MarkItDown

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50MB

SUPPORTED_EXTENSIONS = {
    ".pdf", ".docx", ".doc", ".pptx", ".ppt",
    ".xlsx", ".xls", ".csv", ".txt", ".html",
    ".jpg", ".jpeg", ".png", ".gif", ".webp",
    ".epub", ".xml", ".json", ".zip",
}


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
    if ext not in SUPPORTED_EXTENSIONS:
        return jsonify({"error": f"不支援的格式：{ext}"}), 400

    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
        file.save(tmp.name)
        tmp_path = tmp.name

    try:
        md = MarkItDown()
        result = md.convert(tmp_path)
        return jsonify({"markdown": result.text_content, "filename": Path(file.filename).stem})
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
    print("MarkItDown 已啟動！")
    print("請用 Safari 開啟：http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
