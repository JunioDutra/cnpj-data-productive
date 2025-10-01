import time
import logging

import pandas as pd

from datetime import datetime
from dateutil.relativedelta import relativedelta
from app.files.file_types import FileEntity
from app.utils import to_sql, create_connection, close_connection
from psycopg2 import sql

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseService:
    entity_name: str
    columns: list[str]
    index_column: str
    
    def process(self, file: FileEntity):
        try:
            engine, conn, cur = create_connection()

            insert_start = time.time()

            ref_date = self.create_partition(file.ref, conn, cur)

            logger.info(f'Trabalhando no arquivo: {file.path} [...]')

            dataframe = self.initialize_dataframe(file, ref_date)
            to_sql(dataframe, name=self.entity_name, con=engine, if_exists='append', index=False)

            logger.info(f'Arquivo {file.path} inserido com sucesso no banco de dados!')
            insert_duration = round((time.time() - insert_start))
            logger.info(f'Tempo de execução do processo {file.path} (em segundos): {insert_duration}')

            try:
                self.create_partition_index(file.ref, conn)
            except Exception as ie:
                logger.warning(f'Falha ao criar índice para partição {self.entity_name}_{file.ref.replace("-", "_")}: {ie}')

            close_connection(engine, conn, cur)
        except Exception as e:
            logger.error(f'Erro ao inserir o arquivo {file.path} no banco de dados: {str(e)}')

    def create_partition(self, ref: str, conn, cur):
        date = datetime.strptime(ref, '%Y-%m').date()
        next_date = (date + relativedelta(months=1)).replace(day=1)

        logger.info(f'Criando partição {self.entity_name}_{ref} [...]')
        logger.info(f'VALUES FROM ({date}) TO ({next_date})')

        sql = f'''
                CREATE TABLE IF NOT EXISTS {self.entity_name}_{ref.replace("-", "_")}
                PARTITION OF {self.entity_name}
                FOR VALUES FROM ('{date}') TO ('{next_date}');
                '''
        cur.execute(sql)
        conn.commit()
        return date

    def initialize_dataframe(self, file, ref_date):
        dataframe = pd.DataFrame(columns=list(range(1, len(self.columns) + 1)))
        dataframe = pd.read_csv(filepath_or_buffer=file.path, sep=';', skiprows=0, header=None, dtype='object', encoding='cp1252')

        dataframe = dataframe.reset_index()
        del dataframe['index']

        dataframe.columns = self.columns
        dataframe['download_control_id'] = file.id
        dataframe['effective_date'] = ref_date
        return dataframe

    def create_partition_index(self, ref: str, conn):
        table_name = f"{self.entity_name}_{ref.replace('-', '_')}"
        index_name = f"{table_name}_{self.index_column}_effective_date_idx"

        logger.info(f'Criando índice {index_name} em {table_name} ({self.index_column}, effective_date) ...')
        
        with conn.cursor() as c:
            create_idx_sql = sql.SQL(
                "CREATE INDEX IF NOT EXISTS {idx} ON {tbl} ({col1}, {col2});"
            ).format(
                idx=sql.Identifier(index_name),
                tbl=sql.Identifier(table_name),
                col1=sql.Identifier(self.index_column),
                col2=sql.Identifier('effective_date'),
            )
            c.execute(create_idx_sql)
        logger.info(f'Índice {index_name} criado (ou já existente).')