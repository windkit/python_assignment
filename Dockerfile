FROM python:3.11

EXPOSE 5000

WORKDIR /api_server

COPY financial/* .

# Install the required Python libraries according to requirements.txt
RUN pip3 install -r requirements.txt

CMD ["python3", "main.py"]
