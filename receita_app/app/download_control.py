import os
from datetime import datetime
from app.utils import create_connection, close_connection


def register_available_files(files_list):
    """
    Registra os arquivos disponíveis na tabela de controle com status 'pending'
    e path vazio. Só insere se não existir o registro para evitar duplicatas.
    
    Args:
        files_list: Lista de dicionários com informações dos arquivos
                   [{'name': 'arquivo.zip', 'year_month': '2024-09'}]
    
    Returns:
        int: Número de novos registros inseridos
    """
    if not files_list:
        return 0
    
    engine, conn, cur = create_connection()
    inserted_count = 0
    
    try:
        for file_info in files_list:
            # Verifica se o registro já existe
            cur.execute("""
                SELECT id FROM download_control 
                WHERE name = %s AND ref = %s
            """, (file_info['name'], file_info['year_month']))
            
            existing = cur.fetchone()
            
            if not existing:
                # Insere novo registro com path vazio e status pending
                cur.execute("""
                    INSERT INTO download_control (name, ref, path, status)
                    VALUES (%s, %s, %s, %s)
                """, (file_info['name'], file_info['year_month'], '', 'pending'))
                inserted_count += 1
                print(f'Registrado arquivo disponível: {file_info["name"]}')
        
        conn.commit()
        print(f'Total de novos arquivos registrados: {inserted_count}')
        
    except Exception as e:
        conn.rollback()
        print(f'Erro ao registrar arquivos disponíveis: {str(e)}')
        raise e
    finally:
        close_connection(engine, conn, cur)
    
    return inserted_count


def update_download_success(file_name, ref, file_path, file_size=0):
    """
    Atualiza o registro quando o download é bem-sucedido.
    
    Args:
        file_name: Nome do arquivo
        ref: Referência (ano-mês)
        file_path: Caminho onde o arquivo foi salvo
        file_size: Tamanho do arquivo em bytes
    
    Returns:
        bool: True se atualizou com sucesso
    """
    engine, conn, cur = create_connection()
    
    try:
        cur.execute("""
            UPDATE download_control 
            SET path = %s, 
                file_size = %s, 
                status = 'downloaded',
                created_at = CURRENT_TIMESTAMP
            WHERE name = %s AND ref = %s
        """, (file_path, file_size, file_name, ref))
        
        updated_rows = cur.rowcount
        conn.commit()
        
        if updated_rows > 0:
            print(f'Atualizado registro de download: {file_name}')
            return True
        else:
            print(f'Nenhum registro encontrado para atualizar: {file_name}')
            return False
            
    except Exception as e:
        conn.rollback()
        print(f'Erro ao atualizar registro de download: {str(e)}')
        raise e
    finally:
        close_connection(engine, conn, cur)


def update_extraction_success(file_id):
    """
    Atualiza o status para 'extracted' quando a extração é bem-sucedida.
    
    Args:
        file_id: ID único do arquivo
    
    Returns:
        bool: True se atualizou com sucesso
    """
    engine, conn, cur = create_connection()
    
    try:
        cur.execute("""
            UPDATE download_control 
            SET status = 'extracted'
            WHERE id = %s AND status = 'downloaded'
        """, (file_id,))
        
        updated_rows = cur.rowcount
        conn.commit()
        
        if updated_rows > 0:
            # Busca o nome do arquivo para exibir na mensagem
            cur.execute("SELECT name FROM download_control WHERE id = %s", (file_id,))
            result = cur.fetchone()
            file_name = result[0] if result else f"ID:{file_id}"
            print(f'Atualizado status de extração: {file_name}')
            return True
        else:
            return False
            
    except Exception as e:
        conn.rollback()
        print(f'Erro ao atualizar status de extração: {str(e)}')
        raise e
    finally:
        close_connection(engine, conn, cur)


def update_download_error(file_name, ref, error_message):
    """
    Atualiza o status para 'error' quando há falha no download.
    
    Args:
        file_name: Nome do arquivo
        ref: Referência (ano-mês)
        error_message: Mensagem de erro
    
    Returns:
        bool: True se atualizou com sucesso
    """
    engine, conn, cur = create_connection()
    
    try:
        cur.execute("""
            UPDATE download_control 
            SET status = 'error'
            WHERE name = %s AND ref = %s
        """, (file_name, ref))
        
        updated_rows = cur.rowcount
        conn.commit()
        
        if updated_rows > 0:
            print(f'Registrado erro no download: {file_name} - {error_message}')
            return True
        else:
            return False
            
    except Exception as e:
        conn.rollback()
        print(f'Erro ao atualizar status de erro: {str(e)}')
        raise e
    finally:
        close_connection(engine, conn, cur)


