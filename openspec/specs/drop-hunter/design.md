# DROP HUNTER - Design Decisions

## ADR-001: Por que EventBridge Scheduler + Lambda Container e não Cron no meu PC?

Decisão: EventBridge rodando a cada 10 minutos com Lambda e Playwright (container).

Motivo: Lambda não para de funcionar mesmo com o PC desligado. E, o Playwright precisa do navegador, que não performa com o Lambda zip - apenas container.

Alternativa descartada: Script no PC com o agendador do Windows.

## ADR-002: Por que DynamoDB e não Excel/Sheets para guardar estoque?

Decisão: DynamoDB com Chave SKU de chave primária (PK).

Motivo: Preciso de leitura/escrita atômica para melhor idempotência (evitar notificar 2x). Sheets não garante corrida segura.

Custo: PPR (Pay-per-request), quase grátis para v1

## ADR-003: Por que Eventos `stock_returned` e não chamar WhatsApp direto no scraper?

Decisão: Scraper só expõe evento. Outro Lambda escuta e notifica.

Motivo: Diluir as responsabilidades. Amanhã se quiser notificar no Telegram, Instagram DM ou e-mail, não mexe no scraper.