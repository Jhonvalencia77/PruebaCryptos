from flask import Flask, render_template, request, jsonify
from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import threading
import time

app = Flask(__name__)

# Variable global para almacenar los datos
dataBitCoin = {'data': []}

def fetch_data():
    global dataBitCoin
    api_key = 'd1c51888-744b-4368-82c9-e8ff4f3ab22b'  # Asegúrate de proteger esta clave
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
    parameters = {
        'start': '1',
        'limit': '10',
        'convert': 'USD'
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': api_key,
    }

    session = Session()
    session.headers.update(headers)

    try:
        response = session.get(url, params=parameters)
        dataBitCoin = json.loads(response.text)
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', data=dataBitCoin['data'])

@app.route('/update', methods=['GET'])
def update_data():
    global dataBitCoin
    fetch_data()
    return jsonify({"message": "Data updated successfully", "data": dataBitCoin['data']})

@app.route("/cryptos/", methods=['GET'])
def get_cryptos():
    return jsonify(dataBitCoin)

@app.route("/cryptos/<int:id>", methods=['GET'])
def get_crypto(id): 
    crypto_id = None 
    for crypto in dataBitCoin['data']:
        if crypto['id'] == id:
            crypto_id = crypto
            break
    if crypto_id is not None:
        return jsonify(crypto_id)
    else:
        return jsonify({"error": "not found"}), 404 

@app.route('/api/cryptocurrency', methods=['GET'])
def api_cryptocurrency():
    fetch_data()  # Llama a la función para actualizar los datos desde la API
    return jsonify(dataBitCoin)

if __name__ == '__main__':
    def auto_update_data():
        while True:
            fetch_data()
            time.sleep(300)  # Actualiza cada 5 minutos

    data_thread = threading.Thread(target=auto_update_data)
    data_thread.daemon = True
    data_thread.start()

    app.run(port=4000, debug=True)

