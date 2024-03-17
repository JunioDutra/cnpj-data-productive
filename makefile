build-arm:
	docker buildx build --platform linux/arm64 -t 192.168.2.185:5000/app_web_admin:latest -f ./cnpj-data-admin/infrastructure/Dockerfile  ./cnpj-data-admin --push

build-arm-2:
	docker buildx build --platform linux/arm64 -t registry.dblsoft.xyz/app_web_admin:latest -f ./cnpj-data-admin/infrastructure/Dockerfile  ./cnpj-data-admin --push

build-x86:
	docker buildx build --platform linux/amd64 -t 192.168.2.185:5000/app_web_admin:latest -f ./cnpj-data-admin/infrastructure/Dockerfile  ./cnpj-data-admin --load

run-build-x86-local:
	docker buildx build --platform linux/amd64 -t app_web_admin -f ./cnpj-data-admin/infrastructure/Dockerfile  ./cnpj-data-admin --load
	docker run -it -p 8080:8080 app_web_admin