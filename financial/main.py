#!/usr/bin/env python3

import json
import os
import psycopg2
import logging
from logging import INFO
import pandas as pd

from fastapi import FastAPI

# create formatter
formatter = logging.Formatter(
    "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")

logger = logging.getLogger(__name__)
logger.setLevel(INFO)
log_handler = logging.FileHandler(filename=__file__ + ".log")
log_handler.setFormatter(formatter)
logger.addHandler(log_handler)


def start_server():
    # Database connection configurations.
    user = os.environ.get('DB_USER', 'postgres')
    password = os.environ.get('DB_PASSWORD', 'postgres')
    database = os.environ.get('DB_DATABASE', 'postgres')
    host = os.environ.get('DB_HOST', 'localhost')
    port = os.environ.get('DB_PORT', 5432)

    db_conn = psycopg2.connect(
        database=database,
        host=host,
        port=port,
        user=user,
        password=password)

    app = FastAPI()
    return db_conn, app


db_conn, app = start_server()


@app.get("/database")
def read_db():
    return str(db_conn)


@app.get("/status")
def read_status():
    return "OK Test"


DATA_STATEMENT = "SELECT * FROM financial_data"


def get_data(start_date, end_date, symbol):
    query = DATA_STATEMENT
    query_values = []
    where_clauses = []

    # TODO: Validation
    if start_date:
        where_clauses.append("date >= %s")
        query_values.append(start_date)

    if end_date:
        where_clauses.append("date <= %s")
        query_values.append(end_date)

    if symbol:
        where_clauses.append("symbol = %s")
        query_values.append(symbol)

    if where_clauses:
        query += " WHERE "
        query += " AND ".join(where_clauses)

    cursor = db_conn.cursor()
    if query_values:
        select_sql = cursor.mogrify(query, query_values)
    else:
        select_sql = cursor.mogrify(query)
    df = pd.read_sql(select_sql.decode('utf-8'), db_conn)

    return df


@app.get("/api/financial_data")
def read_data(limit: int = 5, start_date: str | None = None, end_date: str | None = None, symbol: str | None = None, page: int = 1):
    df = get_data(start_date, end_date, symbol)
    count = len(df)
    pages = count // limit + (count % limit > 0)
    offset = (page - 1) * limit
    df = df.iloc[offset:offset+limit]
    df['date'] = df['date'].astype("string")
    df_json = json.loads(df.to_json(orient="records"))
    result_dict = {"data": df_json,
                   "pagination": {
                       "count": count,
                       "page": page,
                       "limit": limit,
                       "pages": pages
                   },
                   "info": {'error': ''}}

    return result_dict


@app.get("/api/statistics")
def read_stat(start_date: str, end_date: str, symbol: str):
    df = get_data(start_date, end_date, symbol)

    # Catch the case when there is no data fetched with the supplied arguments.
    if df.empty:
        return {
            "data": {},
            "info": {'error': 'No data available'}
        }

    avg_open = df["open_price"].mean()
    avg_close = df["close_price"].mean()
    avg_vol = df["volume"].mean()
    result_dict = {
        "data": {
            "start_date": start_date,
            "end_date": end_date,
            "symbol": symbol,
            "average_daily_open_price": avg_open,
            "average_daily_close_price": avg_close,
            "average_daily_volume": avg_vol
        },
        "info": {'error': ''}
    }
    return result_dict
