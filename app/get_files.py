import re
import os
import wget
import zipfile
import requests
import bs4 as bs
import urllib.request

import app.utils as utils

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

def run():
    dados_rf = 'http://200.152.38.155/CNPJ/'
    output_files = os.getenv('OUTPUT_FILES_PATH')
    extracted_files = os.getenv('EXTRACTED_FILES_PATH')

    raw_html = urllib.request.urlopen(dados_rf)
    raw_html = raw_html.read()

    page_items = bs.BeautifulSoup(raw_html, 'lxml')
    html_str = str(page_items)

    Files = []
    text = '.zip'
    for m in re.finditer(text, html_str):
        i_start = m.start()-40
        i_end = m.end()
        i_loc = html_str[i_start:i_end].find('href=')+6
        Files.append(html_str[i_start+i_loc:i_end])

    Files_clean = []
    for i in range(len(Files)):
        if not Files[i].find('.zip">') > -1:
            Files_clean.append(Files[i])

    try:
        del Files
    except:
        pass

    Files = Files_clean

    print('Arquivos que serão baixados:')

    i_f = 0
    for f in Files:
        i_f += 1
        print(str(i_f) + ' - ' + f)

    i_l = 0
    for l in Files:
        i_l += 1
        print('Baixando arquivo:')
        print(str(i_l) + ' - ' + l)
        url = dados_rf+l
        file_name = os.path.join(output_files, l)
        if check_diff(url, file_name):
            print(f'Arquivo não encontrado ou diferente, baixando... {file_name}')
            wget.download(url, out=output_files)
            print(f'Arquivo baixado com sucesso! {file_name}')

    Layout = 'https://www.gov.br/receitafederal/pt-br/assuntos/orientacao-tributaria/cadastros/consultas/arquivos/NOVOLAYOUTDOSDADOSABERTOSDOCNPJ.pdf'
    print('Baixando layout:')
    wget.download(Layout, out=output_files)
    print('Layout baixado com sucesso!')

    i_l = 0
    for l in Files:
        try:
            i_l += 1
            print('Descompactando arquivo:')
            print(str(i_l) + ' - ' + l)
            full_path = os.path.join(output_files, l)
            with zipfile.ZipFile(full_path, 'r') as zip_ref:
                zip_ref.extractall(extracted_files)
        except:
            pass
    
    print('Arquivos descompactados com sucesso!')
        
if __name__ == "__main__":
    utils.initialize()
    run()