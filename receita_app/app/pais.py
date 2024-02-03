import os
import time

import pandas as pd

from app.utils import to_sql, create_connection, filter_files, close_connection, initialize
from app.get_files import get_file_by_prefix

def run():
    get_file_by_prefix('PAIS')
    path_extracted_files = os.getenv('EXTRACTED_FILES_PATH')
    filtered_files_pais = filter_files('PAIS')
    engine, conn, cur = create_connection()

    pais_insert_start = time.time()
    cur.execute('DROP TABLE IF EXISTS "pais";')
    conn.commit()

    for e in range(0, len(filtered_files_pais)):
        print('Trabalhando no arquivo: '+filtered_files_pais[e]+' [...]')
        try:
            del pais
        except:
            pass

        extracted_file_path = os.path.join(path_extracted_files, filtered_files_pais[e])
        pais = pd.DataFrame(columns=[1,2])
        pais = pd.read_csv(filepath_or_buffer=extracted_file_path, sep=';', skiprows=0, header=None, dtype='object', encoding='cp1252')

        pais = pais.reset_index()
        del pais['index']

        pais.columns = ['codigo', 'descricao']

        to_sql(pais, name='pais', con=engine, if_exists='append', index=False)
        print('Arquivo ' + filtered_files_pais[e] + ' inserido com sucesso no banco de dados!')

    try:
        del pais
    except:
        pass

    print('Arquivos de pais finalizados!')
    pais_insert_end = time.time()
    pais_Tempo_insert = round((pais_insert_end - pais_insert_start))
    print('Tempo de execução do processo de país (em segundos): ' + str(pais_Tempo_insert))

    close_connection(engine, conn, cur)

if __name__ == "__main__":
    initialize()
    run()
