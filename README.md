# Description

This uses 

# Tech Stack

# How to run

## 0. Setup


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
