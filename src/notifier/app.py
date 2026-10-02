import os, json, requests

def lambda_handler(event, context):
    token = os.environ['BOT_TOKEN']
    chat_id = os.environ['CHAT_ID']
    detail = event.get('detail', {})

    sku = detail.get('sku', 'PRODUTO DESCONHECIDO')
    stock = detail.get('stock', 0)
    url = detail.get('url', 'https://www.artwalk.com.br/tenis-nike-dunk-low-retro-masculino-dd139-1-100/p')
    sizes = detail.get('sizes', [])

    tam_str = "\n".join([f"• Tam {s}" for s in sizes]) if sizes else "• Conferir no site"

    msg = f"🚨 RARO DETECTADO!\n\n{sku}\nVoltou com {stock} unidades!\n\n📦 Disponíveis:\n{tam_str}\n\n🔗 Comprar: {url}\n\n"

    try:
        r = requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": msg}, timeout=10)
        print(f"Telegram: {r.text}")
        r.raise_for_status()
    except Exception as e:
        print(f"Erro telegram: {e}")

    return {"ok": True}