from app.files import files_service
from app.files.file_types import FileEntity
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/files', methods=['GET'])
def files():
    file_type = request.args.get('type')
    ref = request.args.get('ref')
    if not file_type:
        return jsonify({
            'success': False,
            'message': 'Parâmetro "type" é obrigatório'
        }), 400
    
    try:
        data = files_service.list_files(file_type=file_type, ref=ref)
        return jsonify({
            'success': True,
            'type': file_type,
            'data': data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao listar arquivos: {str(e)}'
        }), 500

@app.route('/files/fetch', methods=['GET'])
def files_fetch():
    year = request.args.get('year')
    month = request.args.get('month')
    
    if not year or not month:
        return jsonify({
            'success': False,
            'message': 'Parâmetros "year", "month" e "type" são obrigatórios'
        }), 400
    
    try:
        ref = f'{int(year):04d}-{int(month):02d}'
        data = files_service.fetch(ref)
        return jsonify({
            'success': True,
            'year': year,
            'month': month,
            'data': data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar arquivos: {str(e)}'
        }), 500

@app.route('/files/download', methods=['POST'])
def files_download():
    try:
        data = request.get_json()

        if not data or 'files' not in data:
            return jsonify({
                'success': False,
                'message': 'A lista de arquivos é obrigatória'
            }), 400

        files = data['files']

        if not isinstance(files, list) or len(files) == 0:
            return jsonify({
                'success': False,
                'message': 'A lista de arquivos deve ser um array não vazio'
            }), 400
        
        files_service.download_files(files)

        return jsonify({
            'success': True,
            'message': f'Download iniciado para {len(files)} arquivo(s)',
            'files': files
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao processar solicitação: {str(e)}'
        }), 500

@app.route('/files/process', methods=['POST'])
def files_process():
    try:
        data = request.get_json()

        if not data or 'files' not in data:
            return jsonify({
                'success': False,
                'message': 'A lista de arquivos é obrigatória'
            }), 400

        files = data['files']

        if not isinstance(files, list) or len(files) == 0:
            return jsonify({
                'success': False,
                'message': 'A lista de arquivos deve ser um array não vazio'
            }), 400
        
        # Convert dicts to FileEntity (expected by service)
        normalized_files = []
        for f in files:
            if isinstance(f, dict):
                normalized_files.append(FileEntity(
                    id=f.get('id'),
                    created_at=f.get('created_at'),
                    path=f.get('path'),
                    name=f.get('name'),
                    ref=f.get('ref'),
                    file_size=f.get('file_size', 0),
                    status=f.get('status'),
                    related_at=f.get('related_at'),
                ))
            else:
                normalized_files.append(f)

        files_service.process_files(normalized_files)

        return jsonify({
            'success': True,
            'message': f'Processamento iniciado para {len(files)} arquivo(s)',
            'files': files
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao processar solicitação: {str(e)}'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'success': True,
        'message': 'API está funcionando',
        'status': 'healthy'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)