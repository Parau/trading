def calculate_volume_profile(df):
    # Agregar OI por níveis de preço
    price_levels = pd.IntervalIndex.from_arrays(
        df['Strike'] - 0.025,
        df['Strike'] + 0.025
    )
    
    volume_profile = df.groupby(pd.cut(df['Strike'], price_levels))['OI'].sum()
    return volume_profile