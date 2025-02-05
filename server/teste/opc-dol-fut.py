import MetaTrader5 as mt5
# display data on the MetaTrader 5 package
print("MetaTrader5 package author: ",mt5.__author__)
print("MetaTrader5 package version: ",mt5.__version__)
 
# establish connection to the MetaTrader 5 terminal
if not mt5.initialize():
    print("initialize() failed, error code =",mt5.last_error())
    quit()
 

# get symbols containing RU in their names
ru_symbols=mt5.symbols_get("DOLH25*")
print('len(DOL*): ', len(ru_symbols))
for s in ru_symbols:
    print(s.name)
print()
 
 
# shut down connection to the MetaTrader 5 terminal
mt5.shutdown()