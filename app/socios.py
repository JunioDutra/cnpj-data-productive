import os
import time

import pandas as pd

from app.utils import to_sql, create_connection, filter_files, create_index, close_connection, initialize

def run():
    path_extracted_files = os.getenv('EXTRACTED_FILES_PATH')
    filtered_files_socios = filter_files('SOCIO')
    engine, conn, cur = create_connection()

    socios_insert_start = time.time()
    cur.execute('DROP TABLE IF EXISTS "socios";')
    conn.commit()

    for e in range(0, len(filtered_files_socios)):
        print('Trabalhando no arquivo: '+filtered_files_socios[e]+' [...]')
        try:
            del socios
        except:
            pass

        extracted_file_path = os.path.join(path_extracted_files, filtered_files_socios[e])
        socios = pd.DataFrame(columns=[1,2,3,4,5,6,7,8,9,10,11])
        socios = pd.read_csv(filepath_or_buffer=extracted_file_path,
                            sep=';',
                            #nrows=100,
                            skiprows=0,
                            header=None,
                            dtype='object',
                            encoding='latin-1',
        )

        socios = socios.reset_index()
        del socios['index']

        socios.columns = ['cnpj_basico',
                        'identificador_socio',
                        'nome_socio_razao_social',
                        'cpf_cnpj_socio',
                        'qualificacao_socio',
                        'data_entrada_sociedade',
                        'pais',
                        'representante_legal',
                        'nome_do_representante',
                        'qualificacao_representante_legal',
                        'faixa_etaria']

        to_sql(socios, name='socios', con=engine, if_exists='append', index=False)
        print('Arquivo ' + filtered_files_socios[e] + ' inserido com sucesso no banco de dados!')

    try:
        del socios
    except:
        pass

    print('Arquivos de socios finalizados!')
    socios_insert_end = time.time()
    socios_Tempo_insert = round((socios_insert_end - socios_insert_start))
    print('Tempo de execução do processo de sócios (em segundos): ' + str(socios_Tempo_insert))

    close_connection(engine, conn, cur)
    create_index('socios', 'cnpj_basico')

if __name__ == "__main__":
    initialize()
    run()