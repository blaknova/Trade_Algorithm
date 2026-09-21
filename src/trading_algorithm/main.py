from collections import defaultdict
volume_per_level = defaultdict(float)
high_per_level = defaultdict(float)
low_per_level = defaultdict(lambda: float('inf'))
threshold = 1000


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

def Absorption(trade_price, trade_size, tick_size):
    global volume_per_level, high_per_level, low_per_level
    
    level = round(trade_price / tick_size) * tick_size
    volume_per_level[level] += trade_size
    
    high_per_level[level] = max(high_per_level[level], trade_price)
    low_per_level[level] = min(low_per_level[level], trade_price)
    
    displacement = high_per_level[level] - low_per_level[level]
    
    if displacement == 0:
        absorption = float('inf')
        print(absorption)
    else:
        absorption = volume_per_level[level] / displacement
        print(absorption)
    
    if absorption > threshold:
        print("Absorption Detected")
        return "Absorption_Detected"
    else:
        print("No Absorption Detected")
        return absorption

# Reset the global dictionaries between tests
volume_per_level.clear()
high_per_level.clear()
low_per_level.clear()

# Two trades far apart in price, small volume
Absorption(trade_price=100.0, trade_size=50, tick_size=0.25)
print(Absorption(trade_price=102.0, trade_size=50, tick_size=0.25))