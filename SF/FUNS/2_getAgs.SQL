create or replace procedure getAgs ( TB STRING, NO FLOAT)
RETURNS ARRAY 
LANGUAGE JAVASCRIPT 
AS $$ 
var MYAGS= snowflake.createStatement ({ sqlText:"select  \
    sum(case when a.close-b.close >0 then a.close-b.close else 0 end )  as AG, \
    sum(case when a.open-b.open > 0 then a.open-b.open else 0 end )  as AL \
    from IDENTIFIER(?) a \
    inner join IDENTIFIER(?) b \
    on a.id+1=b.id \
    where a.id<=?", binds:[TB,TB,NO] });
FOO=MYAGS.execute();
FOO.next();
return [FOO.getColumnValue(1),FOO.getColumnValue(2)];
$$
  ;

CALL getAgs('BTC_1HR'::STRING,14::FLOAT);