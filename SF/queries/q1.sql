with cte as (
select * from BITCORN_DB.DEV.btc_test_5min_calcs
where id > 5000)
select a.id previd, b.id thisid, b.close close, a.close as prevclose,
    a.macd as prevmacd,
    a.signal as prevsignal,
    b.macd as thismacd,
    b.signal as thissignal,
    b.rsi,
    case when b.rsi < 35 then b.close else NULL end as BUY,
    case when b.rsi > 65 then b.close else NULL end as SELL,

    case when prevsignal<prevmacd and thissignal>thismacd then b.close else NULL end as gcross,
    case when prevsignal>prevmacd and thissignal<thismacd then b.close else NULL end as dcross
from cte a 
inner join cte b on a.id+1=b.id;
