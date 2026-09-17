def Aggressor_Side_Classification():
    Current_price = 80
    Ask_price = 90
    Bid_price = 70
    Spread = Ask_price - Bid_price

    if Current_price >= Ask_price:
        print("Buy")
    elif Current_price <= Bid_price:
        print("Sell")
    else:
        Deadzone = Bid_price < Current_price < Ask_price
        if Deadzone:
            prices = [80, 80, 80, 80, 80, 80]
            i = len(prices) - 1

            while True:
                current = prices[i]
                previous = prices[i - 1]

                if previous < current:
                    print("Buy")
                    break
                elif previous > current:
                    print("Sell")
                    break
                elif previous == current:
                    i = i - 1
                    if i == 0:
                        print("No Aggressor Side")
                        break
Aggressor_Side_Classification()
    