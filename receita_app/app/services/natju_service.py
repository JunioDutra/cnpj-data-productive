from app.files.file_types import FileEntity
from app.services.base_service import BaseService

class NatjuService(BaseService):
    entity_name = 'natju'
    columns = ['code', 'description']
    index_column = 'code'

    def process(self, file: FileEntity):
        print(f'Iniciando ++++ processamento do arquivo: {file.name}')
        
        super().process(file)