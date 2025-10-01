List Online
```bash
curl -X GET "http://localhost:5000/files/fetch?year=2025&month=08"
```

Download
```bash
curl -X POST http://localhost:5000/files/download -H "Content-Type: application/json" -d '{"files": [{"name": "Cnaes.zip", "url": "https://arquivos.receitafederal.gov.br/dados/cnpj/dados_abertos_cnpj/2025-08/Cnaes.zip", "year_month": "2025-08"}]}'
```

```bash
 curl -X POST http://localhost:5000/files/download -H "Content-Type: application/json" -d '{"files": [{"name": "Naturezas.zip","url": "https://arquivos.receitafederal.gov.br/dados/cnpj/dados_abertos_cnpj/2025-08/Naturezas.zip","year_month": "2025-08"}]}'
```

Process
```bash
curl -v -X POST "http://localhost:5000/files/process" -H "Content-Type: application/json" -d '{"files": [{"created_at": "Sat, 13 Sep 2025 15:18:18 GMT", "file_size": 0, "id": 2, "name": "F.K03200$Z.D50809.CNAECSV", "path": "./assets/extracted/F.K03200$Z.D50809.CNAECSV", "ref": "2025-08", "related_at": 1, "status": "extracted"}] }'
```

```bash
curl -v -X POST "http://localhost:5000/files/process" -H "Content-Type: application/json" -d '{"files": [{"id": 2,"name": "F.K03200$Z.D50809.NATJUCSV","path": "./assets/extracted/F.K03200$Z.D50809.NATJUCSV","ref": "2025-08"}]}'
```