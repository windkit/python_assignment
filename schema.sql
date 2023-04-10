CREATE TABLE financial_data (
  symbol  VARCHAR(10),
  date  DATE,
  open_price REAL,
  close_price REAL,
  volume BIGINT,
  UNIQUE (symbol, date)
);
