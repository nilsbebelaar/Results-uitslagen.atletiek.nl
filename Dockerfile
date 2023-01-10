FROM python:slim

RUN useradd uitslagen

WORKDIR /home/uitslagen

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY app app
RUN mkdir database
COPY start.py config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP start.py

RUN chown -R uitslagen:uitslagen ./
USER uitslagen

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]