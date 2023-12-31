import os
import time

import pandas as pd

from app.utils import to_sql, create_connection, filter_files, close_connection, initialize

def run():    
    path_extracted_files = os.getenv('EXTRACTED_FILES_PATH')
    filtered_files_munic = filter_files('MUNIC')
    engine, conn, cur = create_connection()

    munic_insert_start = time.time()
    cur.execute('DROP TABLE IF EXISTS "munic";')
    conn.commit()

    for e in range(0, len(filtered_files_munic)):
        print('Trabalhando no arquivo: '+filtered_files_munic[e]+' [...]')
        try:
            del munic
        except:
            pass

        extracted_file_path = os.path.join(path_extracted_files, filtered_files_munic[e])
        munic = pd.DataFrame(columns=[1,2])
        munic = pd.read_csv(filepath_or_buffer=extracted_file_path, sep=';', skiprows=0, header=None, dtype='object', encoding='cp1252')

        munic = munic.reset_index()
        del munic['index']

        munic.columns = ['codigo', 'descricao']

        to_sql(munic, name='munic', con=engine, if_exists='append', index=False)
        print('Arquivo ' + filtered_files_munic[e] + ' inserido com sucesso no banco de dados!')

    try:
        del munic
    except:
        pass

    print('Arquivos de munic finalizados!')
    munic_insert_end = time.time()
    munic_Tempo_insert = round((munic_insert_end - munic_insert_start))
    print('Tempo de execução do processo de municípios (em segundos): ' + str(munic_Tempo_insert))

    close_connection(engine, conn, cur)

if __name__ == "__main__":
    initialize()
    run()
