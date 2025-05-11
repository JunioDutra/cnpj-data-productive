import re
import os
import wget
import zipfile
import requests
import bs4 as bs
from datetime import datetime
import urllib.request
from concurrent.futures import ThreadPoolExecutor
import app.utils as utils

def get_available_files(year_month=None):
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

def download_file(url, output_files, file_name):
    if check_diff(url, file_name):
        print(f'Arquivo não encontrado ou diferente, baixando... {file_name}')
        wget.download(url, out=output_files)
        print(f'Arquivo baixado com sucesso! {file_name}')

def process_download(file_info, output_files, extracted_files):
    """Download and extract a single file"""
    try:
        file_name = os.path.join(output_files, file_info['name'])
        download_file(file_info['url'], output_files, file_name)
        
        # Extract file if download was successful
        if os.path.exists(file_name):
            print(f'Descompactando arquivo: {file_info["name"]}')
            with zipfile.ZipFile(file_name, 'r') as zip_ref:
                zip_ref.extractall(extracted_files)
            print(f'Arquivo descompactado com sucesso! {file_info["name"]}')
    except Exception as e:
        print(f'Error processing file {file_info["name"]}: {str(e)}')

def run():
    env_date = os.getenv('DOWNLOAD_DATE')
    output_files = os.getenv('OUTPUT_FILES_PATH')
    extracted_files = os.getenv('EXTRACTED_FILES_PATH')

    # Get list of available files
    files = get_available_files(env_date)
    
    if not files:
        print('No files found to download')
        return

    print('Arquivos que serão baixados:')
    for i, file in enumerate(files, 1):
        print(f'{i} - {file["name"]}')

    # Download and extract files in parallel
    with ThreadPoolExecutor() as executor:
        futures = []
        skip_keywords = []  # Add keywords to skip specific files if needed
        
        for file in files:
            if any(keyword in str.lower(file['name']) for keyword in skip_keywords):
                print(f'Skipping file: {file["name"]}')
                continue
            
            print(f'Preparando para baixar arquivo: {file["name"]}')
            futures.append(
                executor.submit(
                    process_download, 
                    file, 
                    output_files, 
                    extracted_files
                )
            )
        
        for future in futures:
            future.result()

def get_file_by_prefix(prefix):
    env_date = os.getenv('DOWNLOAD_DATE')
    output_files = os.getenv('OUTPUT_FILES_PATH')
    extracted_files = os.getenv('EXTRACTED_FILES_PATH')
    
    # Get list of available files
    files = get_available_files(env_date)
    
    if not files:
        return None
        
    # Filter files by prefix
    matching_files = [
        file for file in files 
        if prefix.lower() in file['name'].lower()
    ]
    
    print(f'Found {len(matching_files)} files matching prefix "{prefix}":')
    for i, file in enumerate(matching_files, 1):
        print(f'{i} - {file["name"]}')
        
    # Download and extract matching files
    for file in matching_files:
        process_download(file, output_files, extracted_files)

    return None

if __name__ == "__main__":
    run()