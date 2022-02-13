from __future__ import print_function

import os.path
import csv
import pandas as pd
import sys, getopt


def main(argv):
   inputfile = ''
   outputfile = ''
   taxyear=''
   try:
      opts, args = getopt.getopt(argv,"hi:o:",["ifile=","taxyear="])
   except getopt.GetoptError:
      print ('test.py -i <inputfile> -y <taxyear>')
      sys.exit(3)
   for opt, arg in opts:
      if opt == '-h':
         print ('test.py -i <inputfile> -y <taxyear>')
         sys.exit()
      elif opt in ("-i", "--ifile"):
         inputfile = arg
      elif opt in ("-y", "--taxyear"):
         taxyear = arg
   print ('Input file is "', inputfile)
   print ('taxyear file is:', taxyear) 
   df = pd.read_csv(inputfile,parse_dates=[0])
   df['matched']=False
   df['quantity_remaining'] = df['size']

   df_sell= df.query('side == "SELL"', inplace = False)
   df_buy = df.query('side == "BUY"', inplace = False)
   matchBuySell(df,taxyear)




#portfolio,trade id,product,side,created at,size,size unit,price,fee,total,price/fee/total unit    
# Consumes coin base pro fill statements




def matchBuySell(df,taxyear):
    sell_count=0
    txIndex=0
    profit_2021=0
    profit_2022=0
    format = "%Y-%m-%dT%H:%M:%S.%fZ"
    df['year'] = pd.to_datetime(df['created at'],format=format).dt.year
    for ind in df.index:
        side = df['side'][ind]
        txn_year = df['year'][ind]
        #created_year = pd. DatetimeIndex(df['created at'][ind]).year
        
       


        
        if(side =='SELL' ):
            sell_size = df['size'][ind]
            sell_price = df['price'][ind]
            sell_total = df['total'][ind]
            sell_created_at = df['created at'][ind]
            sell_fees = df['fee'][ind]
            sell_tax_year = df['year'][ind]
            #print ('--------------------')
            #print ('Sell transaction' + " - " + str(side) + " - " + str(sell_size) + " - " + str(sell_price) + "- " + str(sell_tax_year) )
            sell_count = sell_count + 1
            txIndex = ind
            matchBuy=False
            #Traverse upwards to find matching transaction and mark it as matched. Employs LIFO match strategy, other strategies are minimize profit, FIFO
            for num in range(txIndex, -1, -1) :
                if df['side'][num] == "BUY":
                    matchChar=""
                    buy_price = df['price'][num]
                    buy_fees = df['fee'][num]
                    #print ("Matching..."  + df['side'][num] + " - " + str(df['size'][num]) + " -"  + str(buy_price) + " - " + df['created at'][num] +  " -Remaining query " + str(df['quantity_remaining'][num] )  + matchChar) 
                    if df['quantity_remaining'][num] > 0: # This transaction has not be been touched before
                       quantity_to_subtraced = df['quantity_remaining'][num]  - sell_size # Subtract quantity remaining of the buy transaction - sell size
                       if quantity_to_subtraced >= 0: #buy transaction has enough size to support the sell transaction fully
                         quantity_remaining = df['quantity_remaining'][num]  - sell_size
                          
                         sell_tx_profit = ((sell_price - buy_price)*sell_size) - sell_fees - buy_fees
                         if(sell_tax_year == 2021):
                            profit_2021 = profit_2021 + sell_tx_profit
                         if(sell_tax_year == 2022):
                            profit_2022 = profit_2022 + sell_tx_profit
                         df['quantity_remaining'][num] = quantity_remaining     
                         #print ("Matched..." + df['side'][num] + " - " + str(df['size'][num]) + " -"  + str(buy_price) + " - " + df['created at'][num] +  " -Remaining quantity " + str(df['quantity_remaining'][num] )  +  " Txn Profit =" + str(sell_tx_profit)) 
                         #print ("Cumulative profit so far: " + profit)
                         break # sell transaction is fully matched
                       else: #buy transaction does not enough size to support the sell transaction fully
                         qt_remaining_in_buy_txn = df['quantity_remaining'][num] 
                         sell_size  = sell_size - qt_remaining_in_buy_txn #subtract sell size - buy quantiy left. This size carries over
                         #TODO need to calculate profit
                         sell_tx_profit = ((sell_price - buy_price)*qt_remaining_in_buy_txn) - sell_fees - buy_fees
                         if(sell_tax_year == 2021) :
                            profit_2021 = profit_2021 + sell_tx_profit
                         if(sell_tax_year == 2022):
                            profit_2022 = profit_2022 + sell_tx_profit
                         df['quantity_remaining'][num] = 0 # set remaining buy quanity to 0
                         #print('buy transaction has lesser quantity than needed to fully match sell transaction' + " Carry-over " + str(sell_size) + " Quantity remaining in this buy transaction " + str(df['quantity_remaining'][num]))
                        
    #printdf(df,"BUY")
    #print(df)
    df_buy = df.query('side == "BUY" and quantity_remaining > 0', inplace = False)
    print(df_buy)
    print ("Total buy Amount left " + str(df_buy['quantity_remaining'].sum()))
    over_all_profit = profit_2021 + profit_2022
    print("2021_Profit= " + str(profit_2021) + " 2022_Profit= " + str(profit_2022) +  " Overall profit =" + str(over_all_profit))
                   



        


if __name__ == '__main__':
    main(sys.argv[1:])
