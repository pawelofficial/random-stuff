CREATE OR REPLACE FUNCTION "EMA"(CLOSE FLOAT, NO float)
RETURNS TABLE (EMA float)
    LANGUAGE JAVASCRIPT
    AS '{
    processRow: function (row, rowWriter, context) {
    this.alpha=2.0/(1.0+row.NO);
    if (this.ema==0) {
        this.ema=row.CLOSE;
    } 
    if (this.ema!=0){
    this.ema=this.alpha*row.CLOSE + (1-this.alpha)*this.ema;
    }
    rowWriter.writeRow( {EMA: this.ema} );
    
    },
    initialize: function(argumentInfo, context) {
    this.ema=0;
    }}';

--SELECT ID,CLOSE,EMA5(CLOSE::FLOAT,5::FLOAT) FROM BTC_1HR;