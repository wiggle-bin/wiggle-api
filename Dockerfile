FROM python:3.7.4-slim-buster
EXPOSE 5000
WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY . .
CMD ["flask", "run", "--host", "0.0.0.0"]