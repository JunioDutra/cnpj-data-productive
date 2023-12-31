import os
import time

import pandas as pd

from app.utils import to_sql, create_connection, filter_files, close_connection, initialize

def run():
    path_extracted_files = os.getenv('EXTRACTED_FILES_PATH')
    filtered_files_moti = filter_files('MOTI')
    engine, conn, cur = create_connection()

    moti_insert_start = time.time()

    cur.execute('DROP TABLE IF EXISTS "moti";')
    conn.commit()

    for e in range(0, len(filtered_files_moti)):
        print('Trabalhando no arquivo: '+filtered_files_moti[e]+' [...]')
        try:
            del moti
        except:
            pass

        extracted_file_path = os.path.join(path_extracted_files, filtered_files_moti[e])
        moti = pd.DataFrame(columns=[1,2])
        moti = pd.read_csv(filepath_or_buffer=extracted_file_path, sep=';', skiprows=0, header=None, dtype='object', encoding='cp1252')

        moti = moti.reset_index()
        del moti['index']

        moti.columns = ['codigo', 'descricao']

        to_sql(moti, name='moti', con=engine, if_exists='append', index=False)
        print('Arquivo ' + filtered_files_moti[e] + ' inserido com sucesso no banco de dados!')

    try:
        del moti
    except:
        pass

    print('Arquivos de moti finalizados!')
    moti_insert_end = time.time()
    moti_Tempo_insert = round((moti_insert_end - moti_insert_start))
    print('Tempo de execução do processo de motivos da situação atual (em segundos): ' + str(moti_Tempo_insert))

    close_connection(engine, conn, cur)

if __name__ == "__main__":
    initialize()
    run()