def get_download_status(ref=None):
    """
    Consulta o status dos downloads.
    
    Args:
        ref: Referência específica (ano-mês). Se None, retorna todos.
    
    Returns:
        list: Lista de registros com status dos downloads
    """
    engine, conn, cur = create_connection()
    
    try:
        if ref:
            cur.execute("""
                SELECT name, ref, path, status, file_size, created_at
                FROM download_control 
                WHERE ref = %s
                ORDER BY name
            """, (ref,))
        else:
            cur.execute("""
                SELECT name, ref, path, status, file_size, created_at
                FROM download_control 
                ORDER BY ref DESC, name
            """)
        
        results = cur.fetchall()
        
        # Converte para lista de dicionários
        columns = [desc[0] for desc in cur.description]
        return [dict(zip(columns, row)) for row in results]
        
    except Exception as e:
        print(f'Erro ao consultar status dos downloads: {str(e)}')
        return []
    finally:
        close_connection(engine, conn, cur)


def is_file_downloaded(file_name, ref):
    """
    Verifica se um arquivo já foi baixado com sucesso.
    
    Args:
        file_name: Nome do arquivo
        ref: Referência (ano-mês)
    
    Returns:
        bool: True se já foi baixado com sucesso
    """
    engine, conn, cur = create_connection()
    
    try:
        cur.execute("""
            SELECT path FROM download_control 
            WHERE name = %s AND ref = %s AND status = 'downloaded' AND path != ''
        """, (file_name, ref))
        
        result = cur.fetchone()
        
        if result and result[0]:
            # Verifica se o arquivo ainda existe no caminho
            if os.path.exists(result[0]):
                return True
            else:
                # Arquivo foi removido, atualiza status
                cur.execute("""
                    UPDATE download_control 
                    SET path = '', status = 'pending'
                    WHERE name = %s AND ref = %s
                """, (file_name, ref))
                conn.commit()
                return False
        
        return False
        
    except Exception as e:
        print(f'Erro ao verificar se arquivo foi baixado: {str(e)}')
        return False
    finally:
        close_connection(engine, conn, cur)


def get_pending_downloads(ref=None):
    """
    Retorna lista de arquivos que ainda precisam ser baixados.
    
    Args:
        ref: Referência específica (ano-mês). Se None, retorna todos.
    
    Returns:
        list: Lista de arquivos pendentes
    """
    engine, conn, cur = create_connection()
    
    try:
        if ref:
            cur.execute("""
                SELECT name, ref FROM download_control 
                WHERE ref = %s AND status = 'pending'
                ORDER BY name
            """, (ref,))
        else:
            cur.execute("""
                SELECT name, ref FROM download_control 
                WHERE status = 'pending'
                ORDER BY ref DESC, name
            """)
        
        results = cur.fetchall()
        return [{'name': row[0], 'year_month': row[1]} for row in results]
        
    except Exception as e:
        print(f'Erro ao buscar downloads pendentes: {str(e)}')
        return []
    finally:
        close_connection(engine, conn, cur)


def get_file_id(name, year_month):
    """
    Retrieve the unique ID of a file based on its name and year_month.
    
    Args:
        name: Name of the file
        year_month: Year and month of the file
    
    Returns:
        file_id: Unique identifier for the file
    """
    engine, conn, cur = create_connection()
    try:
        cur.execute("""
            SELECT id FROM download_control
            WHERE name = %s AND ref = %s
        """, (name, year_month))
        result = cur.fetchone()
        if result:
            return result[0]  # Return the file ID
        else:
            print(f'File not found: {name} ({year_month})')
            return None
    except Exception as e:
        print(f'Error fetching file ID: {str(e)}')
        raise e
    finally:
        close_connection(engine, conn, cur)


def register_extracted_file(name, year_month, path, related_at=None):
    """
    Register an extracted file in the control table.
    
    Args:
        name: Name of the extracted file
        year_month: Year and month of the parent .zip file
        path: Full path of the extracted file
        related_at: ID of the parent .zip file
    """
    engine, conn, cur = create_connection()
    try:
        cur.execute("""
            INSERT INTO download_control (name, ref, path, status, related_at)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (name, ref) DO NOTHING
        """, (name, year_month, path, 'extracted', related_at))
        conn.commit()
        print(f'Registered extracted file: {name}, related to file ID: {related_at}')
    except Exception as e:
        conn.rollback()
        print(f'Error registering extracted file: {str(e)}')
        raise e
    finally:
        close_connection(engine, conn, cur)
