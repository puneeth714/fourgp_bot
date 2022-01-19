-- find number of values in  coloum Timestamp has any value repeated in Kline_ETHUSDT_1m table
select count(*) from (select distinct Timestamp from Kline_ETHUSDT_1m) as t;

--find the max value in Timestamp coloumn of table Kline_ETHUSDT_1m
select max(Timestamp) from Kline_ETHUSDT_1m;

--find the count of values in Timestamp coloumn of table Kline_ETHUSDT_1m
    --SELECT all from Kline_ETHUSDT_1m order by TimeStamp in descending order
    select TimeStamp/1000 from Kline_ETHUSDT_1m order by Timestamp desc;

    --SELECT all from Kline_ETHUSDT_1m TABLE
    select count(*) from Kline_ETHUSDT_1m;

    --SELECT all from Kline_ETHUSDT_3m TABLE
    select count(*) from Kline_ETHUSDT_3m;

    --SELECT all from Kline_ETHUSDT_5m TABLE
    select count(*) from Kline_ETHUSDT_5m;

    --SELECT all from Kline_ETHUSDT_5m TABLE
    select count(*) from Kline_ETHUSDT_5m;


--Fix the bug in getting limited values
SELECT count(*) from Kline_ETHUSDT_1m;
SELECT count(*) from Kline_ETHUSDT_1m WHERE Timestamp > 1642206660000;

SELECT count(*) from Kline_ETHUSDT_3m;
SELECT count(*) from Kline_ETHUSDT_3m WHERE Timestamp > 1642206660000;

SELECT count(*) from Kline_ETHUSDT_5m;
SELECT count(*) from Kline_ETHUSDT_5m WHERE Timestamp > 1642206660000;

SELECT count(*) from Kline_ETHUSDT_4h;
SELECT count(*) from Kline_ETHUSDT_4h WHERE Timestamp > 1642206660000;

SELECT * from Kline_ETHUSDT_1m order by Timestamp desc;

--get all table names and drop table names starting with Indicators_ in sqlite3
SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'Indicators_%';
