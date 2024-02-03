import os
import time

import pandas as pd

from app.utils import to_sql, create_connection, filter_files, create_index, close_connection, initialize
from app.get_files import get_file_by_prefix

def run():
    get_file_by_prefix('ESTABELE')
    
    path_extracted_files = os.getenv('EXTRACTED_FILES_PATH')
    filtered_files_estabelecimento = filter_files('ESTABELE')

    engine, conn, cur = create_connection()

    estabelecimento_insert_start = time.time()

    cur.execute('DROP TABLE IF EXISTS "estabelecimento";')
    conn.commit()

    for e in range(0, len(filtered_files_estabelecimento)):
        print('Trabalhando no arquivo: '+filtered_files_estabelecimento[e]+' [...]')
        try:
            del estabelecimento
        except:
            pass

        estabelecimento = pd.DataFrame(columns=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28])
        extracted_file_path = os.path.join(path_extracted_files, filtered_files_estabelecimento[e])

        estabelecimento = pd.read_csv(filepath_or_buffer=extracted_file_path,
                            sep=';',
                            skiprows=0,
                            header=None,
                            dtype='object',
                            encoding='latin-1',
        )

        estabelecimento = estabelecimento.reset_index()
        del estabelecimento['index']

        estabelecimento.columns = ['cnpj_basico',
                                'cnpj_ordem',
                                'cnpj_dv',
                                'identificador_matriz_filial',
                                'nome_fantasia',
                                'situacao_cadastral',
                                'data_situacao_cadastral',
                                'motivo_situacao_cadastral',
                                'nome_cidade_exterior',
                                'pais',
                                'data_inicio_atividade',
                                'cnae_fiscal_principal',
                                'cnae_fiscal_secundaria',
                                'tipo_logradouro',
                                'logradouro',
                                'numero',
                                'complemento',
                                'bairro',
                                'cep',
                                'uf',
                                'municipio',
                                'ddd_1',
                                'telefone_1',
                                'ddd_2',
                                'telefone_2',
                                'ddd_fax',
                                'fax',
                                'correio_eletronico',
                                'situacao_especial',
                                'data_situacao_especial']

        to_sql(estabelecimento, name='estabelecimento', con=engine, if_exists='append', index=False)
        print('Arquivo ' + filtered_files_estabelecimento[e] + ' inserido com sucesso no banco de dados!')

    try:
        del estabelecimento
    except:
        pass
    print('Arquivos de estabelecimento finalizados!')
    estabelecimento_insert_end = time.time()
    estabelecimento_Tempo_insert = round((estabelecimento_insert_end - estabelecimento_insert_start))
    print('Tempo de execução do processo de estabelecimento (em segundos): ' + str(estabelecimento_Tempo_insert))

    close_connection(engine, conn, cur)
    create_index('estabelecimento', 'cnpj_basico')
    
if __name__ == "__main__":
    initialize()
    run()