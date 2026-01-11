from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
from langchain_experimental.agents import create_csv_agent
from langchain_openai import ChatOpenAI
import psycopg2
from functools import wraps

app = Flask(__name__)

DATABASE_URL = os.environ.get('DATABASE_URL')
API_TOKEN = os.environ.get('API_TOKEN')
OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-4o')

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

def get_db_connection():
    if not DATABASE_URL:
        raise ValueError('DATABASE_URL not configured')
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS files
                  (id SERIAL PRIMARY KEY,
                   file_id TEXT,
                   file_data BYTEA,
                   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    cur.close()
    conn.close()

@app.route('/api/health', methods=['GET'])
def health():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT 1')
        cur.close()
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
    file_data = file.read()

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO files (file_id, file_data) VALUES (%s, %s) RETURNING id',
        (filename, psycopg2.Binary(file_data))
    )
    file_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
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

    conn = get_db_connection()
    cur = conn.cursor()

    file_paths = []
    for file_id in data['file_ids']:
        cur.execute('SELECT file_data FROM files WHERE id = %s', (file_id,))
        result = cur.fetchone()
        if result:
            temp_path = f'/tmp/csv_{file_id}.csv'
            with open(temp_path, 'wb') as f:
                f.write(result[0])
            file_paths.append(temp_path)

    cur.close()
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
    finally:
        for path in file_paths:
            try:
                os.remove(path)
            except Exception:
                pass

@app.route('/files', methods=['GET'])
@require_token
def list_files():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, file_id, created_at FROM files ORDER BY created_at DESC')
    files = cur.fetchall()
    cur.close()
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
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM files WHERE id = %s RETURNING id', (file_id,))
    deleted = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    if not deleted:
        return jsonify({'error': 'File not found'}), 404

    return jsonify({'message': 'File deleted successfully'}), 200

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('FLASK_DEBUG', 'false').lower() == 'true')
