import os
import json

def lambda_handler(event, context):
    print("Evento recebido:", json.dumps(event))
    detail = event.get("detail", {})
    sku = detail.get("sku")
    stock = detail.get("stock")
    
    print(f"📲 ENVIAR WHATSAPP: 🚨 RARO {sku} voltou com {stock} unidades! - @prints.raros")
    
    return {"sent": True}