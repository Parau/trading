from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS

import pandas as pd
import random
import time
from datetime import datetime
import sys
sys.path.append('./lib')
import di as di
from api import get_ticker_data, get_CDI_estimate, get_historical_ticker_data


app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Load configuration settings if any
# app.config.from_object('config.Config')

app.add_url_rule('/api/last-ticker-data', view_func=get_ticker_data, methods=['GET'])
app.add_url_rule('/api/estimate-cdi', view_func=get_CDI_estimate, methods=['GET'])
app.add_url_rule('/api/historical-ticker-data', view_func=get_historical_ticker_data, methods=['GET'])


######################################
# homepage
@app.route("/")
def pagina_inicial():
  print('get_initial_data')
  return send_from_directory('./', 'index.html')
# SnP
@app.route("/WSPFUT")
def wsp_fut():
  return send_from_directory('cli', 'graficoWSPFUT.html')
# DI
@app.route("/DI")
def di_fut():
  return send_from_directory('cli', 'DI.html')






