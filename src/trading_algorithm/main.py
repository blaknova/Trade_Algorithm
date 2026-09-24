from collections import defaultdict, deque

# Tracks the cumulative traded volume at each price level.
volume_per_level = defaultdict(float)

# Tracks the highest trade price observed at each level.
high_per_level = defaultdict(float)

# Tracks the lowest trade price observed at each level.
low_per_level = defaultdict(lambda: float('inf'))

# Threshold used to flag abnormal absorption at a price level.
threshold = 1000


def Aggressor_Side_Classification(Current_price, Ask_price, Bid_price, prices):
    # If the current price is at or above the ask, the incoming trade likely hit the offer.
    if Current_price >= Ask_price:
        return "Buy"
    # If the current price is at or below the bid, the incoming trade likely hit the bid.
    elif Current_price <= Bid_price:
        return "Sell"
    else:
        # In the bid/ask dead zone, we inspect recent price direction to infer aggressor intent.
        Deadzone = Bid_price < Current_price < Ask_price
        if Deadzone:
            i = len(prices) - 1
            while True:
                current = prices[i]
                previous = prices[i - 1]

                # Rising price sequence suggests buying pressure; falling sequence suggests selling pressure.
                if previous < current:
                    return "Buy"
                elif previous > current:
                    return "Sell"
                elif previous == current:
                    i = i - 1
                    if i == 0:
                        return "No Aggressor Side"
                    
def Cumulative_Volume_Delta_Calculator(Current_price,Ask_price,Bid_price, prices, volume, timestamp):
    # Running net volume delta for the session; reset at the close.
    Cumulative_Volume_Delta = 0
    while True:
        # Classify whether the trade looked buyer- or seller-driven.
        label =Aggressor_Side_Classification(Current_price, Ask_price, Bid_price, prices)
        Volume_Delta = 0
        if label == "Buy":
            Volume_Delta = volume
        elif label == "Sell":
            Volume_Delta = -volume
        else:
            # No aggressor classification means no directional contribution.
            Volume_Delta += 0

        # Reset the cumulative measure after market close.
        if timestamp >= 2300:
            Cumulative_Volume_Delta = 0
        elif timestamp >= 1530:
            Cumulative_Volume_Delta += Volume_Delta
        print(Cumulative_Volume_Delta)
        return Cumulative_Volume_Delta
    
# Tracks the prior EMA value so the imbalance signal can smooth over time.
Previous_EMA = 0

def bid_ask_imbalance(bid_depth, ask_depth, alpha, timestamp):
    global Previous_EMA

    # Positive values indicate more bid pressure; negative values indicate more ask pressure.
    imbalance = (bid_depth - ask_depth)/(bid_depth + ask_depth)
    if imbalance > 0.5:
        label = "Bid_Heavy"
    elif imbalance < -0.5:
        label = "Ask_Heavey"
    else:
        label = "Balanced"

    # Reset the smoothing state after the market closes.
    if timestamp >= 2300:
        EMA = 0
        Previous_EMA = 0
    elif timestamp >= 1530:
        # Exponential smoothing of the imbalance signal over time.
        EMA = (alpha * imbalance) + ((1 - alpha) * Previous_EMA)
        Previous_EMA = 0
        print(f"imbalance is {imbalance} | label is {label} | EMA is {EMA}")
        return imbalance, label, EMA
    else:
        print(f"imbalance is {imbalance} | label is {label} | EMA is {None}")
        return imbalance, label, None

def Absorption(trade_price, trade_size, tick_size):
    global volume_per_level, high_per_level, low_per_level

    # Normalize the trade to the nearest tick-based price bucket.
    level = round(trade_price / tick_size) * tick_size

    # Accumulate volume at that level and track the range of prices seen there.
    volume_per_level[level] += trade_size
    high_per_level[level] = max(high_per_level[level], trade_price)
    low_per_level[level] = min(low_per_level[level], trade_price)
    displacement = high_per_level[level] - low_per_level[level]

    # If there is no price range, the signal is treated as extreme absorption.
    if displacement == 0:
        absorption = float('inf')
    else:
        absorption = volume_per_level[level] / displacement

    # Large values indicate price is being absorbed rather than moving freely.
    if absorption > threshold:
        return "Absorption_Detected"
    else:
        return absorption

