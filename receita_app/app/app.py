import argparse

import app.get_files as get_files
import app.empresa as empresa
import app.estabelecimentos as estabelecimentos
import app.socios as socios
import app.simples as simples
import app.cnae as cnae
import app.moti as moti
import app.munic as munic
import app.natju as natju
import app.pais as pais
import app.quals as quals
import app.webserver as webserver

from app.utils import initialize

def process_data():
    initialize()

    # get_files.run()

    cnae.run()
    moti.run()
    munic.run()
    natju.run()
    pais.run()
    quals.run()

    empresa.run()
    estabelecimentos.run()
    socios.run()
    simples.run()

    print("""Processo 100% finalizado! Você já pode usar seus dados no BD!
        - Desenvolvido por: JunioDBL
        - Contribua com esse projeto aqui: https://github.com/xpto
    """)

def main():
    parser = argparse.ArgumentParser(description='CNPJ Data Processing and API Server')
    parser.add_argument('--server-only', action='store_true', help='Run only the web server')
    parser.add_argument('--port', type=int, default=5000, help='Port for the web server')
    args = parser.parse_args()

    if args.server_only:
        initialize()
        webserver.start_server(port=args.port)
    else:
        process_data()
        # Start web server after processing
        webserver.start_server(port=args.port)

if __name__ == "__main__":
    main()