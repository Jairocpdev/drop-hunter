# DROP HUNTER V1.0 - Spec

## Objetivo
Detectar retorno de estoque de itens raros e notificar em até 10 minutos.

## O que é RARO na v1 (Regra 80/20 Pareto)
Foco v1: Apenas 【entity-Nike¦canonical_name=Nike】 Air Jordan (20% das marcas que geram 80% do valor para @prints.raros)
Regra de negócio: Item é raro SE estoque anterior = 0 E estoque atual > 0

## Cenários de Sucesso
DADO que SKU AJ1-High-001 estava com estoque 0 no DynamoDB
QUANDO scraper encontrar estoque 5 no site oficial da entity-Nike canonical_name=Nike
ENTÃO publicar evento `stock_returned` com {sku, stock: 5, score: 9.0, timestamp}

## Cenário de Idempotência (Anti-spam)
DADO que SKU AJ1-High-001 já foi notificado com estoque 5
QUANDO scraper encontrar novamente estoque 5
ENTÃO NÃO notificar novamente

## Cenário de Falha
DADO que o site da entity-Nike canonical_name=Nike está fora do ar
QUANDO scraper falhar 3 vezes seguidas
ENTÃO NÃO publicar evento, registrar métrica ScrapeFailure e manter último estado

## Fora de Escopo v1
- Comparação de preço
- Outras marcas além de Air Jordan
- Scoring dinâmico (score fixo 9.0 na v1)