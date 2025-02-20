class DolarOption:
    # Mapping of option series to expiration dates
    # https://www.b3.com.br/pt_br/solucoes/plataformas/puma-trading-system/para-participantes-e-traders/calendario-de-negociacao/vencimentos/vencimentos/
    # Mercado: Opções sobre disponível
    # Mercadoria: DOL
    expirations = {
        "H25": "05/03/2025",
        "J25": "01/04/2025",
        "K25": "02/05/2025",
        "M25": "02/06/2025",
        "N25": "01/07/2025",
        "Q25": "01/08/2025",
        "U25": "01/09/2025",
        "V25": "01/10/2025",
        "X25": "03/11/2025",
        "Z25": "01/12/2025",
        "F26": "02/01/2026",
        "G26": "02/02/2026",
        "J26": "01/04/2026",
        "N26": "01/07/2026",
        "V26": "01/10/2026",
        "F27": "04/01/2027",
        "J27": "01/04/2027",
        "N27": "01/07/2027",
        "F28": "03/01/2028",
        "N28": "03/07/2028",
        "F29": "02/01/2029",
        "N29": "02/07/2029",
    }
    
    def __init__(self, series):
        # Ensure series is uppercase for lookup
        self.series = series.upper()
    
    def get_expiration_date(self):
        return DolarOption.expirations.get(self.series, "Série não encontrada")


# Exemplos de uso:
if __name__ == "__main__":
    for s in ["H25", "J25", "N26", "F29", "XYZ"]:
        option = DolarOption(s)
        print(f"Série {s}: {option.get_expiration_date()}")
