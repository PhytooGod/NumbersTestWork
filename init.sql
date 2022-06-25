CREATE DATABASE numberstest;
\c numberstest
CREATE TABLE numbersdata(num integer PRIMARY KEY, ordernum integer, pricedollar numeric, supplydate date, priceruble numeric);