import os
import time

import pandas as pd

from app.utils import to_sql, create_connection, filter_files, create_index, close_connection, initialize

def run():
    path_extracted_files = os.getenv('EXTRACTED_FILES_PATH')
    filtered_files_empresa = filter_files('EMPRE')
    engine, conn, cur = create_connection()

    empresa_insert_start = time.time()
    cur.execute('DROP TABLE IF EXISTS "empresa";')
    conn.commit()

    for e in range(0, len(filtered_files_empresa)):
        print('Trabalhando no arquivo: '+filtered_files_empresa[e]+' [...]')
        try:
            del empresa
        except:
            pass

        empresa = pd.DataFrame(columns=[0, 1, 2, 3, 4, 5, 6])
        empresa_dtypes = {0: 'object', 1: 'object', 2: 'object', 3: 'object', 4: 'object', 5: 'object', 6: 'object'}
        extracted_file_path = os.path.join(path_extracted_files, filtered_files_empresa[e])

        empresa = pd.read_csv(filepath_or_buffer=extracted_file_path,
                            sep=';',
                            skiprows=0,
                            header=None,
                            dtype=empresa_dtypes,
                            encoding='latin-1',
        )

        empresa = empresa.reset_index()
        del empresa['index']

        empresa.columns = ['cnpj_basico', 'razao_social', 'natureza_juridica', 'qualificacao_responsavel', 'capital_social', 'porte_empresa', 'ente_federativo_responsavel']

        empresa['capital_social'] = empresa['capital_social'].apply(lambda x: x.replace(',','.'))
        empresa['capital_social'] = empresa['capital_social'].astype(float)

        to_sql(empresa, name='empresa', con=engine, if_exists='append', index=False)
        print('Arquivo ' + filtered_files_empresa[e] + ' inserido com sucesso no banco de dados!')
    try:
        del empresa
    except:
        pass

    print('Arquivos de empresa finalizados!')
    empresa_insert_end = time.time()
    empresa_Tempo_insert = round((empresa_insert_end - empresa_insert_start))
    print('Tempo de execução do processo de empresa (em segundos): ' + str(empresa_Tempo_insert))

    close_connection(engine, conn, cur)
    create_index('empresa', 'cnpj_basico')

if __name__ == "__main__":
    initialize()
    run()