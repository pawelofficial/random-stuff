
#creates calculation view - view with emas, rsis etc
#   returns:
#        empty array
#   requires:
#    - getAGs procedure for RSI calculation  
#    - RSI2 table function for RSI calculation 
#    - EMA table function for NO calculation 
#    - agg view
#inputs:
#   makeCV(no, aggview, output)
#    - no - calculations period like ema 
#    - aggview ->  
#example:
#   call makeCV(14, 'BTC_TEST_1HR','BTC_TEST_1HR_CALCS');
#   select * from BTC_TEST_1HR_CALCS where ID > 8000 
;
call GETAGS(14::float,'BTC_1HR');
;

  CREATE OR REPLACE PROCEDURE makeCV(NO FLOAT, TB STRING, NM string)
  RETURNS array
  LANGUAGE JAVASCRIPT 
  EXECUTE AS caller
  AS $$
  var ags=snowflake.createStatement({sqlText: "call getAGs(?,?)", binds:[NO,TB] } );
  foo=ags.execute();
  foo.next();
  FAG=parseFloat(foo.getColumnValue(1)[0]);
  FAL=parseFloat(foo.getColumnValue(1)[1]);

  var  stm=snowflake.createStatement({sqlText:"\
  create or replace view IDENTIFIER(?) as ( WITH CTE AS ( select a.id, \
  a.open, \
  a.close,\
  a.CANDLE_START as CANDLE_START, \
  a.CANDLE_END as CANDLE_END, \
  EMA5.EMA AS EMA5, \
  EMA10.EMA AS EMA10, \
  EMA15.EMA AS EMA15, \
  RSI2.RSI as RSI, \
    MACD1.EMA-MACD2.EMA AS MACD, SIGNAL.EMA AS SIGNAL \
  from IDENTIFIER(?) a, \
      TABLE(EMA(a.close::FLOAT, 5::FLOAT)) as EMA5, \
      TABLE(EMA(a.close::FLOAT, 10::FLOAT)) as EMA10, \
      TABLE(EMA(a.close::FLOAT, 15::FLOAT)) as EMA15, \
      TABLE(EMA(A.CLOSE,26::float)) AS MACD1, \
      TABLE(EMA(A.CLOSE,12::float)) AS MACD2, \
      TABLE(EMA( (MACD1.EMA-MACD2.EMA)::FLOAT,6::FLOAT)) AS SIGNAL \
      where a.id>14 ) \
      SELECT * from CTE ) \
      ",binds:[NM,TB,TB]});
  stm.execute();
  return [];
  $$;

  #call makeCV(14::FLOAT, 'BTC_1HR','BTC_1HR_CV');
  #select * from BTC_1HR_CV; 



-- V2 NO SELF JOIN WITH NEW RSI DEF 
CREATE OR REPLACE PROCEDURE makeCV(NO FLOAT, TB STRING, NM string)
RETURNS array
LANGUAGE JAVASCRIPT 
EXECUTE AS caller
AS $$
var ags=snowflake.createStatement({sqlText: "call getAGs(?,?)", binds:[NO,TB] } );
foo=ags.execute();
foo.next();
FAG=parseFloat(foo.getColumnValue(1)[0]);
FAL=parseFloat(foo.getColumnValue(1)[1]);
var  stm=snowflake.createStatement({sqlText:"\
create or replace view IDENTIFIER(?) as ( WITH CTE AS ( select a.id, \
a.open, \
a.close,\
a.CANDLE_START as CANDLE_START, \
a.CANDLE_END as CANDLE_END, \
EMA5.EMA AS EMA5, \
EMA10.EMA AS EMA10, \
EMA15.EMA AS EMA15, \
RSI.RSI as RSI, \
  MACD1.EMA-MACD2.EMA AS MACD, SIGNAL.EMA AS SIGNAL \
from IDENTIFIER(?) a, \
    TABLE(RSI(A.close::float,"+FAG+"::float,"+FAL+"::float)) AS RSI,\
    TABLE(EMA(a.close::FLOAT, 5::FLOAT)) as EMA5, \
    TABLE(EMA(a.close::FLOAT, 10::FLOAT)) as EMA10, \
    TABLE(EMA(a.close::FLOAT, 15::FLOAT)) as EMA15, \
    TABLE(EMA(A.CLOSE,26::float)) AS MACD1, \
    TABLE(EMA(A.CLOSE,12::float)) AS MACD2, \
    TABLE(EMA( (MACD1.EMA-MACD2.EMA)::FLOAT,6::FLOAT)) AS SIGNAL \
    where a.id>14 ) \
    SELECT * from CTE ) \
    ",binds:[NM,TB,TB]});
stm.execute();
return [];
$$;
  #call makeCV(14::FLOAT, 'BTC_1HR','BTC_1HR_CV');
  #select * from BTC_1HR_CV; 


