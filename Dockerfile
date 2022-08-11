FROM python:3.10
WORKDIR /app
RUN pip3 install --no-cache-dir requests
COPY . .
ENTRYPOINT [ "python3", "main.py" ]
