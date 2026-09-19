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

        if timestamp >= 2300:
            Cumulative_Volume_Delta = 0
        elif timestamp >= 1530:
            Cumulative_Volume_Delta += Volume_Delta
        print(Cumulative_Volume_Delta)
        return Cumulative_Volume_Delta
    
Previous_EMA = 0
def bid_ask_imbalance(bid_depth, ask_depth, alpha, timestamp):

    global Previous_EMA

    imbalance = (bid_depth - ask_depth)/(bid_depth + ask_depth)
    if imbalance > 0.5:
        label = "Bid_Heavy"
    elif imbalance < -0.5:
        label = "Ask_Heavey"
    else:
        label = "Balanced"

    if timestamp >= 2300:
        EMA = 0
        Previous_EMA = 0
    elif timestamp >= 1530:
        EMA = (alpha * imbalance) + ((1 - alpha) * Previous_EMA) 
        Previous_EMA = 0
        print(f"imbalance is {imbalance} | label is {label} | EMA is {EMA}")
        return imbalance, label, EMA
    else:
        print(f"imbalance is {imbalance} | label is {label} | EMA is {None}")
        return imbalance, label, None


          

    
