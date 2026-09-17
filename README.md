METHOD
    current_price
    Bid
    Ask
    Spread

    if current_price>=Ask
        then buy
    elseif current_price<=Bid
        then sell
    else 
        deadzone
    while in deadzone
        current =price at position i
        previous = price at position i - 1

        if previous < current -> Buy, exit loop
        elsif previous > current -> Sell, exit loop
        elseif(equal)
            i = i - 1    
        elseif i = 0
            setup invalid

