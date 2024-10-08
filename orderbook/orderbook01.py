import MetaTrader5 as mt5
import time
import csv
from datetime import datetime, timedelta


###########################
# Imprimir os significados das flags
def print_flag_description(flag_value):
    # Define the flag constants
    flags = {
        0: "No special flags",
        1: "Last trade tick",
        2: "Last bid tick",
        4: "Last ask tick",
        8: "Last tick for the symbol"
    }
    
    # List to store the descriptions of the active flags
    active_flags = []

    # Check each flag and see if it is active in the flag_value
    for value, description in flags.items():
        if flag_value & value == value:  # Check if the flag is set
            active_flags.append(description)
    
    # Print the results
    if active_flags:
        print(f"Flag {flag_value}: {', '.join(active_flags)}")
    else:
        print(f"Flag {flag_value}: no special flags.")


# Inicializa a conexão ao MetaTrader 5
if not mt5.initialize():
    print("Falha ao inicializar MetaTrader5")
    quit()

# Ativo para monitorar (exemplo: WIN, mini contrato de índice do Ibovespa)
symbol = "WSPZ24"

# Verifica se o ativo está disponível para negociação
if not mt5.symbol_select(symbol, True):
    print(f"Falha ao selecionar o símbolo {symbol}")
    mt5.shutdown()
    quit()

if not mt5.market_book_add(symbol):
    print("mt5.market_book_add('EURUSD') failed, error code =",mt5.last_error())
    mt5.shutdown()
    quit()
    
# Intervalo de tempo entre capturas (em segundos)
intervalo = 1

orderType = {}
orderType[mt5.BOOK_TYPE_SELL] = "sell"
orderType[mt5.BOOK_TYPE_BUY] = "buy"
orderType[mt5.BOOK_TYPE_SELL_MARKET] = "sell by mkt"
orderType[mt5.BOOK_TYPE_BUY_MARKET] = "buy by mkt"

# Abre os arquivos CSV para gravar os dados
orderbook_filename = f"orderbook_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
tick_filename = f"tick_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

orderbook_file = open(orderbook_filename, mode='w', newline='')
tick_file = open(tick_filename, mode='w', newline='')

orderbook_writer = csv.writer(orderbook_file)
tick_writer = csv.writer(tick_file)

# Escreve os cabeçalhos nos arquivos CSV
orderbook_writer.writerow(['Timestamp', 'Type', 'Price', 'Volume'])
tick_writer.writerow(['Timestamp', 'Last', 'Bid', 'Ask', 'Volume', 'Flags'])

try:
    while True:
        ###############
        # Captura dados
        timestamp = datetime.now()
        # Captura o Depth of Market novamente
        book = mt5.market_book_get(symbol)
        # Captura o tick atual (cotação) do ativo
        tick = mt5.symbol_info_tick(symbol)

        ###############
        # Verifica se ocorreu algum erro na captura
        bookETicket = 0;
        if book is None:
            print(f"Sem dados do Book de Ofertas para {symbol}")
        else:
            print(f'Capturado book em:{timestamp}');
            bookETicket += 1

        if tick is None:
            print(f"Não foi possível obter a cotação atual para {symbol}")
        else:
            print(f"Último preço (last): {tick.last}")
            bookETicket += 1

        ###############
        # Grava somente se os dois dados foram capturados
        #if bookETicket == 2:
            # Grava book em um arquivo CSV
            for entry in book:
                orderbook_writer.writerow([timestamp, entry.type, entry.price, entry.volume])
            
            # Grava tick em um arquivo CSV
            tick_writer.writerow([timestamp, tick.last, tick.bid, tick.ask, tick.volume, tick.flags])
            print_flag_description(tick.flags)

        # Aguarda o próximo intervalo
        time.sleep(intervalo)

except KeyboardInterrupt:
    print("Interrompendo captura de dados... (teclado)")
finally:
    print("Encerrando a captura de dados...")
    print("Fechando arquivos.")
    orderbook_file.close()
    tick_file.close()
    print('Liberando MT5')
    mt5.market_book_release(symbol)    
    mt5.shutdown()
    print('Encerrado!')