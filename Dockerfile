FROM python:3.9-slim-buster

WORKDIR /NumbersTestWork
COPY ./ /NumbersTestWork

RUN pip3 install -r requirements.txt