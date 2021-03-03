FROM python:3.8 as bigimage
RUN apt-get update && \
    apt-get install -y gcc python-pycurl curl
COPY ./requirements.txt ./requirements.txt
RUN pip install --prefix=/install -r ./requirements.txt
FROM python:3.8-alpine as smallimage
ENV PYTHONUNBUFFERED 1
COPY --from=bigimage /install /usr/local
COPY app app
WORKDIR app
CMD ["python", "main.py"]