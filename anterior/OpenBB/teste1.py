

# Importar OpenBB SDK e Plotly
from openbb import obb
import pandas as pd
from plotly import graph_objects as go

# Definir o ticker da Petrobras
ticker = "PETR4.SA"

# Obter dados históricos da ação
stock_data = obb.equity.price.historical(symbol=ticker, start_date="2023-01-01", provider="yfinance")

# Converter os dados históricos em um DataFrame do Pandas
df = pd.DataFrame(stock_data.results)

# Calcular VWAP usando a função do OpenBB
vwap_data = obb.technical.vwap(data=stock_data.results, anchor='D', offset=0)

# Criar o gráfico de candlestick
candlestick = go.Candlestick(
    x=df['date'],
    open=df['open'],
    high=df['high'],
    low=df['low'],
    close=df['close'],
    name='Candlestick'
)

# Adicionar a linha VWAP ao gráfico
vwap_line = go.Scatter(
    x=df['date'],
    y=vwap_data['vwap'],
    mode='lines',
    line=dict(color='blue', width=2),
    name='VWAP'
)

# Plotar o gráfico com Candlestick e VWAP
fig = go.Figure(data=[candlestick, vwap_line])

# Adicionar título e ajustar layout
fig.update_layout(
    title=f'Candlestick Chart com VWAP - {ticker}',
    xaxis_title='Data',
    yaxis_title='Preço',
    xaxis_rangeslider_visible=False
)

# Mostrar o gráfico
fig.show()