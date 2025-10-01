from datetime import datetime

import os
import re
import wget
import urllib
import zipfile
import bs4 as bs
import requests

from app.services import cnae_service
from app.services.natju_service import NatjuService
from app.files import files_repository
from concurrent.futures import ThreadPoolExecutor

from app.files.file_types import FileEntity

def list_files(ref=None, file_type=None):
    if not ref:
        current_date = datetime.now()
        ref = current_date.strftime('%Y-%m')
    return [item._asdict() for item in files_repository.list_files(ref, file_type=file_type)]

def fetch(year_month):
    """Get list of available files from Receita Federal for a specific year-month"""
    if not year_month:
        current_date = datetime.now()
        year_month = current_date.strftime('%Y-%m')

    dados_rf = f'https://arquivos.receitafederal.gov.br/dados/cnpj/dados_abertos_cnpj/{year_month}/'
    
    try:
        raw_html = urllib.request.urlopen(dados_rf)
        raw_html = raw_html.read()

        page_items = bs.BeautifulSoup(raw_html, 'lxml')
        html_str = str(page_items)

        files = []
        text = '.zip'
        for m in re.finditer(text, html_str):
            i_start = m.start()-40
            i_end = m.end()
            i_loc = html_str[i_start:i_end].find('href=')+6
            file_name = html_str[i_start+i_loc:i_end]
            if not file_name.find('.zip">') > -1:
                files.append({
                    'name': file_name,
                    'url': dados_rf + file_name,
                    'year_month': year_month
                })
        return files
    except urllib.error.URLError:
        print(f'No files found for year-month: {year_month}')
        return []
    
def download_files(files):
    files_repository.register_available_files(files)

    print(f'\nArquivos que serão baixados ({len(files)} de {len(files)}):')
    for i, file in enumerate(files, 1):
        print(f'{i} - {file["name"]}')

    with ThreadPoolExecutor() as executor:
        futures = []
        skip_keywords = []
        
        for file in files:
            if any(keyword in str.lower(file['name']) for keyword in skip_keywords):
                print(f'Skipping file: {file["name"]}')
                continue
            
            print(f'Preparando para baixar arquivo: {file["name"]}')
            futures.append(
                executor.submit(
                    process_download, 
                    file
                )
            )
        
        for future in futures:
            future.result()

def process_download(file_info):
    try:
        output_files = os.getenv('OUTPUT_FILES_PATH')
        extracted_files = os.getenv('EXTRACTED_FILES_PATH')
        
        download_directory = os.path.join(output_files, file_info['year_month'])
        if not os.path.exists(download_directory):
            os.makedirs(download_directory)
            
        extracted_directory = os.path.join(extracted_files, file_info['year_month'])
        if not os.path.exists(extracted_directory):
            os.makedirs(extracted_directory)

        file_name = os.path.join(download_directory, file_info['name'])
        file_id = files_repository.get_file_id(file_info['name'], file_info['year_month'])
        download_file(file_info['url'], output_files, file_name, file_info)
        
        if os.path.exists(file_name):
            print(f'Descompactando arquivo: {file_info["name"]}')
            with zipfile.ZipFile(file_name, 'r') as zip_ref:
                zip_ref.extractall(extracted_directory)
                extracted_file_names = zip_ref.namelist()
            
            print(f'Arquivo descompactado com sucesso! {file_info["name"]}')
            
            files_repository.update_extraction_success(file_id)
            
            for extracted_file in extracted_file_names:
                extracted_file_path = os.path.join(extracted_directory, extracted_file)
                files_repository.register_extracted_file(
                    extracted_file,
                    file_info['year_month'],
                    extracted_file_path,
                    related_at=file_id
                )
    except Exception as e:
        print(f'Error processing file {file_info["name"]}: {str(e)}')
        files_repository.update_download_error(
            file_info['name'], 
            file_info['year_month'], 
            str(e)
        )

def download_file(url, output_files, file_name, file_info):
    try:
        if check_diff(url, file_name):
            print(f'Arquivo não encontrado ou diferente, baixando... {file_info["name"]}')
            wget.download(url, out=output_files)
            
            if os.path.exists(file_name):
                file_size = os.path.getsize(file_name)
                print(f'Arquivo baixado com sucesso! {file_info["name"]} ({file_size} bytes)')
                
                files_repository.update_download_success(
                    file_info['name'], 
                    file_info['year_month'], 
                    file_name, 
                    file_size
                )
            else:
                files_repository.update_download_error(
                    file_info['name'], 
                    file_info['year_month'], 
                    'Arquivo não encontrado após download'
                )
        else:
            if os.path.exists(file_name):
                file_size = os.path.getsize(file_name)
                files_repository.update_download_success(
                    file_info['name'], 
                    file_info['year_month'], 
                    file_name, 
                    file_size
                )
    except Exception as e:
        print(f'Erro no download do arquivo {file_info["name"]}: {str(e)}')
        files_repository.update_download_error(
            file_info['name'], 
            file_info['year_month'], 
            str(e)
        )

def check_diff(url, file_name):
    if not os.path.isfile(file_name):
        return True

    response = requests.head(url)
    new_size = int(response.headers.get('content-length', 0))
    old_size = os.path.getsize(file_name)
    if new_size != old_size:
        os.remove(file_name)
        return True

    return False

def process_files(files: list[FileEntity]):
    with ThreadPoolExecutor() as executor:
        for file in files:

            if file.path.find('.CNAECSV') != -1:
                print(f'Processando arquivo: {file.name}')

                executor.submit(
                    cnae_service.process,
                    file
                )
            
            if file.path.find('.NATJUCSV') != -1:
                print(f'Processando arquivo: {file.name}')

                executor.submit(
                    NatjuService().process,
                    file
                )

            continue
