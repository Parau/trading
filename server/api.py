from flask import Blueprint, jsonify, request
from datetime import datetime
import time
import sys
sys.path.append('./lib')
import di  
import MT5

from OptionsAnalysis.analysis import OptionsAnalysis
import os
import glob

api = Blueprint('api', __name__)

@api.route('/api/last-ticker-data', methods=['GET'])
def get_ticker_data():
    ticker_names = request.args.getlist('tickerName')
    updates = {}
    for ticker in ticker_names:
        if ticker == "CDI":
            updates[ticker] = {
                'time': int(time.time()),
                'bid': 12.25,
                'ask': 12.25,
                'last': 12.25,
                'volume': 0
            }
        else:
            update = MT5.get_real_time_tick2(ticker)
            if update:
                updates[ticker] = update
    return jsonify(updates)

@api.route('/api/historical-ticker-data', methods=['GET'])
def get_historical_ticker_data():
    ticker = request.args.get('tickerName')
    minutes = request.args.get('minutes', default=60, type=int)
    
    if not ticker:
        return jsonify({'error': 'tickerName is required'}), 400
        
    if ticker == "CDI":
        return jsonify({'error': 'Historical data not available for CDI'}), 400
    
    historical_data = MT5.get_historical_data(ticker) 
    if historical_data is None:
        return jsonify({'error': f'No historical data found for {ticker}'}), 404
        
    return jsonify(historical_data)

@api.route('/api/dolar-options', methods=['GET'])
def get_dolar_options():


    # Get list of CSV files in the opcoes_dolar directory
    calls_pattern = 'data/opcoes_dolar/*_DOL_OP_Call.csv'
    puts_pattern = 'data/opcoes_dolar/*_DOL_OP_Put.csv'
    
    # Get the most recent files
    calls_file = max(glob.glob(calls_pattern))
    puts_file = max(glob.glob(puts_pattern))
    
    print(f'Calls file: {calls_file} and Puts file: {puts_file}')
    analyzer = OptionsAnalysis(5.80, "H25", calls_file, puts_file)
    df = analyzer.getOptionsData()
    
    # Convert DataFrame to dict and format response
    result = {
        'options': df[['Strike', 'OI', 'Tipo']].to_dict(orient='records'),
        'timestamp': int(time.time())
    }
    
    return jsonify(result)

@api.route('/api/estimate-cdi', methods=['GET'])
def get_CDI_estimate():
    ticker = request.args.get('ticker')
    target_rate = request.args.get('target_rate', type=float)
    
    if not ticker or target_rate is None:
        return jsonify({'error': 'Ticker and target_rate are required'}), 400
    
    initial_date = datetime.now().date()
    
    ticker_dates = {
        "DI1N24": datetime(2024, 7, 1).date(),
        "DI1F25": datetime(2025, 1, 2).date(),
        "DI1N25": datetime(2025, 7, 1).date(),
        "DI1F26": datetime(2026, 1, 2).date(),
        "DI1N26": datetime(2026, 7, 1).date(),
        "DI1F27": datetime(2027, 1, 4).date(),
        "DI1F28": datetime(2028, 1, 3).date(),
        "DI1F29": datetime(2029, 1, 2).date(),
        "DI1F30": datetime(2030, 1, 2).date(),
        "DI1F31": datetime(2031, 1, 2).date()
    }

    final_date = ticker_dates.get(ticker)
    if not final_date:
        return jsonify({'error': 'Invalid ticker'}), 400

    initial_rate = 12.25  
    resultado = di.EstimaCDI(initial_rate, target_rate, initial_date, final_date)
    resultado_dict = resultado.to_dict(orient='records')

    return jsonify({'result': resultado_dict})



"""
######################################
# DESCONTINUADO
# API endpoint for initial data
@app.route('/api/initial-data', methods=['GET'])
def get_initial_data():
  print('get_initial_data')
  initial_data = get_historical_data()
  return jsonify(initial_data)
  #initial_data = [generate_candlestick_data() for _ in range(2500)]
  #return jsonify(initial_data)

# updated-data
# API endpoint for real-time updated data
@app.route('/api/updated-data', methods=['GET'])
def get_updated_data():
    #updated_data = get_real_time_tick()
    update = get_lastbar_data()
    #print(update)
    if update:
      return jsonify(update)
    return jsonify(None)
######################################
"""