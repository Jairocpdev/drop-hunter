import requests, json, os, boto3, re
from datetime import datetime

TABLE = os.environ.get('TABLE_NAME', 'drop-hunter-stock')
EVENT_BUS = os.environ.get('EVENT_BUS_NAME', 'drop-hunter-events')
SKU = "ARTWALK DUNK LOW PANDA - DD1391-100"
PRODUCT_URL = "https://www.artwalk.com.br/tenis-nike-dunk-low-retro-masculino-dd139-1-100/p"

dynamodb = boto3.resource('dynamodb')
events = boto3.client('events')

def get_product_id():
    r = requests.get(PRODUCT_URL, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
    html = r.text
    for pattern in [r'"productId"\s*:\s*"(\d+)"', r'"productId":(\d+)', r'productId\s*=\s*(\d+)']:
        m = re.search(pattern, html)
        if m:
            return m.group(1)
    return None

def lambda_handler(event, context):
    try:
        product_id = get_product_id()
        print(f"ProductId: {product_id}")
        if not product_id:
            return {"status": "productId_not_found"}

        API_URL = f"https://www.artwalk.com.br/api/catalog_system/pub/products/search?fq=productId:{product_id}"
        r = requests.get(API_URL, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        data = r.json()
        if not data:
            return {"status": "not_found"}

        stock_total = 0
        sizes = []
        sizes_simple = []

        for item in data[0].get('items', []):
            raw_name = item.get('nameComplement', '') or item.get('name', '')
            size_match = re.search(r'(\d+[\.,]?\d*)', raw_name)
            size_label = size_match.group(1) if size_match else raw_name

            sellers = item.get('sellers', [])
            qty = 0
            if sellers:
                qty = sellers[0].get('commertialOffer', {}).get('AvailableQuantity', 0)
                stock_total += qty

            try:
                name_fixed = raw_name.encode('latin1').decode('utf-8')
            except:
                name_fixed = raw_name.replace('TÃªnis','Tênis')

            sizes.append(f"{name_fixed}: {qty}")
            if qty > 0:
                sizes_simple.append(f"{size_label}: {qty}")

        print(f"[{SKU}] Estoque: {stock_total} - {sizes_simple}")

        table = dynamodb.Table(TABLE)
        resp = table.get_item(Key={'sku': SKU})
        old_stock = int(resp.get('Item', {}).get('stock', 0))
        table.put_item(Item={'sku': SKU, 'stock': stock_total, 'last_check': datetime.now().isoformat(), 'sizes': sizes, 'productId': product_id})

        if old_stock == 0 and stock_total > 0:
            print(f"RARE DROP: {old_stock} -> {stock_total}")
            # CORRIGIDO: Source, DetailType e EventBusName obrigatórios
            events.put_events(
                Entries=[{
                    'Source': 'drop-hunter.scraper',
                    'DetailType': 'stock_return',
                    'EventBusName': EVENT_BUS,
                    'Detail': json.dumps({
                        "sku": SKU,
                        "stock": stock_total,
                        "url": PRODUCT_URL,
                        "sizes": sizes_simple
                    })
                }]
            )
            return {"status": "notified", "old": old_stock, "new": stock_total, "sizes": sizes_simple}

        return {"status": "checked", "old": old_stock, "new": stock_total, "sizes": sizes_simple}

    except Exception as e:
        print(f"ERRO SCRAPER: {e}")
        raise