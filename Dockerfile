FROM python:3.11.1-slim-buster

ENV TZ="Europe/Moscow"
WORKDIR /app
COPY requirements.txt requirements.txt

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
RUN apt-get install zbar-tools -y
RUN pip3 install -r requirements.txt

COPY . .
COPY config_linux.json config.json

CMD [ "python", "main.py" ]
