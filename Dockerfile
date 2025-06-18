FROM python:3.13-slim

RUN useradd uitslagen

WORKDIR /home/uitslagen

# Install dotenvx
RUN apt-get -y update && apt-get -y install curl
RUN curl -sfS https://dotenvx.sh | sh


COPY requirements.txt requirements.txt
RUN pip install gunicorn
RUN pip install gevent
RUN pip install --no-cache-dir -r requirements.txt

ENV FLASK_APP=start.py

COPY app app
RUN mkdir database
COPY start.py config.py .env ./

RUN chown -R uitslagen:uitslagen ./
USER uitslagen

EXPOSE 5000
CMD ["dotenvx", "run",  "--env-file=.env", "--", "gunicorn", "-b", ":5000", "--timeout", "300", "--access-logfile", "-", "--error-logfile", "-", "start:app", "--worker-class", "gevent"]