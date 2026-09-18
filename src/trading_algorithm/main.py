def Aggressor_Side_Classification(Current_price, Ask_price, Bid_price, prices):
    Spread = Ask_price - Bid_price

    if Current_price >= Ask_price:
        return "Buy"
    elif Current_price <= Bid_price:
        return "Sell"
    else:
        Deadzone = Bid_price < Current_price < Ask_price
        if Deadzone:
            i = len(prices) - 1
            while True:
                current = prices[i]
                previous = prices[i - 1]

                if previous < current:
                    return "Buy"
                elif previous > current:
                    return "Sell"
                elif previous == current:
                    i = i - 1
                    if i == 0:
                        return "No Aggressor Side"
                    
def Cumulative_Volume_Delta_Calculator(Current_price,Ask_price,Bid_price, prices, volume, timestamp):
    Cumulative_Volume_Delta = 0
    while True:
        label =Aggressor_Side_Classification(Current_price, Ask_price, Bid_price, prices)
        Volume_Delta = 0
        if label == "Buy":
            Volume_Delta = volume
        elif label == "Sell":
            Volume_Delta = -volume
        else:
            Volume_Delta += 0

        if timestamp >= 1530:
            Cumulative_Volume_Delta += Volume_Delta
        elif timestamp == 2300:
            Cumulative_Volume_Delta = 0
        print(Volume_Delta)
        return Cumulative_Volume_Delta

Cumulative_Volume_Delta_Calculator(Current_price=10, Ask_price=12, Bid_price=19, prices=[98, 99, 100, 101], volume=10, timestamp=1635)