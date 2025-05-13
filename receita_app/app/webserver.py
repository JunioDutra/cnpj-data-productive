import os
import hashlib
import re
import bs4 as bs
import urllib.request
from datetime import datetime
from enum import Enum
from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from app.utils import create_connection, close_connection
from app.get_files import get_available_files, process_download
import threading

app = Flask(__name__)
api = Api(app)

class DownloadStatus(Enum):
    DOWNLOADING = 'DOWNLOADING'
    COMPLETED = 'COMPLETED'
    ERROR = 'ERROR'

# Create files table if it doesn't exist
def init_db():
    engine, conn, cur = create_connection()
    try:
        cur.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id SERIAL PRIMARY KEY,
                full_path VARCHAR(500) NOT NULL,
                name VARCHAR(255) NOT NULL,
                size BIGINT,
                file_hash VARCHAR(64),
                url VARCHAR(500),
                download_status VARCHAR(20) CHECK (download_status IN ('DOWNLOADING', 'COMPLETED', 'ERROR'))
            )
        ''')
        conn.commit()
    finally:
        close_connection(engine, conn, cur)

class DownloadedFiles(Resource):
    def get(self):
        output_files = os.getenv('OUTPUT_FILES_PATH')
        if not output_files or not os.path.exists(output_files):
            return {'error': 'Output files directory not found'}, 404
            
        files = []
        for file in os.listdir(output_files):
            if file.endswith('.zip'):
                file_path = os.path.join(output_files, file)
                files.append({
                    'name': file,
                    'size': os.path.getsize(file_path),
                    'created': os.path.getctime(file_path)
                })
                
        return {'files': files}

class File(Resource):
    def calculate_hash(self, file_path):
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def download_file_and_update_db(self, file_info, file_id):
        """Download file and update database status"""
        engine, conn, cur = create_connection()
        try:
            output_files = os.getenv('OUTPUT_FILES_PATH')
            extracted_files = os.getenv('EXTRACTED_FILES_PATH')
            
            # Download and extract the file
            process_download(file_info, output_files, extracted_files)
            
            # Update database with file info
            full_path = os.path.join(output_files, file_info['name'])
            if os.path.exists(full_path):
                size = os.path.getsize(full_path)
                file_hash = self.calculate_hash(full_path)
                
                cur.execute('''
                    UPDATE files 
                    SET size = %s, file_hash = %s, download_status = %s 
                    WHERE id = %s
                ''', (size, file_hash, DownloadStatus.COMPLETED.value, file_id))
                conn.commit()
            else:
                cur.execute('UPDATE files SET download_status = %s WHERE id = %s', 
                           (DownloadStatus.ERROR.value, file_id))
                conn.commit()
        except Exception as e:
            cur.execute('UPDATE files SET download_status = %s WHERE id = %s', 
                       (DownloadStatus.ERROR.value, file_id))
            conn.commit()
        finally:
            close_connection(engine, conn, cur)

    def get(self):
        """Search files (both local and online)"""
        query = request.args.get('query', '')
        year_month = request.args.get('year_month')
        
        # Get files from database (local files)
        engine, conn, cur = create_connection()
        try:
            cur.execute('SELECT * FROM files WHERE name ILIKE %s', (f'%{query}%',))
            local_files = [{
                'id': f[0],
                'full_path': f[1],
                'name': f[2],
                'size': f[3],
                'hash': f[4],
                'url': f[5],
                'download_status': f[6],
                'source': 'local'
            } for f in cur.fetchall()]
            
            # Get available online files
            online_files = [{
                **f,
                'source': 'online',
                'download_status': None
            } for f in get_available_files(year_month) 
               if query.lower() in f['name'].lower()]
            
            return jsonify({
                'local_files': local_files,
                'online_files': online_files
            })
        finally:
            close_connection(engine, conn, cur)

    def post(self):
        """Download a new file"""
        data = request.get_json()
        year_month = data.get('year_month')
        file_name = data.get('name')
        
        # Get available files for the specified year-month
        available_files = get_available_files(year_month)
        file_info = next((f for f in available_files if f['name'] == file_name), None)
        
        if not file_info:
            return {'error': 'File not found in available files'}, 404
            
        output_dir = os.getenv('OUTPUT_FILES_PATH')
        full_path = os.path.join(output_dir, file_name)

        engine, conn, cur = create_connection()
        try:
            # Check if file is already being downloaded
            cur.execute('SELECT id, download_status FROM files WHERE name = %s', (file_name,))
            existing_file = cur.fetchone()
            
            if existing_file and existing_file[1] == DownloadStatus.DOWNLOADING.value:
                return {'error': 'File is already being downloaded'}, 409
            
            # Create or update file record
            if existing_file:
                file_id = existing_file[0]
                cur.execute('''
                    UPDATE files 
                    SET download_status = %s 
                    WHERE id = %s
                ''', (DownloadStatus.DOWNLOADING.value, file_id))
            else:
                cur.execute('''
                    INSERT INTO files (full_path, name, url, download_status)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                ''', (full_path, file_name, file_info['url'], DownloadStatus.DOWNLOADING.value))
                file_id = cur.fetchone()[0]
            
            conn.commit()

            # Start download in background
            thread = threading.Thread(
                target=self.download_file_and_update_db,
                args=(file_info, file_id)
            )
            thread.start()

            return {'id': file_id, 'message': 'Download started'}, 202
        finally:
            close_connection(engine, conn, cur)

    def delete(self, file_id):
        """Delete a file"""
        engine, conn, cur = create_connection()
        try:
            cur.execute('SELECT full_path FROM files WHERE id = %s', (file_id,))
            result = cur.fetchone()
            if not result:
                return {'error': 'File not found'}, 404

            full_path = result[0]
            if os.path.exists(full_path):
                os.remove(full_path)

            cur.execute('DELETE FROM files WHERE id = %s', (file_id,))
            conn.commit()
            return {'message': 'File deleted successfully'}
        finally:
            close_connection(engine, conn, cur)

class AvailableFiles(Resource):
    def get(self):
        """List available files from Receita Federal for a specific year-month"""
        year_month = request.args.get('year_month')
        if not year_month:
            current_date = datetime.now()
            year_month = current_date.strftime('%Y-%m')

        dados_rf = f'https://arquivos.receitafederal.gov.br/dados/cnpj/dados_abertos_cnpj/{year_month}/'
        
        try:
            raw_html = urllib.request.urlopen(dados_rf)
            raw_html = raw_html.read()

            page_items = bs.BeautifulSoup(raw_html, 'lxml')
            html_str = str(page_items)

            files = []
            text = '.zip'
            for m in re.finditer(text, html_str):
                i_start = m.start()-40
                i_end = m.end()
                i_loc = html_str[i_start:i_end].find('href=')+6
                file_name = html_str[i_start+i_loc:i_end]
                if not file_name.find('.zip">') > -1:
                    files.append({
                        'name': file_name,
                        'url': dados_rf + file_name,
                        'year_month': year_month
                    })

            return jsonify({
                'year_month': year_month,
                'base_url': dados_rf,
                'files': files
            })
        except urllib.error.URLError:
            return {'error': f'No files found for year-month: {year_month}'}, 404

# Update the api routes
api.add_resource(DownloadedFiles, '/api/downloaded-files')
api.add_resource(File, '/api/files', '/api/files/<int:file_id>')
api.add_resource(AvailableFiles, '/api/available-files')

def start_server(host='0.0.0.0', port=5000):
    init_db()  # Initialize database tables
    app.run(host=host, port=port)

if __name__ == '__main__':
    start_server()