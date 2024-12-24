import pandas as pd
import matplotlib.pyplot as plt
import QuantLib as ql

dados_selic = [
    {"tipo": "realizado", "data": "2024-02-01", "reuniao": "30 e 31 de janeiro de 2024", "taxa_selic": 11.25, "variacao": -0.50},
    {"tipo": "realizado", "data": "2024-03-21", "reuniao": "19 e 20 de março", "taxa_selic": 10.75, "variacao": -0.50},
    {"tipo": "realizado", "data": "2024-05-09", "reuniao": "7 e 8 de maio", "taxa_selic": 10.50, "variacao": -0.25},
    {"tipo": "realizado", "data": "2024-06-20", "reuniao": "18 e 19 de junho", "taxa_selic": 10.50, "variacao": 0.00},
    {"tipo": "realizado", "data": "2024-08-01", "reuniao": "30 e 31 de julho", "taxa_selic": 10.50, "variacao": 0.00},
    {"tipo": "realizado", "data": "2024-09-19", "reuniao": "17 e 18 de setembro", "taxa_selic": 10.75, "variacao": 0.25},
    {"tipo": "realizado", "data": "2024-11-07", "reuniao": "5 e 6 de novembro", "taxa_selic": 11.25, "variacao": 0.50},
    {"tipo": "realizado", "data": "2024-12-12", "reuniao": "10 e 11 de dezembro", "taxa_selic": 12.25, "variacao": 1.00},
    {"tipo": "estimado", "data": "2025-02-01", "reuniao": "28 e 29 de janeiro", "taxa_selic": 13.25, "variacao": 1.00},
    {"tipo": "estimado", "data": "2025-03-21", "reuniao": "18 e 19 de março", "taxa_selic": 14.25, "variacao": 1.00},
    {"tipo": "estimado", "data": "2025-05-09", "reuniao": "6 e 7 de maio", "taxa_selic": 14.75, "variacao": 0.50},
    {"tipo": "estimado", "data": "2025-06-20", "reuniao": "17 e 18 de junho", "taxa_selic": 15.00, "variacao": 0.25},
    {"tipo": "estimado", "data": "2025-08-01", "reuniao": "29 e 30 de julho", "taxa_selic": 15.00, "variacao": 0.00},
    {"tipo": "estimado", "data": "2025-09-19", "reuniao": "16 e 17 de setembro", "taxa_selic": 15.00, "variacao": 0.00},
    {"tipo": "estimado", "data": "2025-11-07", "reuniao": "4 e 5 de novembro", "taxa_selic": 15.00, "variacao": 0.00},
    {"tipo": "estimado", "data": "2025-12-12", "reuniao": "9 e 10 de dezembro", "taxa_selic": 15.00, "variacao": 0.00},
    {"tipo": "estimado", "data": "2026-02-01", "reuniao": "data estimada", "taxa_selic": 15.00, "variacao": 0.00},
    {"tipo": "estimado", "data": "2026-03-21", "reuniao": "data estimada", "taxa_selic": 15.00, "variacao": 0.00},
    {"tipo": "estimado", "data": "2026-05-09", "reuniao": "data estimada", "taxa_selic": 15.00, "variacao": 0.00},
    {"tipo": "estimado", "data": "2026-06-20", "reuniao": "data estimada", "taxa_selic": 15.00, "variacao": 0.00},
    {"tipo": "estimado", "data": "2026-08-01", "reuniao": "data estimada", "taxa_selic": 15.00, "variacao": 0.00},
    {"tipo": "estimado", "data": "2026-09-19", "reuniao": "data estimada", "taxa_selic": 15.00, "variacao": 0.00},
    {"tipo": "estimado", "data": "2026-11-07", "reuniao": "data estimada", "taxa_selic": 15.00, "variacao": 0.00},
    {"tipo": "estimado", "data": "2026-12-12", "reuniao": "data estimada", "taxa_selic": 15.00, "variacao": 0.00},
]

df_selic = pd.DataFrame(dados_selic)
df_selic['data'] = pd.to_datetime(df_selic['data'])

# Separando dados realizados e estimados (para o plot de escada)
df_selic_realizado = df_selic[df_selic['tipo'] == 'realizado']
df_selic_estimado = df_selic[df_selic['tipo'] == 'estimado']

# --- Dados dos DI Futuros (EXTRAÍDOS DA IMAGEM) ---
data_hoje = ql.Date(21, ql.December, 2023)
vencimentos_str_di = ["2025-01-01", "2025-07-01", "2026-01-01", "2026-07-01", "2027-01-01", "2028-01-01", "2029-01-01", "2030-01-01", "2031-01-01", "2033-01-01", "2034-01-01", "2035-01-01", "2037-01-01"]
taxas_di = [0.12165, 0.14020, 0.14930, 0.15165, 0.15060, 0.14850, 0.14630, 0.14470, 0.14320, 0.14090, 0.13950, 0.13880, 0.13700]

# --- Configuração do QuantLib ---
ql.Settings.instance().evaluationDate = data_hoje

# --- Construindo a curva DI Futuro (QuantLib) ---
helpers_di = []
for vencimento_str, taxa in zip(vencimentos_str_di, taxas_di):
    vencimento = ql.DateParser.parse(vencimento_str, "%Y-%m-%d")
    helper = ql.SimpleQuote(taxa)
    rate_helper = ql.FuturesRateHelper(ql.QuoteHandle(helper), vencimento, ql.Actual365Fixed(), ql.NullCalendar(), ql.Following, ql.Simple)
    helpers_di.append(rate_helper)
helpers_di = []

curve_di = ql.PiecewiseLogCubicDiscount(data_hoje, helpers_di, ql.Actual365Fixed())

# --- Gerando pontos para plotar a curva DI ---
datas_plot_di = [data_hoje + ql.Period(i, ql.Days) for i in range(0, 365*15, 30)]
taxas_plot_di = [curve_di.forwardRate(d, d, ql.Actual365Fixed(), ql.Simple).rate() * 100 for d in datas_plot_di]
datas_plot_di_py = [pd.Timestamp(d.to_date()) for d in datas_plot_di]

# --- Plotando com Matplotlib ---
plt.figure(figsize=(14, 8)) # Aumentei o tamanho da figura

# Curva DI Futuro
plt.plot(datas_plot_di_py, taxas_plot_di, marker='o', label='DI Futuro')

# Selic (plot de escada)
plt.step(df_selic_realizado['data'], df_selic_realizado['taxa_selic'], where='post', marker='o', label='Selic Realizada', color = 'red')
plt.step(df_selic_estimado['data'], df_selic_estimado['taxa_selic'], where='post', marker='x', linestyle='--', label='Selic Estimada', color = 'darkred')
# Conectando o último ponto realizado com o primeiro estimado
plt.step([df_selic_realizado['data'].iloc[-1], df_selic_estimado['data'].iloc[0], ],
         [df_selic_realizado['taxa_selic'].iloc[-1], df_selic_estimado['taxa_selic'].iloc[0]],
         where='post', linestyle='--', color='gray') # Linha tracejada cinza para a conexão

plt.xlabel("Data", fontsize=12)
plt.ylabel("Taxa (%)", fontsize=12)
plt.title("Curva de Juros DI Futuro vs. Selic (Realizada e Estimada)", fontsize=14)
plt.grid(True)
plt.xticks(rotation=45, ha='right')
plt.legend()
plt.tight_layout()
plt.show()