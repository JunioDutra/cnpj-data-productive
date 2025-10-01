import os
import time

import pandas as pd

from app.files.file_types import FileEntity
from app.utils import to_sql, create_connection, filter_files, close_connection
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

def process(file: FileEntity):
    try:
        engine, conn, cur = create_connection()

        cnae_insert_start = time.time()
        
        date = datetime.strptime(file.ref, '%Y-%m').date()
        next_date = (date + relativedelta(months=1)).replace(day=1)
        
        print('Criando partição cnae_'+file.ref+' [...]')
        print(f'VALUES FROM ({date}) TO ({next_date})')

        sql = f'''
                CREATE TABLE IF NOT EXISTS cnae_{file.ref.replace("-", "_")}
                PARTITION OF cnae
                FOR VALUES FROM ('{date}') TO ('{next_date}');
                '''
        cur.execute(sql)
        conn.commit()
        
        print('Trabalhando no arquivo: '+file.path+' [...]')

        try:
            del cnae
        except:
            pass

        cnae = pd.DataFrame(columns=[1,2])
        cnae = pd.read_csv(filepath_or_buffer=file.path, sep=';', skiprows=0, header=None, dtype='object', encoding='cp1252')

        cnae = cnae.reset_index()
        del cnae['index']

        cnae.columns = ['code', 'description']
        cnae['download_control_id'] = file.id
        cnae['effective_date'] = date
        

        to_sql(cnae, name='cnae', con=engine, if_exists='append', index=False)
        print('Arquivo ' + file.path + ' inserido com sucesso no banco de dados!')

        cur.execute(f"CREATE INDEX CONCURRENTLY ON cnae_{file.ref.replace('-', '_')} (code, effective_date);")
        
        try:
            del cnae
        except:
            pass

        print('Arquivos de cnae finalizados!')
        
        cnae_insert_end = time.time()
        cnae_Tempo_insert = round((cnae_insert_end - cnae_insert_start))
        print('Tempo de execução do processo de cnae (em segundos): ' + str(cnae_Tempo_insert))

        close_connection(engine, conn, cur)
    except Exception as e:
        print('Erro ao inserir o arquivo ' + file.path + ' no banco de dados: ' + str(e))