# Reset the global dictionaries between tests to avoid stale state leakage.
volume_per_level.clear()
high_per_level.clear()
low_per_level.clear()

# Keep a short rolling lookback of trades to detect local swing behavior.
price_history = deque(maxlen=50)  # Store the last 50 prices
delta_history = deque(maxlen=50)  # Store the last 50 volume deltas
swing_highs = deque(maxlen=3)  # Store the last 3 swing highs
swing_lows = deque(maxlen=3)  # Store the last 3 swing lows

def Exhaustion(trade_price, volume_delta):
    global price_history, delta_history, swing_highs, swing_lows

    # Record the newest trade so trend exhaustion can be evaluated on a sliding window.
    price_history.append(trade_price)
    delta_history.append(volume_delta)

    if len(price_history) < 5:
        return "Not enough data"

    # Scan recent price action for local peak and trough formations.
    for i in range(2, len(price_history) - 2):
        current_price = price_history[i]
        previous_price_1 = price_history[i - 1]
        previous_price_2 = price_history[i - 2]
        next_price_1 = price_history[i + 1]
        next_price_2 = price_history[i + 2]

        # A swing high is a local peak where price rises above neighbors before falling.
        if (
            current_price > previous_price_1
            and current_price > previous_price_2
            and current_price > next_price_1
            and current_price > next_price_2
        ):
            swing_highs.append((current_price, delta_history[i]))

        # A swing low is a local trough where price falls below neighbors before rising.
        if (
            current_price < previous_price_1
            and current_price < previous_price_2
            and current_price < next_price_1
            and current_price < next_price_2
        ):
            swing_lows.append((current_price, delta_history[i]))

    # Bullish exhaustion occurs when successive highs rise while associated volume deltas weaken.
    if len(swing_highs) >= 3:
        price0, delta0 = swing_highs[0]
        price1, delta1 = swing_highs[1]
        price2, delta2 = swing_highs[2]

        if price0 < price1 and price1 < price2 and delta0 > delta1 and delta1 > delta2:
            return "Bullish_Exhaustion"

    # Bearish exhaustion occurs when successive lows fall while volume deltas weaken.
    if len(swing_lows) >= 3:
        price0, delta0 = swing_lows[0]
        price1, delta1 = swing_lows[1]
        price2, delta2 = swing_lows[2]

        if price0 > price1 and price1 > price2 and delta0 < delta1 and delta1 < delta2:
            return "Bearish_Exhaustion"

    return "No_Exhaustion"

footprint = defaultdict(lambda: [0, 0])
bar_high = 0
bar_low = float('inf')
current_bar = None


def round_to_bar(timestamp):
    """Group timestamps into the same price bar bucket.

    The project uses integer timestamps like 1000, 1005, 1015, so values in
    the same 100-unit bucket belong to the same bar.
    """
    return int(timestamp // 100) * 100


def Footprint_Delta(trade_price, volume, direction, timestamp, tick_size):
    global footprint, bar_high, bar_low, current_bar

    bar_time = round_to_bar(timestamp)

    if current_bar is None:
        current_bar = bar_time
    elif bar_time != current_bar:
        if footprint:
            POC = max(footprint, key=lambda level: footprint[level][0] + footprint[level][1])
            delta_at_high = footprint.get(bar_high, [0, 0])[0] - footprint.get(bar_high, [0, 0])[1]
            delta_at_low = footprint.get(bar_low, [0, 0])[0] - footprint.get(bar_low, [0, 0])[1]

            total_buy = sum(level_data[0] for level_data in footprint.values())
            total_sell = sum(level_data[1] for level_data in footprint.values())
            bar_delta = total_buy - total_sell

            print(POC, delta_at_high, delta_at_low, bar_delta)

        footprint.clear()
        bar_high = 0
        bar_low = float('inf')
        current_bar = bar_time

    level = round(trade_price / tick_size) * tick_size

    if direction == "Buy":
        footprint[level][0] += volume
    elif direction == "Sell":
        footprint[level][1] += volume

    bar_high = max(bar_high, trade_price)
    bar_low = min(bar_low, trade_price)

    return None
    