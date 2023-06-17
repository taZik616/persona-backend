FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONWARNINGS="ignore:Unverified HTTPS request"

RUN apt-get update && apt-get install -y memcached && rm -rf /var/lib/apt/lists/*
# && apt-get install -y memcached rabbitmq-server docker-compose 
WORKDIR /project
COPY . /project/

RUN pip install -r reqs.txt
# -d - если нужно запустить фоном

# CMD ["gunicorn", "--bind","0.0.0.0:2006", "persona_backend.wsgi:application"]