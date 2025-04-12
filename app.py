import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import pandas as pd

app = Flask(__name__)
CORS(app)  # 添加跨域支持

# 设置文件上传的目录
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 设置保存解析后数据的目录
SAVED_DATA_FOLDER = 'saved_data'
if not os.path.exists(SAVED_DATA_FOLDER):
    os.makedirs(SAVED_DATA_FOLDER)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': '没有文件部分'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400

    # 打印文件信息调试
    print(f"Received file: {file.filename}")

    # 生成上传文件的路径并保存文件
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)

    try:
        file.save(file_path)
        print(f"File saved at {file_path}")
    except Exception as e:
        return jsonify({'error': f'无法保存文件: {str(e)}'}), 500

    try:
        # 处理不同类型的文件
        if file.filename.endswith('.json'):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
        elif file.filename.endswith('.csv'):
            # 使用 pandas 读取 CSV 文件
            df = pd.read_csv(file_path)
            content = df.to_dict(orient='records')
        elif file.filename.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().splitlines()  # 读取文本文件内容
        elif file.filename.endswith('.xlsx'):
            # 使用 pandas 读取 Excel 文件
            df = pd.read_excel(file_path)
            content = df.to_dict(orient='records')
        else:
            return jsonify({'error': '不支持的文件类型'}), 400
    except Exception as e:
        return jsonify({'error': f'无法读取文件内容: {str(e)}'}), 500

    # 将内容转换为 JSON 格式的键值对
    formatted_content = json.dumps(content, indent=4)

    # 保存解析后的数据到本地文件
    saved_file_path = os.path.join(SAVED_DATA_FOLDER, file.filename)
    try:
        with open(saved_file_path, 'w', encoding='utf-8') as f:
            f.write(formatted_content)
        print(f"File saved at {saved_file_path}")
    except Exception as e:
        return jsonify({'error': f'无法保存解析后的文件: {str(e)}'}), 500

    # 返回完整的文件内容
    return jsonify({
        'message': '文件上传并处理成功',
        'original_file_path': file_path,
        'saved_file_path': saved_file_path,
        'content': content  # 返回完整的内容
    })

@app.route('/api/data', methods=['GET'])
def get_data():
    # 返回保存的解析后数据
    try:
        # 获取保存的文件列表
        saved_files = os.listdir(SAVED_DATA_FOLDER)
        if not saved_files:
            return jsonify({'error': '没有保存的数据文件'}), 404

        # 读取最新的文件内容
        latest_file = saved_files[-1]  # 假设最新的文件是列表中的最后一个文件
        saved_file_path = os.path.join(SAVED_DATA_FOLDER, latest_file)

        with open(saved_file_path, 'r', encoding='utf-8') as f:
            content = json.load(f)
        return jsonify({'data': content})
    except Exception as e:
        return jsonify({'error': f'无法读取保存的数据: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)

