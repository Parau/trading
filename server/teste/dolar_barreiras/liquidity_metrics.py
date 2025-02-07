def calculate_liquidity_score(df):
    # Adiciona análise de spread
    df['Spread'] = df['Última Oferta de Venda'] - df['Última Oferta de Compra']
    
    # Calcula score de liquidez considerando OI e spread
    df['Liquidity_Score'] = (
        df['OI'] / df['OI'].max() * 0.7 +  # Peso de 70% para OI
        (1 - df['Spread'] / df['Spread'].max()) * 0.3  # Peso de 30% para spread
    )
    
    return df