# Description
Provides a API server to read financial data and statistics.

# Tech Stack
- Docker
- PostgreSQL
  - Performant Database
- FastAPI (Python)
  - Easy to develop yet performant RESTful API server
  - Built-in query parameter check
- Pandas (Python)
  - Easy to process data, e.g. computing statistics of data
  


# How to run
## 0. Setup
Data fill script needs PostgreSQL client installed on the system.
```
# Ubuntu/Debian
$ apt install -y postgresql-client

# Mac
$ brew install postgresql
```

Environment variables are used to pass necessary parameters to components and scripts, so you have to set the envionrment variables before running the server.
```
## AlphaVantage API Key
ALPHA_VANTAGE_KEY="KEY_HERE"

## Database related
DB_USER="testuser"
DB_PASSWORD="testpass"
DB_DATABASE="testdb"

```

## 1. Start the database and api server
Start up the database and 

```
  $ docker-compose up
```

## 2. Create the table `financial_data`
```
  $ psql -h localhost -p 5432 -U $DB_USER -w $DB_PASSWORD -d $DB_DATABASE
```

## 3. Fill in the data with `get_raw_data.py`
```
  $ pip3 install -r requirements.txt
  $ python get_raw_data.py
```
