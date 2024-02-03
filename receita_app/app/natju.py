import os
import time

import pandas as pd

from app.utils import to_sql, create_connection, filter_files, close_connection, initialize
from app.get_files import get_file_by_prefix

def run():
    get_file_by_prefix('NAT')
    path_extracted_files = os.getenv('EXTRACTED_FILES_PATH')
    filtered_files_natju = filter_files('NATJU')
    engine, conn, cur = create_connection()

    natju_insert_start = time.time()
    cur.execute('DROP TABLE IF EXISTS "natju";')
    conn.commit()

    for e in range(0, len(filtered_files_natju)):
        print('Trabalhando no arquivo: '+filtered_files_natju[e]+' [...]')
        try:
            del natju
        except:
            pass

        extracted_file_path = os.path.join(path_extracted_files, filtered_files_natju[e])
        natju = pd.DataFrame(columns=[1,2])
        natju = pd.read_csv(filepath_or_buffer=extracted_file_path, sep=';', skiprows=0, header=None, dtype='object', encoding='cp1252')

        natju = natju.reset_index()
        del natju['index']

        natju.columns = ['codigo', 'descricao']

        to_sql(natju, name='natju', con=engine, if_exists='append', index=False)
        print('Arquivo ' + filtered_files_natju[e] + ' inserido com sucesso no banco de dados!')

    try:
        del natju
    except:
        pass

    print('Arquivos de natju finalizados!')
    natju_insert_end = time.time()
    natju_Tempo_insert = round((natju_insert_end - natju_insert_start))
    print('Tempo de execução do processo de natureza jurídica (em segundos): ' + str(natju_Tempo_insert))

    close_connection(engine, conn, cur)

if __name__ == "__main__":
    initialize()
    run()
