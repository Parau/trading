import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# Dados fornecidos
vencimentos_str_di = ["2025-01-01", "2025-07-01", "2026-01-01", "2026-07-01",
                      "2027-01-01", "2028-01-01", "2029-01-01", "2030-01-01",
                      "2031-01-01", "2033-01-01", "2034-01-01", "2035-01-01",
                      "2037-01-01"]

vencimentos_di = [datetime.strptime(date, "%Y-%m-%d") for date in vencimentos_str_di]

taxas_di = [0.12165, 0.14020, 0.14930, 0.15165, 0.15060, 0.14850, 0.14630,
            0.14470, 0.14320, 0.14090, 0.13950, 0.13880, 0.13700]

dados_selic = [
    {"tipo": "realizado", "data": "2024-02-01", "taxa_selic": 11.25},
    {"tipo": "realizado", "data": "2024-03-21", "taxa_selic": 10.75},
    {"tipo": "realizado", "data": "2024-05-09", "taxa_selic": 10.50},
    {"tipo": "realizado", "data": "2024-06-20", "taxa_selic": 10.50},
    {"tipo": "realizado", "data": "2024-08-01", "taxa_selic": 10.50},
    {"tipo": "realizado", "data": "2024-09-19", "taxa_selic": 10.75},
    {"tipo": "realizado", "data": "2024-11-07", "taxa_selic": 11.25},
    {"tipo": "realizado", "data": "2024-12-12", "taxa_selic": 12.25},
    {"tipo": "estimado", "data": "2025-02-01", "taxa_selic": 13.25},
    {"tipo": "estimado", "data": "2025-03-21", "taxa_selic": 14.25},
    {"tipo": "estimado", "data": "2025-05-09", "taxa_selic": 14.75},
    {"tipo": "estimado", "data": "2025-06-20", "taxa_selic": 15.00},
    {"tipo": "estimado", "data": "2025-08-01", "taxa_selic": 15.00},
    {"tipo": "estimado", "data": "2025-09-19", "taxa_selic": 15.00},
    {"tipo": "estimado", "data": "2025-11-07", "taxa_selic": 15.00},
    {"tipo": "estimado", "data": "2025-12-12", "taxa_selic": 15.00}
]

# Prepara os dados da Selic
datas_selic = [datetime.strptime(item["data"], "%Y-%m-%d") for item in dados_selic]
taxas_selic = [item["taxa_selic"] / 100 for item in dados_selic]

# Calcula as taxas spot implícitas
def calcula_taxas_spot(vencimentos, taxas_di):
    taxas_spot = []
    for i in range(len(taxas_di)):
        if i == 0:
            taxas_spot.append(taxas_di[i])
        else:
            t_anterior = (vencimentos[i - 1] - vencimentos[0]).days / 252
            t_atual = (vencimentos[i] - vencimentos[0]).days / 252
            taxa_anterior = taxas_spot[i - 1]
            taxa_atual = taxas_di[i]

            # Evitar overflow usando logaritmos para os cálculos
            if abs(t_atual - t_anterior) < 1e-6:
                spot = taxa_atual
            else:
                try:
                    log_term = (np.log(1 + taxa_atual) * t_atual - np.log(1 + taxa_anterior) * t_anterior)
                    spot = np.exp(log_term / (t_atual - t_anterior)) - 1
                except OverflowError:
                    spot = taxa_atual  # Fallback seguro em caso de erro

            # Validação para evitar valores nulos ou negativos
            if spot < 0:
                print(f"Aviso: Taxa spot negativa calculada para índice {i}. Usando taxa_atual como fallback.")
                spot = taxa_atual

            taxas_spot.append(spot)
    return taxas_spot

# Depuração: Imprimir taxas spot
print("Taxas Spot Calculadas:")
taxas_spot = calcula_taxas_spot(vencimentos_di, taxas_di)
for i, spot in enumerate(taxas_spot):
    print(f"Vencimento: {vencimentos_str_di[i]}, Spot: {spot:.6f}")

# Plota o gráfico
plt.figure(figsize=(12, 6))

# Selic
plt.plot(datas_selic, taxas_selic, marker="o", label="Selic (realizada e estimada)")

# Taxas DI Futuro
plt.plot(vencimentos_di, taxas_di, marker="x", label="Taxas DI Futuro")

# Taxas Spot
plt.plot(vencimentos_di, taxas_spot, marker="d", label="Taxas Spot Implícitas")

# Configurações do gráfico
plt.title("Taxa Selic, Contratos DI Futuros e Taxas Spot")
plt.xlabel("Data")
plt.ylabel("Taxa (%)")
plt.legend()
plt.grid(True)
plt.tight_layout()

# Exibe o gráfico
plt.show()
