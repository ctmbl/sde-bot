FROM python:3.10.9

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

WORKDIR /opt/sde-bot
COPY . .

ENTRYPOINT ["python3"]
CMD ["/opt/sde-bot/main.py"]
