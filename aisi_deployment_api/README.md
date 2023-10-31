# Introduction
Deployment API app in Docker

# Prerequisites
1) Create an Azure storage
2) Create a KeyVault in Azure

To connect to your keyvault, please change the Azure App Registerations authentication variables and Azure KeyVault
name in Dockerfile.

### Build application
Build the Docker image manually.
```
$ docker build -t aisi_deployment --build-arg env_val="DT" .
```
or
```
$ docker build -t aisi_deployment --build-arg env_val="VPCX_QA" .
```
or
```
$ docker build -t aisi_deployment --build-arg env_val="PROD" .
```
### Run the container
Create a container from the image.
```
$ docker run --name my-aisi-deployment -d -p 8080:80 aisi_deployment
```

Now visit http://localhost:80/start_deploy or
http://localhost:80/get_status




