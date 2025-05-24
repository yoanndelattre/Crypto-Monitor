FROM python:3-alpine
ENV WEBHOOK_URL_DISCORD="https://discord.com/api/webhooks/XXX/YYY"
WORKDIR /app
COPY main.py requirements.txt ./
RUN pip install -r requirements.txt
CMD [ "python", "main.py" ]