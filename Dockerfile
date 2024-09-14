FROM python:3.11
ENV PYTHONUNBUFFERED 1
WORKDIR /application
COPY . .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
