#!/usr/bin/env python3

import requests
import datetime
import sys
import os
import psycopg2
import logging
from psycopg2.extensions import AsIs
from logging import INFO


URL_FMT_STR = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=%s&apikey=%s'
TZ_KEY = "5. Time Zone"
OPEN_KEY = "1. open"
CLOSE_KEY = "4. close"
VOLUME_KEY = "6. volume"
INSERT_FORMAT = 'INSERT INTO financial_data (%s) VALUES %s ON CONFLICT (symbol, date) DO NOTHING'

# create formatter
formatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")

logger = logging.getLogger(__name__)
logger.setLevel(INFO)
log_handler = logging.FileHandler(filename=__file__ + ".log")
log_handler.setFormatter(formatter)
logger.addHandler(log_handler)

logger.info("Fetch data from Alpha Vantage.")

datetime_cur = datetime.datetime.now().date()
datetime_14d = datetime_cur - datetime.timedelta(days=14)


def get_one_stock(db_conn, key, symbol):
    url = URL_FMT_STR % (symbol, key)
    r = requests.get(url)
    r.raise_for_status()
    data = r.json()

    try:
        ts = data["Time Series (Daily)"]
        meta = data["Meta Data"]
    except Exception as e:
        sys.exit("Data unavailable from AlphaVantage")

    for date, data in ts.items():
        dt = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        if dt < datetime_14d:
            continue
        open_price = data[OPEN_KEY]
        close_price = data[CLOSE_KEY]
        volume = data[VOLUME_KEY]

        record = {
            "symbol": symbol,
            "date": date,
            "open_price": float(open_price),
            "close_price": float(close_price),
            "volume": int(volume)
        }

        keys = record.keys()
        values = [record[k] for k in keys]

        cursor = db_conn.cursor()
        try:
            cursor.execute(INSERT_FORMAT, (AsIs(
                ','.join(keys)), tuple(values)))
            db_conn.commit()
        except Exception as e:
            logger.error(e)
            db_conn.rollback()
        finally:
            cursor.close()


def main():
    key = os.environ.get('ALPHA_VANTAGE_KEY', 'demo')

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

    for symbol in ['IBM', 'AAPL']:
        get_one_stock(db_conn, key, symbol)

    db_conn.close()


if __name__ == "__main__":
    main()
