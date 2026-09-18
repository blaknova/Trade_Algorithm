 Method CVD_Calculator(Current_price,Ask_price,Bid_price, prices, volume, timestamp)
        CVD = 0
        WHILE TRUE:
            label = Aggressor_Side_Classification(Current_price, Ask_price, Bid_price,prices)

            if label == "Buy"
                THEN Volume_delta = +volume
            ELSEIF label == "Sell"
                THEN Volume_delta = -volume
            ELSE
                volume_delta = 0   

            IF timestamp >= 1530
                CVD += volume_delta
            ELEIF tmestamp == 2300
                CVD = 0  
        
