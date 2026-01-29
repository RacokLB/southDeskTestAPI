import requests
import json

# Prueba primero localmente para asegurar que el código funciona
url = "http://127.0.0.1:8000/enrich"

payload = {
    "company_name": "Tesla",
    "website": "https://tesla.com"
}

headers = {
    "Content-Type": "application/json"
}

try:
    print(f"Enviando petición a {url}...")
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    
    print(f"Estado: {response.status_code}")
    if response.status_code == 200:
        print("Respuesta Exitosa de la IA:")
        print(json.dumps(response.json(), indent=2))
    else:
        print("Error del Servidor:")
        print(response.text)
        
except Exception as e:
    print(f"Error de conexión: {e}")