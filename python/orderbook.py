import MetaTrader5 as mt5
import time
from datetime import datetime, timedelta

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
intervalo = 5

# Define o intervalo de captura (últimos 10 segundos)
intervalo_captura = timedelta(seconds=10)

# Armazena o horário da última captura
ultima_captura = datetime.now() - intervalo_captura

orderType = {}
orderType[mt5.BOOK_TYPE_SELL] = "sell"
orderType[mt5.BOOK_TYPE_BUY] = "buy"
orderType[mt5.BOOK_TYPE_SELL_MARKET] = "sell by mkt"
orderType[mt5.BOOK_TYPE_BUY_MARKET] = "buy by mkt"


try:
    while True:
        ####################################################
        # Captura o Depth of Market novamente
        book = mt5.market_book_get(symbol)

        if book is None:
            print(f"Sem dados do Book de Ofertas para {symbol}")
        else:
            print(f"\nBook de Ofertas para {symbol} atualizado:")
            for order in book:
              print(f"{orderType[order.type]} - Preço: {order.price}, Volume: {order.volume}")

        ########################################################
        # Captura o tick atual (cotação) do ativo
        tick = mt5.symbol_info_tick(symbol)

        if tick is None:
            print(f"Não foi possível obter a cotação atual para {symbol}")
        else:
            print(f"Cotação atual de {symbol}:")
            print(f"  Preço de compra (bid): {tick.bid}")
            print(f"  Preço de venda (ask): {tick.ask}")
            print(f"  Último preço (last): {tick.last}")

        ########################################################
        # Captura o intervalo de tempo (do último momento até agora)
        time_from = ultima_captura
        time_to = datetime.now()

        # Obtém o histórico de ordens executadas (deals) no intervalo
        deals = mt5.history_deals_get(time_from, time_to, "WSP")

        if deals is not None and len(deals) > 0:
            print(f"Novas ordens executadas encontradas ({len(deals)}):")
            for deal in deals:
                print(f"Ordem executada: Ticket: {deal.ticket}, Símbolo: {deal.symbol}, "
                      f"Volume: {deal.volume}, Preço: {deal.price}, Tipo: {deal.type}, Data: {deal.time}")

        else:
            print("Nenhuma nova execução de ordem")

        # Atualiza o horário da última captura
        ultima_captura = time_to


        # Aguarda o próximo intervalo
        time.sleep(intervalo)

except KeyboardInterrupt:
    print("Encerrando a captura de dados...")
finally:
    mt5.shutdown()