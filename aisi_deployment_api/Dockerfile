FROM python:3.6


WORKDIR /aisi
COPY . /aisi

ARG env_val='VPCX_QA'
ARG is_vpcx="yes"
ENV ENV_VAL $env_val
ENV ENV_IS_VPCX $is_vpcx

RUN mkdir -p /app/logs

RUN apt-get update && apt-get install -y python3-pip
RUN pip3 install pip --upgrade
RUN pip3 install -r requirements.txt
RUN chmod 777 /aisi/azcopy2

EXPOSE 80

CMD ["sh", "-c", "python -u main.py ${ENV_VAL} ${ENV_IS_VPCX}"]