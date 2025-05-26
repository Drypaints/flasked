FROM python:3.13-slim

RUN apt-get update && apt-get install -y curl wget build-essential postgresql netcat-traditional nano
RUN useradd -ms /bin/bash flask-app
RUN pip install playwright
RUN python -m playwright install --with-deps firefox

COPY rootflag.txt /root/flag.txt

COPY backup.sh /home/flask-app/backup.sh
COPY suid_wrapper.c /home/flask-app/suid_wrapper.c
RUN gcc -o /home/flask-app/suid_wrapper /home/flask-app/suid_wrapper.c
RUN chmod 6755 /home/flask-app/suid_wrapper

USER flask-app

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt 
RUN python -m playwright install firefox

COPY . .
RUN rm rootflag.txt

CMD [ "/usr/local/bin/python", "/app/main.py" ]
