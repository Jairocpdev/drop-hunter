import requests, json, os, boto3, re
from datetime import datetime

TABLE = os.environ.get('TABLE_NAME', 'drop-hunter-stock')
EVENT_BUS = os.environ.get('EVENT_BUS_NAME', 'drop-hunter-events')
SKU = "ARTWALK DUNK LOW PANDA - DD1391-100"
PRODUCT_URL = "https://www.artwalk.com.br/tenis-nike-dunk-low-retro-masculino-dd139-1-100/p"

dynamodb = boto3.resource('dynamodb')
events = boto3.client('events')

def get_product_id():
    # Pega HTML da página do produto
    r = requests.get(PRODUCT_URL, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
    html = r.text
    # Tenta achar productId no JSON da VTEX que fica no HTML
    m = re.search(r'"productId"\s*:\s*"(\d+)"', html)
    if m:
        return m.group(1)
    m = re.search(r'productId\s*=\s*(\d+)', html)
    if m:
        return m.group(1)
    # fallback: procura no skuJson
    m = re.search(r'"productId":(\d+)', html)
    if m:
        return m.group(1)
    return None

def lambda_handler(event, context):
    try:
        product_id = get_product_id()
        print(f"ProductId encontrado: {product_id}")
        if not product_id:
            return {"status": "productId_not_found"}

        API_URL = f"https://www.artwalk.com.br/api/catalog_system/pub/products/search?fq=productId:{product_id}"
        r = requests.get(API_URL, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        data = r.json()
        if not data:
            return {"status": "not_found", "productId": product_id}

        stock_total = 0
        sizes = []
        for item in data[0].get('items', []):
            name = item.get('name', '')
            sellers = item.get('sellers', [])
            qty = 0
            if sellers:
                qty = sellers[0].get('commertialOffer', {}).get('AvailableQuantity', 0)
                stock_total += qty

        try:
            name_fixed = name.encode('latin1').decode('utf-8')
        except:
            name_fixed = name
        sizes.append(f"{name_fixed}: {qty}")

        print(f"[{SKU}] Estoque atual: {stock_total} - {sizes}")

        table = dynamodb.Table(TABLE)
        resp = table.get_item(Key={'sku': SKU})
        old_stock = int(resp.get('Item', {}).get('stock', 0))

        table.put_item(Item={'sku': SKU, 'stock': stock_total, 'last_check': datetime.now().isoformat(), 'sizes': sizes, 'productId': product_id})

        if old_stock == 0 and stock_total > 0:
            print(f"RARE DROP: {old_stock} -> {stock_total}")
            events.put_events(
                Entries=[{
                    'Source': 'drop-hunter.scraper',
                    'DetailType': 'stock_return',
                    'Detail': json.dumps({"sku": SKU, "stock": stock_total, "url": PRODUCT_URL, "sizes": sizes}),
                    'EventBusName': EVENT_BUS
                }]
            )
            return {"status": "notified", "old": old_stock, "new": stock_total, "sizes": sizes}

        return {"status": "checked", "old": old_stock, "new": stock_total, "sizes": sizes, "productId": product_id}

    except Exception as e:
        print(f"ERRO SCRAPER: {e}")
        raise