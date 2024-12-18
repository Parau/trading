import requests

url = "https://simulador.b3.com.br/api/cors-app/web/V1.0/RiskCalculation"

headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
    "Content-Type": "application/json",
    "Cookie": "_ga_0W7NXV5699=GS1.1.1713950441.1.0.1713950523.0.0.0; visid_incap_2246223=6pK2d5ojRWG8IpdQwIfwKJtzKWYAAAAAQUIPAAAAAACmdJhzk+G9SXCZjBr40YEX; _fbp=fb.2.1713992616497.1589545696; OptanonAlertBoxClosed=2024-05-04T12:47:42.002Z; ...",
    "Origin": "https://simulador.b3.com.br",
    "Referer": "https://simulador.b3.com.br/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
}

data = {
    "ReferenceData": {
        "referenceDataToken": "7ec5ab293526937a70bd40c14bec2b37"
    },
    "LiquidityResource": {
        "value": 6100000000
    },
    "RiskPositionList": [
        {
            "Security": {
                "symbol": "PETR4"
            },
            "SecurityGroup": {
                "positionTypeCode": 0
            },
            "Position": {
                "longQuantity": 0,
                "shortQuantity": 100,
                "tradeDate": "2024-12-10",
                "longPrice": 0,
                "shortPrice": 40.19
            }
        }
    ]
}

response = requests.post(url, headers=headers, json=data, verify=False) #tive que desligar o certificado, não sei se dá para mudar alguma coisa aqui.

print("Status Code:", response.status_code)
print("Response:", response.json())