from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Cargar las claves de la API de Wompi desde las variables de entorno
WOMPI_PUBLIC_KEY = os.getenv("WOMPI_PUBLIC_KEY", "pub_prod_gSUXEb0ZmMp5ukHW3jYFBgKVE3A3HdQu")
WOMPI_PRIVATE_KEY = os.getenv("WOMPI_PRIVATE_KEY", "prv_prod_iVpI45LnlEmfyy1bKaKxhyhGE0lXJE2W")
WOMPI_BASE_URL = "https://production.wompi.co/v1"

@app.route('/api/create_transaction', methods=['POST'])
def create_transaction():
    data = request.json
    if not data:
        return jsonify({"error": "Invalid request"}), 400

    # Validar que se haya recibido el token de pago
    if "payment_token" not in data or not data["payment_token"]:
        return jsonify({"error": "Invalid payment token"}), 400

    # Crear el payload para Wompi
    payload = {
        "acceptance_token": get_acceptance_token(),
        "amount_in_cents": data["amount"] * 100,  # Convertir a centavos
        "currency": "COP",
        "customer_email": data["email"],
        "payment_method": {
            "type": "CARD",
            "token": data["payment_token"],
            "installments": data.get("installments", 1)  # Por defecto, 1 cuota
        },
        "reference": data["reference"]
    }

    headers = {"Authorization": f"Bearer {WOMPI_PRIVATE_KEY}"}

    # Enviar la solicitud a Wompi
    try:
        response = requests.post(f"{WOMPI_BASE_URL}/transactions", json=payload, headers=headers)
        if response.status_code != 200:
            print("Error de Wompi:", response.json())  # Depuración
            return jsonify({
                "error": "Error processing transaction",
                "details": response.json()
            }), 400

        return jsonify(response.json())  # Responder con la respuesta de Wompi

    except Exception as e:
        print("Error enviando la solicitud a Wompi:", str(e))
        return jsonify({"error": "An internal error occurred"}), 500

def get_acceptance_token():
    """
    Obtener el acceptance token necesario para procesar pagos.
    """
    try:
        response = requests.get(f"{WOMPI_BASE_URL}/merchants/{WOMPI_PUBLIC_KEY}")
        data = response.json()
        return data["data"]["presigned_acceptance"]["acceptance_token"]
    except Exception as e:
        print("Error obteniendo el acceptance token:", str(e))
        raise Exception("Unable to fetch acceptance token")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

