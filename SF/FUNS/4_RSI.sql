-- creates table function for rsi calculation 
create or replace function "RSI"(CLOSE float, PCLOSE FLOAT, FAG float,FAL float)
returns table(RSI float) 
language javascript as $$ {
initialize: function (ArgumentInfo,context ) { 
this.FAG=ArgumentInfo.FAG.constValue;
this.FAL=ArgumentInfo.FAL.constValue;
},
processRow: function (row,rowWriter,context){
cg=row.CLOSE-row.PCLOSE;
cl=row.PCLOSE-row.CLOSE;
if (cg<0){cg=0};
if (cl<0){cl=0};

ag=(13*this.FAG+cg)/14;
al=(13*this.FAL+cl)/14;
rsi=100-100/(1+ag/al);
rowWriter.writeRow( { RSI: rsi } );
this.FAG=ag;
this.FAL=al;
}}
$$
;
 
-- new version - does not require PCLOSE and hence selfjoin !  
create or replace function "RSI"(CLOSE float, FAG float,FAL float)
returns table(RSI float) 
language javascript as $$ {
initialize: function (ArgumentInfo,context ) { 
this.FAG=ArgumentInfo.FAG.constValue;
this.FAL=ArgumentInfo.FAL.constValue;
this.PCLOSE=-1;
},
processRow: function (row,rowWriter,context){
if (this.PCLOSE==-1) {this.PCLOSE=row.CLOSE*0.99};
cg=row.CLOSE-this.PCLOSE;
cl=this.PCLOSE-row.CLOSE;
if (cg<0){cg=0};
if (cl<0){cl=0};

ag=(13*this.FAG+cg)/14;
al=(13*this.FAL+cl)/14;
rsi=100-100/(1+ag/al);
rowWriter.writeRow( { RSI: rsi } );
this.FAG=ag;
this.FAL=al;
this.PCLOSE=row.CLOSE;
}}
$$
;