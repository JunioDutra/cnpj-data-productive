from app.files.file_types import FileEntity
from app.utils import create_connection, close_connection


def list_files(ref=None, file_type=None) -> list[FileEntity]:
    engine, conn, cur = create_connection()
    try:
        query = """
            SELECT *
            FROM download_control
            WHERE 1 = 1
        """
        params = []

        if file_type is not None:
            query += " AND path LIKE %s"
            params.append(f"%.{file_type}")

        if ref is not None:
            query += " AND ref = %s"
            params.append(ref)

        query += " ORDER BY ref DESC, name ASC LIMIT 100"

        cur.execute(query, params)
        rows = cur.fetchall()

        files: list[FileEntity] = []
        for row in rows:
            files.append(FileEntity(
                id=row[0],
                created_at=row[1],
                path=row[2],
                name=row[3],
                ref=row[4],
                file_size=row[5],
                status=row[6],
                related_at=row[7],
            ))
        return files
    except Exception as e:
        print(f'Erro ao listar arquivos ZIP: {str(e)}')
        raise e
    finally:
        close_connection(engine, conn, cur)

def register_available_files(files_list):
    if not files_list:
        return 0
    
    engine, conn, cur = create_connection()
    inserted_count = 0
    
    try:
        for file_info in files_list:
            cur.execute("""
                SELECT id FROM download_control 
                WHERE name = %s AND ref = %s
            """, (file_info['name'], file_info['year_month']))
            
            existing = cur.fetchone()
            
            if not existing:
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

def get_file_id(name, year_month):
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

def update_download_success(file_name, ref, file_path, file_size=0):
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

def update_download_error(file_name, ref, error_message):
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

def update_extraction_success(file_id):
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

def register_extracted_file(name, year_month, path, related_at=None):
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

def update_download_error(file_name, ref, error_message):
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