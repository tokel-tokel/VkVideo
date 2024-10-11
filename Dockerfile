FROM python:3.12.2-alpine3.19

WORKDIR /home/app

COPY . ./
COPY requirements.txt /tmp/

RUN apk add ffmpeg
RUN pip install -r /tmp/requirements.txt

ENTRYPOINT ["python", "main.py"]
