import os
import boto3
import json
from datetime import datetime

TABLE_NAME = os.environ.get("TABLE_NAME")
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)
events = boto3.client("events")

def get_stock_from_nike(sku):
    # TODO V1: Implementar Playwright real
    # Por enquanto MOCK para testar fluxo E2E
    print(f"[MOCK] Checando estoque para {sku}")
    return {"stock": 3} # Simula que voltou

def lambda_handler(event, context):
    sku = "AJ1-HIGH-OG-TEST" 
    
    current = get_stock_from_nike(sku)
    current_stock = current["stock"]

    resp = table.get_item(Key={"sku": sku})
    previous_stock = resp.get("Item", {}).get("stock", 0)
    print(f"SKU {sku} | Anterior: {previous_stock} | Atual: {current_stock}")

    if previous_stock == 0 and current_stock > 0:
        print(f"🚨 RARO DETECTADO! {sku} voltou com {current_stock} un.")

        table.put_item(Item={
            "sku": sku,
            "stock": current_stock,
            "last_check": datetime.utcnow().isoformat(),
            "last_notified_stock": 0
        })
        events.put_events(Entries=[{
            "Source": "drop.hunter",
            "DetailType": "stock_returned",
            "Detail": json.dumps({
                "sku": sku,
                "stock": current_stock,
                "score": 9.0
            }),
            "EventBusName": "default"
        }])
    else:
        table.put_item(Item={
            "sku": sku,
            "stock": current_stock,
            "last_check": datetime.utcnow().isoformat()
        })
    
    return {"status": "ok", "sku": sku, "stock": current_stock}