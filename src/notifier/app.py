import os
import json
import requests

def lambda_handler(event, context):
    token = os.environ['BOT_TOKEN']
    chat_id = os.environ['CHAT_ID']
    detail = event.get('detail', {})
    sku = detail.get('sku', 'PRODUTO DESCONHECIDO')
    stock = detail.get('stock', 0)
    msg = f"RARO DETECTADO!\n\n{sku}\nVoltou com {stock} unidades!\n\n@prints.raros"
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        r = requests.post(url, json={"chat_id": chat_id, "text": msg}, timeout=10)
        print(f"Telegram response: {r.text}")
    except Exception as e:
        print(f"Erro telegram: {e}")
    return {"ok": True, "sent": msg}
