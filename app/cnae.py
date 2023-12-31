import os
import time

import pandas as pd

from app.utils import to_sql, create_connection, filter_files, close_connection, initialize

def run():
    path_extracted_files = os.getenv('EXTRACTED_FILES_PATH')
    filtered_files_cnae = filter_files('CNAE')
    engine, conn, cur = create_connection()

    cnae_insert_start = time.time()

    cur.execute('DROP TABLE IF EXISTS "cnae";')
    conn.commit()

    for e in range(0, len(filtered_files_cnae)):
        print('Trabalhando no arquivo: '+filtered_files_cnae[e]+' [...]')
        try:
            del cnae
        except:
            pass

        extracted_file_path = os.path.join(path_extracted_files, filtered_files_cnae[e])
        cnae = pd.DataFrame(columns=[1,2])
        cnae = pd.read_csv(filepath_or_buffer=extracted_file_path, sep=';', skiprows=0, header=None, dtype='object', encoding='cp1252')

        cnae = cnae.reset_index()
        del cnae['index']

        cnae.columns = ['codigo', 'descricao']

        to_sql(cnae, name='cnae', con=engine, if_exists='append', index=False)
        print('Arquivo ' + filtered_files_cnae[e] + ' inserido com sucesso no banco de dados!')

    try:
        del cnae
    except:
        pass
    print('Arquivos de cnae finalizados!')
    cnae_insert_end = time.time()
    cnae_Tempo_insert = round((cnae_insert_end - cnae_insert_start))
    print('Tempo de execução do processo de cnae (em segundos): ' + str(cnae_Tempo_insert))

    close_connection(engine, conn, cur)

if __name__ == "__main__":
    initialize()
    run()
