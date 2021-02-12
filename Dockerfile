FROM python:3.7-slim
WORKDIR /code
COPY ./src/requirements.txt /code/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY ./src /code
EXPOSE 5000