## How to run
### run this to import with one instance
```shell
docker compose up postgrest postgres database_admin app
```

### or run in two steps to get better performance

#### step one, get files
```shell
docker compose up -d postgrest postgres database_admin
docker compose up app_getfiles
```

#### step two, import data
```shell
docker compose up app_empresa app_estabelecimentos app_socios app_simples app_cnae app_moti app_munic app_natju app_pais app_quals
```

### app list
- [x] [Rest api](http://localhost:3000/)
- [x] [PgAdmin](http://localhost:5050/)

### links
- [x] [Postgrest](https://postgrest.org/en/v7.0.0/)
- [x] [Postgres](https://www.postgresql.org/)
- [x] [Docker](https://www.docker.com/)
- [x] [Docker Compose](https://docs.docker.com/compose/)
- [x] [Docker Hub](https://hub.docker.com/)