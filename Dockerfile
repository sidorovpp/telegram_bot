FROM telegram-bot-base

COPY . .
COPY config_linux.json config.json

CMD [ "python", "main.py" ]
