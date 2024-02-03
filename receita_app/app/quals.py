import os
import time

import pandas as pd

from app.utils import to_sql, create_connection, filter_files, close_connection,  initialize
from app.get_files import get_file_by_prefix

def run():
    get_file_by_prefix('QUAL')
    path_extracted_files = os.getenv('EXTRACTED_FILES_PATH')
    filtered_files_quals = filter_files('QUALS')
    engine, conn, cur = create_connection()

    quals_insert_start = time.time()
    cur.execute('DROP TABLE IF EXISTS "quals";')
    conn.commit()

    for e in range(0, len(filtered_files_quals)):
        print('Trabalhando no arquivo: '+filtered_files_quals[e]+' [...]')
        try:
            del quals
        except:
            pass

        extracted_file_path = os.path.join(path_extracted_files, filtered_files_quals[e])
        quals = pd.DataFrame(columns=[1,2])
        quals = pd.read_csv(filepath_or_buffer=extracted_file_path, sep=';', skiprows=0, header=None, dtype='object', encoding='cp1252')

        quals = quals.reset_index()
        del quals['index']

        quals.columns = ['codigo', 'descricao']

        to_sql(quals, name='quals', con=engine, if_exists='append', index=False)
        print('Arquivo ' + filtered_files_quals[e] + ' inserido com sucesso no banco de dados!')

    try:
        del quals
    except:
        pass

    print('Arquivos de quals finalizados!')
    quals_insert_end = time.time()
    quals_Tempo_insert = round((quals_insert_end - quals_insert_start))
    print('Tempo de execução do processo de qualificação de sócios (em segundos): ' + str(quals_Tempo_insert))

    close_connection(engine, conn, cur)

if __name__ == "__main__":
    initialize()
    run()
