# this sql create saggregation view for candles stuff 
# call makeAggView('BTC_TEST_1MINUTE','MINUTE','BTC_TEST');
# 

create or replace procedure makeAggView2( NM string, TF FLOAT)
returns float 
language javascript as $$ 
var st= snowflake.createStatement({sqlText:"create or replace view identifier(?) ( ID, CANDLE_START, CANDLE_END,LOW,HIGH,OPEN,CLOSE) as ( \
 WITH CTEO AS ( \
 WITH CTE AS (  \
 SELECT END_TIME,LOW,HIGH,OPEN,CLOSE \
 FROM BTC_RAW ), \
 CTE2 AS (  \
 SELECT  MIN(END_TIME) CANDLE_START,MAX(END_TIME) AS CANDLE_END, MIN(LOW) AS LOW, MAX(HIGH) AS HIGH \
 FROM CTE  \
 GROUP BY time_slice(END_TIME, "+TF+", 'MINUTE') ) \
 SELECT CTE2.CANDLE_START,CTE2.CANDLE_END,CTE2.LOW,CTE2.HIGH, A.OPEN AS OPEN, B.CLOSE AS CLOSE  FROM CTE2 \
 INNER JOIN BTC_RAW A \
    ON CTE2.CANDLE_START=A.END_TIME \
INNER JOIN BTC_RAW B  \
    ON CTE2.CANDLE_END=B.END_TIME \
    ) SELECT ROW_NUMBER() OVER(ORDER BY CANDLE_START) AS ID, * FROM CTEO ORDER BY ID \
    )",binds:[NM] }).execute();
    return 1.0
$$;

call makeAggView2('BTC_1HR',60);
call makeAggView2('BTC_4HR',60*4);
call makeAggView2('BTC_1D',60*24);