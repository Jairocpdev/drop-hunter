import os
import json
import requests
from urllib.parse import quote

def lambda_handler(event, context):
    token = os.environ['BOT_TOKEN']
    chat_id = os.environ['CHAT_ID']
    detail = event.get('detail', {})
    
    sku = detail.get('sku', 'PRODUTO DESCONHECIDO')
    stock = detail.get('stock', 0)
    url = detail.get('url', 'https://www.artwalk.com.br/tenis-nike-dunk-low-retro-masculino-dd139-1-100/p')
    sizes = detail.get('sizes', [])
    
    # Filtra só tamanhos com estoque > 0 e limpa o TÃªnis bugado
    disponiveis = []
    for s in sizes:
        try:
            # Corrige encoding VTEX: TÃªnis -> Tênis
            s_fixed = s.encode('latin1').decode('utf-8')
        except:
            s_fixed = s.replace('TÃªnis', 'Tênis')
        
        if ': 0' not in s and ':0' not in s:
            disponiveis.append(s_fixed)

    tam_str = "\n".join(disponiveis) if disponiveis else "Ver no site (API retornou geral)"
    
    msg = (
        f"🚨 RARO DETECTADO!\n\n"
        f"{sku}\n"
        f"Voltou com {stock} unidades!\n\n"
        f"📦 Disponíveis:\n{tam_str}\n\n"
        f"🔗 Comprar: {url}\n\n"
        f"@prints.raros"
    )

    try:
        api_url = f"https://api.telegram.org/bot{token}/sendMessage"
        r = requests.post(api_url, json={
            "chat_id": chat_id, 
            "text": msg,
            "disable_web_page_preview": False
        }, timeout=10)
        print(f"Telegram response: {r.status_code} {r.text}")
        r.raise_for_status()
    except Exception as e:
        print(f"Erro telegram: {e}")
        # não falha a lambda, só loga
    
    return {"ok": True, "sent": msg}