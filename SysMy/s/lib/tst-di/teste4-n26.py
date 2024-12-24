import QuantLib as ql
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import ambima as ambima

def create_brazil_calendar():
    """
    Cria um calendário brasileiro considerando os feriados nacionais.
    """
    brazil = ql.Brazil()
    return brazil

def get_next_business_day(date, calendar):
    """
    Retorna o próximo dia útil após uma data específica.
    
    Args:
        date: Data em formato datetime
        calendar: Objeto Calendar do QuantLib
    """
    ql_date = ql.Date(date.day, date.month, date.year)
    next_business = calendar.adjust(ql_date, ql.Following)
    return datetime(next_business.year(), next_business.month(), next_business.dayOfMonth())

def create_copom_schedule():
    """
    Cria um DataFrame com as datas das reuniões do COPOM e suas respectivas taxas.
    Inclui uma coluna para indicar se a taxa foi definida manualmente.
    """
    copom_dates = [
        datetime(2024, 12, 11),  # 267ª reunião
        datetime(2025, 1, 29),   # 268ª reunião
        datetime(2025, 3, 19),   # 269ª reunião
        datetime(2025, 5, 7),    # 270ª reunião
        datetime(2025, 6, 18),   # 271ª reunião
        datetime(2025, 7, 30),   # 272ª reunião
        datetime(2025, 9, 17),   # 273ª reunião
        datetime(2025, 11, 5),   # 274ª reunião
        datetime(2025, 12, 10),  # 275ª reunião
        datetime(2026, 1, 28),   # 1ª reunião 2026
        datetime(2026, 3, 18),   # 2ª reunião 2026
        datetime(2026, 5, 6),    # 3ª reunião 2026
        datetime(2026, 6, 17)    # 4ª reunião 2026
    ]
    
    return pd.DataFrame({
        'data_reuniao': copom_dates,
        'taxa': None,
        'manual': False  # Indica se a taxa foi definida manualmente
    })

def set_manual_rates(schedule_df, manual_rates):
    """
    Define as taxas especificadas manualmente no DataFrame.
    
    Args:
        schedule_df: DataFrame com as datas das reuniões
        manual_rates: Dicionário com as datas e taxas definidas manualmente
        Ex: {'2025-01-29': 12.25, '2025-03-19': 12.75}
    """
    for date_str, rate in manual_rates.items():
        date = datetime.strptime(date_str, '%Y-%m-%d')
        mask = schedule_df['data_reuniao'].dt.date == date.date()
        if mask.any():
            schedule_df.loc[mask, 'taxa'] = rate
            schedule_df.loc[mask, 'manual'] = True
    return schedule_df

def optimize_remaining_rates(schedule_df, initial_rate, target_rate, calendar):
    """
    Otimiza as taxas não definidas manualmente para atingir a taxa média alvo.
    
    Args:
        schedule_df: DataFrame com as reuniões e taxas manuais já definidas
        initial_rate: Taxa CDI inicial
        target_rate: Taxa alvo a ser atingida
        calendar: Calendário brasileiro
    """
    # Ajusta as datas para o próximo dia útil
    schedule_df['data_efetiva'] = schedule_df['data_reuniao'].apply(
        lambda x: get_next_business_day(x, calendar)
    )
    
    # Identifica reuniões sem taxa definida
    auto_meetings = schedule_df[~schedule_df['manual']].index
    num_auto_meetings = len(auto_meetings)
    
    if num_auto_meetings == 0:
        return schedule_df
    
    # Define a primeira taxa não manual com base na última taxa manual ou taxa inicial
    last_manual_rate = initial_rate
    if schedule_df['manual'].any():
        last_manual_idx = schedule_df[schedule_df['manual']].index.max()
        if last_manual_idx >= 0:
            last_manual_rate = schedule_df.loc[last_manual_idx, 'taxa']
    
    # Calcula o aumento necessário por reunião para as taxas não definidas
    remaining_increase = target_rate - last_manual_rate
    increase_per_meeting = remaining_increase / num_auto_meetings
    
    # Aplica os aumentos graduais
    current_rate = last_manual_rate
    for idx in auto_meetings:
        current_rate += increase_per_meeting
        schedule_df.loc[idx, 'taxa'] = current_rate
    
    return schedule_df

def calculate_average_rate(schedule_df, start_date, end_date, calendar):
    """
    Calcula a taxa média ponderada pelo número de dias úteis.
    """
    weighted_sum = 0
    total_days = 0
    
    dates = [start_date] + list(schedule_df['data_efetiva']) + [end_date]
    rates = [schedule_df['taxa'].iloc[0]] + list(schedule_df['taxa']) + [schedule_df['taxa'].iloc[-1]]
    
    for i in range(len(dates) - 1):
        ql_start = ql.Date(dates[i].day, dates[i].month, dates[i].year)
        ql_end = ql.Date(dates[i+1].day, dates[i+1].month, dates[i+1].year)
        
        business_days = calendar.businessDaysBetween(ql_start, ql_end)
        weighted_sum += rates[i] * business_days
        total_days += business_days
    
    return weighted_sum / total_days if total_days > 0 else 0

def main():
    # Parâmetros iniciais
    initial_date = datetime(2024, 12, 23)
    final_date = datetime(2026, 7, 1)
    initial_rate = 12.25  # CDI atual
    target_rate = 15.530  # Taxa DI1N26
    
    # Taxas definidas manualmente (exemplo)
    manual_rates = {
        '2024-12-11': 12.25,  # já foi
        '2025-01-29': 13.25,  # Estimado na ata do copom
        '2025-03-19': 14.25,  # Estimado na ata do copom
        '2025-05-07': 15.25,  # Considerando estimativa da skopus de selic terminal 15,50
        '2025-06-18': 15.50   # sendo um pouco mais agressivo considerando o din26 alto  
    }
    
    # Criar calendário brasileiro
    calendar = create_brazil_calendar()
    
    ## Calcular a quantidade de dias úteis entre 01/01/2024 e 31/12/2024
    # Para testar diferença entre QuantLib e Ambima (no restuldo do teste com 2024 e 2025 não deu diferença)
    start_date = ql.Date(1, 1, 2024)
    end_date = ql.Date(31, 12, 2024)
    business_days = calendar.businessDaysBetween(start_date, end_date)
    business_days_ambima = ambima.dias_uteis(datetime(2024, 1, 1).date(), datetime(2024, 12, 31).date())
    print(f"Quantidade de dias úteis entre 01/01/2024 e 31/12/2024: {business_days} (QuantLib) {business_days_ambima} (Ambima)")
    
    # Criar cronograma de reuniões
    schedule_df = create_copom_schedule()
    
    # Definir taxas manuais
    schedule_df = set_manual_rates(schedule_df, manual_rates)
    
    # Otimizar taxas restantes
    rates_df = optimize_remaining_rates(schedule_df, initial_rate, target_rate, calendar)
    
    # Calcular taxa média
    average_rate = calculate_average_rate(rates_df, initial_date, final_date, calendar)
    
    # Exibir resultados
    print("\nProjeção de taxas por reunião do COPOM:")
    for _, row in rates_df.iterrows():
        taxa_tipo = "(Manual)" if row['manual'] else "(Calculada)"
        print(f"Data: {row['data_efetiva'].strftime('%d/%m/%Y')} - Taxa: {row['taxa']:.3f}% {taxa_tipo}")
    
    print(f"\nTaxa média no período: {average_rate:.3f}%")
    print(f"Taxa alvo (DI1N26): {target_rate}%")
    print(f"Diferença: {abs(average_rate - target_rate):.3f}%")

if __name__ == "__main__":
    main()