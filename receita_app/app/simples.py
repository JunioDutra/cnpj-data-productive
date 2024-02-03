import os
import time

import pandas as pd

from app.utils import to_sql, create_connection, filter_files, create_index, close_connection, initialize
from app.get_files import get_file_by_prefix

def run():
    get_file_by_prefix('SIMPLES')
    
    path_extracted_files = os.getenv('EXTRACTED_FILES_PATH')
    filtered_files_simples = filter_files('SIMPLES')
    engine, conn, cur = create_connection()

    simples_insert_start = time.time()
    cur.execute('DROP TABLE IF EXISTS "simples";')
    conn.commit()

    for e in range(0, len(filtered_files_simples)):
        print('Trabalhando no arquivo: '+filtered_files_simples[e]+' [...]')
        try:
            del simples
        except:
            pass

        print('Lendo o arquivo ' + filtered_files_simples[e]+' [...]')
        extracted_file_path = os.path.join(path_extracted_files, filtered_files_simples[e])

        simples_lenght = sum(1 for line in open(extracted_file_path, "r"))
        print('Linhas no arquivo do Simples '+ filtered_files_simples[e] +': '+str(simples_lenght))

        tamanho_das_partes = 100000
        partes = round(simples_lenght / tamanho_das_partes)
        nrows = tamanho_das_partes
        skiprows = 0

        print('Este arquivo será dividido em ' + str(partes) + ' partes para inserção no banco de dados')

        for i in range(0, partes):
            print('Iniciando a parte ' + str(i+1) + ' [...]')
            simples = pd.DataFrame(columns=[1,2,3,4,5,6])

            simples = pd.read_csv(filepath_or_buffer=extracted_file_path,
                                sep=';',
                                nrows=nrows,
                                skiprows=skiprows,
                                header=None,
                                dtype='object',
                                encoding='latin-1',
            )

            simples = simples.reset_index()
            del simples['index']

            simples.columns = ['cnpj_basico',
                            'opcao_pelo_simples',
                            'data_opcao_simples',
                            'data_exclusao_simples',
                            'opcao_mei',
                            'data_opcao_mei',
                            'data_exclusao_mei']

            skiprows = skiprows+nrows

            to_sql(simples, size=tamanho_das_partes, name='simples', con=engine, if_exists='append', index=False)
            print('Arquivo ' + filtered_files_simples[e] + ' inserido com sucesso no banco de dados! - Parte '+ str(i+1))

            try:
                del simples
            except:
                pass

    try:
        del simples
    except:
        pass

    print('Arquivos do simples finalizados!')
    simples_insert_end = time.time()
    simples_Tempo_insert = round((simples_insert_end - simples_insert_start))
    print('Tempo de execução do processo do Simples Nacional (em segundos): ' + str(simples_Tempo_insert))

    close_connection(engine, conn, cur)
    create_index('simples', 'cnpj_basico')

if __name__ == "__main__":
    initialize()
    run()
