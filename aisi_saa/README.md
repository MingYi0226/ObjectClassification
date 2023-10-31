# Introduction
Semi Auto Annotation FastAPI app in Docker which anticipates the annotations on image series on Azure Storage

# Prerequisites
1) Create an Azure storage
2) Create a KeyVault in Azure

To connect to your keyvault, please change the Azure App Registerations authentication variables and Azure KeyVault
name in Dockerfile.

### Build application
Build the Docker image manually.
```
$ docker build -t saa_api --build-arg env_val="VPCX_QA" .
```
or
```
$ docker build -t saa_api --build-arg env_val="VPCX_PROD" .
```

### Run the container
Create a container from the image.
```
$ docker run --name my-saa-api -d -p 8080:80 saa_api
```

Now visit http://localhost:8080/get_status or
http://localhost:8080/make_annotations
