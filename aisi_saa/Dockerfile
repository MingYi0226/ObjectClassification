FROM python:3.7

WORKDIR /aisi
COPY . /aisi
# Creating mount path as /app/logs
RUN mkdir -p /app/logs

ARG env_val="VPCX_QA"
ARG is_vpcx="yes"

ENV ENV_VAL $env_val
ENV ENV_IS_VPCX $is_vpcx

# RUN if [ "$is_QA" = "yes" ]; then \
#     bash -c "source env_QA.sh"; \
#     else \
#     bash -c "source env_PROD.sh"; \
#     fi
RUN apt-get update && apt-get install -y python3-pip
RUN pip3 install pip --upgrade
RUN pip3 install -r requirements.txt
RUN chmod 777 /aisi/azcopy2
EXPOSE 80


# ENTRYPOINT ["python"]

CMD ["sh", "-c", "python -u app.py ${ENV_VAL} ${ENV_IS_VPCX}"]