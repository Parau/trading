def analyze_term_structure(dfs_by_expiry):
    """
    Análise da estrutura a termo das barreiras
    dfs_by_expiry: dict com DataFrames de diferentes vencimentos
    """
    term_structure = {}
    
    for expiry, df in dfs_by_expiry.items():
        term_structure[expiry] = {
            'total_oi': df['OI'].sum(),
            'main_strikes': df.nlargest(5, 'OI')['Strike'].tolist(),
            'put_call_ratio': (
                df[df['Tipo'] == 'Put']['OI'].sum() /
                df[df['Tipo'] == 'Call']['OI'].sum()
            )
        }
    
    return term_structure