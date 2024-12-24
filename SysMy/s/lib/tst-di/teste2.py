import QuantLib as ql
import matplotlib.pyplot as plt

# Data de referência (atualize conforme necessário)
data_hoje = ql.Date(21, ql.December, 2023)  # Deve ser antes dos vencimentos fornecidos
ql.Settings.instance().evaluationDate = data_hoje

# Vencimentos e taxas DI
vencimentos_str_di = ["2025-01-01", "2025-07-01", "2026-01-01", "2026-07-01",
                      "2027-01-01", "2028-01-01", "2029-01-01", "2030-01-01",
                      "2031-01-01", "2033-01-01", "2034-01-01", "2035-01-01",
                      "2037-01-01"]
taxas_di = [0.12165, 0.14020, 0.14930, 0.15165, 0.15060, 0.14850, 0.14630,
            0.14470, 0.14320, 0.14090, 0.13950, 0.13880, 0.13700]

# Converter vencimentos para objetos QuantLib
vencimentos_di = [ql.DateParser.parseISO(date) for date in vencimentos_str_di]

# Verificar e ajustar vencimentos para estarem no futuro
if any(venc < data_hoje for venc in vencimentos_di):
    raise ValueError("Alguns vencimentos estão no passado em relação à data de referência!")

# Day Count - Usar 252 dias úteis por padrão (compatível com mercado brasileiro)
day_count = ql.ActualActual(ql.ActualActual.ISDA)

# Criar um calendário para refletir os dias úteis brasileiros
calendario = ql.Brazil()

# Criar instrumentos para os vencimentos e taxas
helpers = [
    ql.DepositRateHelper(
        ql.QuoteHandle(ql.SimpleQuote(taxa)),
        ql.Period(ql.Date.serialNumber(venc) - ql.Date.serialNumber(data_hoje), ql.Days),
        0,  # Sem fixing days para os depósitos
        calendario,
        ql.ModifiedFollowing,
        False,
        day_count
    )
    for taxa, venc in zip(taxas_di, vencimentos_di)
]

# Criar a curva com interpolação cúbica logarítmica
curve = ql.PiecewiseLogCubicDiscount(data_hoje, helpers, day_count)
curve.enableExtrapolation()

# Criar um handle da curva
curve_handle = ql.YieldTermStructureHandle(curve)

# Obter pontos para o gráfico
dates = [data_hoje + i * 30 for i in range(0, 400)]  # Pular a cada 30 dias corridos
rates = [curve.zeroRate(d, day_count, ql.Compounded, ql.Annual).rate() for d in dates]

# Plotar a curva
dates_plot = [ql.Date.to_date(d) for d in dates]
plt.figure(figsize=(10, 6))
plt.plot(dates_plot, rates, label="Curva de Juros DI (Base 252 Ajustada)")
plt.scatter([ql.Date.to_date(d) for d in vencimentos_di], taxas_di, color='red', label="Taxas fornecidas")
plt.xlabel("Data")
plt.ylabel("Taxa (%)")
plt.title("Curva de Juros DI Futuros (Base 252)")
plt.legend()
plt.grid()
plt.show()
