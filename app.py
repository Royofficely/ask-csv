from flask import Flask, request, jsonify
import os
import duckdb
from werkzeug.utils import secure_filename
from langchain_experimental.agents import create_csv_agent
from langchain_openai import ChatOpenAI
from functools import wraps
from datetime import datetime

app = Flask(__name__)

API_TOKEN = os.environ.get('API_TOKEN')
OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-4o')
DATA_DIR = os.environ.get('DATA_DIR', '/data')

os.makedirs(DATA_DIR, exist_ok=True)

DB_PATH = os.path.join(DATA_DIR, 'askcsv.duckdb')

def get_db():
    return duckdb.connect(DB_PATH)

def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.execute('CREATE SEQUENCE IF NOT EXISTS files_seq START 1')
    conn.close()

init_db()

def require_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not API_TOKEN:
            return jsonify({'error': 'API_TOKEN not configured'}), 500
        token = request.headers.get('Authorization')
        if not token or token != f'Bearer {API_TOKEN}':
            return jsonify({'error': 'Invalid or missing token'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/api/health', methods=['GET'])
def health():
    try:
        conn = get_db()
        conn.execute('SELECT 1')
        conn.close()
        db_status = True
    except Exception:
        db_status = False

    return jsonify({
        'status': 'healthy',
        'database': db_status,
        'openai_configured': bool(os.environ.get('OPENAI_API_KEY'))
    })

@app.route('/upload', methods=['POST'])
@require_token
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'Only CSV files are supported'}), 400

    filename = secure_filename(file.filename)

    conn = get_db()
    file_id = conn.execute("SELECT nextval('files_seq')").fetchone()[0]

    filepath = os.path.join(DATA_DIR, f'{file_id}_{filename}')
    file.save(filepath)

    conn.execute(
        'INSERT INTO files (id, filename, filepath) VALUES (?, ?, ?)',
        [file_id, filename, filepath]
    )
    conn.close()

    return jsonify({
        'message': 'File uploaded successfully',
        'file_id': str(file_id),
        'filename': filename
    }), 201

@app.route('/query', methods=['POST'])
@require_token
def query_files():
    data = request.get_json()
    if not data or 'query' not in data or 'file_ids' not in data:
        return jsonify({'error': 'Missing query or file_ids'}), 400

    conn = get_db()

    file_paths = []
    for file_id in data['file_ids']:
        result = conn.execute('SELECT filepath FROM files WHERE id = ?', [int(file_id)]).fetchone()
        if result and os.path.exists(result[0]):
            file_paths.append(result[0])

    conn.close()

    if not file_paths:
        return jsonify({'error': 'No valid files found'}), 404

    try:
        agent = create_csv_agent(
            ChatOpenAI(temperature=0, model=OPENAI_MODEL),
            file_paths,
            verbose=False,
            allow_dangerous_code=True
        )

        response = agent.invoke(data['query'])

        return jsonify({
            'status': 'success',
            'data': {
                'query': data['query'],
                'result': response.get('output', str(response))
            }
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/files', methods=['GET'])
@require_token
def list_files():
    conn = get_db()
    files = conn.execute('SELECT id, filename, created_at FROM files ORDER BY created_at DESC').fetchall()
    conn.close()

    return jsonify({
        'files': [
            {'id': str(f[0]), 'filename': f[1], 'created_at': f[2].isoformat() if f[2] else None}
            for f in files
        ]
    })

@app.route('/files/<file_id>', methods=['DELETE'])
@require_token
def delete_file(file_id):
    conn = get_db()
    result = conn.execute('SELECT filepath FROM files WHERE id = ?', [int(file_id)]).fetchone()

    if not result:
        conn.close()
        return jsonify({'error': 'File not found'}), 404

    filepath = result[0]
    conn.execute('DELETE FROM files WHERE id = ?', [int(file_id)])
    conn.close()

    if os.path.exists(filepath):
        os.remove(filepath)

    return jsonify({'message': 'File deleted successfully'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('FLASK_DEBUG', 'false').lower() == 'true')
