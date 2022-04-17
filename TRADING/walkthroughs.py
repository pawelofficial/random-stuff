from TRADING.API import BApi
b=BApi(config='./configs/binance_api.json')

if 1:
    print(b.check_positions())
    exit(1)

# walkthrough 1 - check price of crypto
if 0:
    print(b.get_price(asset='CARDANO'))

# w2 - check your positions 
if 1:
    print(b.get_position(asset='CARDANO'))
    print(b.get_position(asset='TETHER'))

if 0:
    b.close_position(asset='CARDANO')

# w3 - market buy/sell amount
if 0: 
    b.make_any_order(
        order_type='market',
        asset='CARDANO',
        amount=20,
        side='BUY',
        test_order=1
    )
    
if 0: 
    b.make_any_order(
        order_type='limit',
        price=0.5,
        base='TETHER',
        asset='CARDANO',
        percentage=100,
        side='BUY',
        test_order=1
    )
    
if 0:
    b.market_order(
    asset='CARDANO',
    quantity=15,
    side='SELL', # BUY for buying
    test_order=1, # watch out ! 
    in_dollars=True)

# w5 - market buy/sell percentage
if 0:
    b.market_order_p(
    base='CARDANO',
    asset='CARDANO',
    percentage=99,
    side='SELL', # BUY for buying
    test_order=0 # watch out ! 
    )

# w7 - order buy/sell amount 
if 0:
    b.order_limit_buy(
        asset='CARDANO',
        quantity=30,
        side='BUY',
        price=0.5)

# w8 - order buy/sell percentage 
if 0:
    b.order_limit_buy_p(
        base='TETHER',
        asset='CARDANO',
        percentage=100,
        side='BUY',
        price=0.8)


# w8 - cancel an order 

# w9 - close all orders

#w10 - market short 

if 1:
    print(b.get_position(asset='CARDANO'))
    print(b.get_position(asset='TETHER'))


