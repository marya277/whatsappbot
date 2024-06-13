from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Configuración de la API de WhatsApp desde variables de entorno
whatsapp_token = os.getenv('WHATSAPP_TOKEN')
phone_id = os.getenv('PHONE_ID')
whatsapp_api_url = f'https://graph.facebook.com/v13.0/{phone_id}/messages'

# Configuración de la API de Best Sheets desde variables de entorno
best_sheets_url = os.getenv('BEST_SHEETS_URL')

def send_whatsapp_message(to, message):
    headers = {
        'Authorization': f'Bearer {whatsapp_token}',
        'Content-Type': 'application/json',
    }
    data = {
        'messaging_product': 'whatsapp',
        'to': to,
        'type': 'text',
        'text': {
            'body': message
        }
    }
    response = requests.post(whatsapp_api_url, headers=headers, json=data)
    return response.json()

def save_response_to_sheet(user, response):
    headers = {
        'Content-Type': 'application/json',
    }
    data = {
        'user': user,
        'response': response
    }
    response = requests.post(best_sheets_url, headers=headers, json=data)
    return response.json()

def handle_user_response(user, message):
    option = message.strip()
    
    if option == '1':
        response = 'Has seleccionado Carnes.'
    elif option == '2':
        response = 'Has seleccionado Granos.'
    elif option == '3':
        response = 'Has seleccionado Bebidas.'
    elif option == '4':
        response = 'Has seleccionado Quesos.'
    elif option == '5':
        response = 'Has seleccionado Embutidos.'
    elif option == '6':
        response = 'Has seleccionado Lácteos.'
    else:
        response = 'Opción no válida. Por favor, elige una opción del 1 al 6.'
    
    send_whatsapp_message(user, response)
    save_response_to_sheet(user, response)

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        verify_token = 'my_verification_token'  # El mismo que configuraste en Meta
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        if token == verify_token:
            return str(challenge)
        return 'Invalid verification token'
    
    if request.method == 'POST':
        data = request.json
        for entry in data['entry']:
            for change in entry['changes']:
                if change['field'] == 'messages':
                    message = change['value']['messages'][0]
                    user = message['from']
                    text = message['text']['body']
                    handle_user_response(user, text)
        return 'EVENT_RECEIVED', 200

if __name__ == '__main__':
    app.run(port=5000)
