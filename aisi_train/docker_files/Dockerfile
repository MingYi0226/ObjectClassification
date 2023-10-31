# Use an official Python runtime as a parent image
FROM python:3.8

ARG is_vpcx=yes
ENV ENV_IS_VPCX $is_vpcx

ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES compute,utility
ENV PYTHONUNBUFFERED 1
ENV WORKER_CLASS="uvicorn.workers.UvicornH11Worker"

# Set the working directory
WORKDIR /aisi

# Copy the current directory contents into the container at working directory
COPY . /aisi

RUN mkdir -p /app/logs

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt
#RUN pip install -U 'git+https://github.com/cocodataset/cocoapi.git#subdirectory=PythonAPI'
# Make port available to the world outside this container
EXPOSE 80

# Run app.py when the container launches
CMD ["sh", "-c", "python -u aisi_api.py ${ENV_IS_VPCX}"]
