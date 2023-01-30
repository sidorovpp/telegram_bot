FROM python:3.11.1-slim-buster

WORKDIR /app
COPY requirements.txt requirements.txt

# install FreeTDS and dependencies
RUN apt-get update \
 && apt-get install unixodbc -y \
 && apt-get install unixodbc-dev -y \
 && apt-get install freetds-dev -y \
 && apt-get install freetds-bin -y \
 && apt-get install tdsodbc -y \
 && apt-get install --reinstall build-essential -y

# populate "ocbcinst.ini" as this is where ODBC driver config sits
RUN echo "[FreeTDS]\n\
Description = FreeTDS Driver\n\
Driver = /usr/lib/x86_64-linux-gnu/odbc/libtdsodbc.so\n\
Setup = /usr/lib/x86_64-linux-gnu/odbc/libtdsS.so" >> /etc/odbcinst.ini
RUN pip3 install -r requirements.txt
RUN pip install APScheduler
RUN pip install python-telegram-bot[job_queue]
COPY . .
COPY config_linux.json config.json

CMD [ "python", "main.py" ]
