from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Load Wompi API keys from environment variables
WOMPI_PUBLIC_KEY = os.getenv("WOMPI_PUBLIC_KEY", "pub_prod_gSUXEb0ZmMp5ukHW3jYFBgKVE3A3HdQu")
WOMPI_PRIVATE_KEY = os.getenv("WOMPI_PRIVATE_KEY", "prv_prod_iVpI45LnlEmfyy1bKaKxhyhGE0lXJE2W")
WOMPI_BASE_URL = "https://production.wompi.co/v1"

@app.route('/api/create_transaction', methods=['POST'])
def create_transaction():
    data = request.json
    if not data:
        return jsonify({"error": "Invalid request"}), 400
    
    # Create payment payload
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
response = requests.post(f"{WOMPI_BASE_URL}/transactions", json=payload, headers=headers)

return jsonify(response.json())

def get_acceptance_token():
    response = requests.get(f"{WOMPI_BASE_URL}/merchants/{WOMPI_PUBLIC_KEY}")
    data = response.json()
    return data["data"]["presigned_acceptance"]["acceptance_token"]

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
