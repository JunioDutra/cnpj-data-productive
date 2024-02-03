import sys
import os
import psycopg2

from sqlalchemy import create_engine

def create_connection():
    user=os.getenv('DB_USER')
    passw=os.getenv('DB_PASSWORD')
    host=os.getenv('DB_HOST')
    port=os.getenv('DB_PORT')
    database=os.getenv('DB_NAME')

    engine = create_engine(f'postgresql://{user}:{passw}@{host}:{port}/{database}')
    conn = psycopg2.connect(f'dbname={database} user={user} host={host} port={port} password={passw}')
    cur = conn.cursor()
    return engine, conn, cur

def to_sql(dataframe, size=10000, **kwargs):
    total = len(dataframe)
    name = kwargs.get('name')

    def chunker(df):
        return (df[i:i + size] for i in range(0, len(df), size))

    for i, df in enumerate(chunker(dataframe)):
        df.to_sql(chunksize=size, **kwargs)
        index = i * size
        percent = (index * 100) / total
        progress = f'{name} {percent:.2f}% {index:0{len(str(total))}}/{total}'
        sys.stdout.write(f'\r{progress}')

def filter_files(prefix):
    extracted_files = os.getenv('EXTRACTED_FILES_PATH')

    Items = [name for name in os.listdir(extracted_files) if name.endswith('')]

    arquivos = []

    for i in range(len(Items)):
        if Items[i].find(prefix) > -1:
            arquivos.append(Items[i])
        else:
            pass
    
    return arquivos

def create_index(table, column):
    engine, conn, cur = create_connection()
    cur.execute(f'CREATE INDEX {table}_{column}_idx ON {table} ({column});')
    conn.commit()
    
    close_connection(engine, conn, cur)
    
    print(f'Índice {table}_{column}_idx criado com sucesso!')
    
def close_connection(engine, conn, cur):
    cur.close()
    conn.close()
    engine.dispose()
    print('Conexão encerrada com sucesso!')
    
def makedirs(path):
    if not os.path.exists(path):
        os.makedirs(path)

def initialize():
    try:
        output_files = os.getenv('OUTPUT_FILES_PATH')
        makedirs(output_files)

        extracted_files = os.getenv('EXTRACTED_FILES_PATH')
        makedirs(extracted_files)

        print('Diretórios definidos: \n' +
            'output_files: ' + str(output_files)  + '\n' +
            'extracted_files: ' + str(extracted_files))
    except:
        pass
        print('Erro na definição dos diretórios, verifique o arquivo ".env" ou o local informado do seu arquivo de configuração.')