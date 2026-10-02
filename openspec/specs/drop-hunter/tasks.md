# DROP HUNTER - Tasks (V1.1 - 80/20)

## Objetivo V1: 1 SKU de Jordan monitorado, notificação em <10min

### Fase 1: Infra Base (sem código de negócio ainda)
- [ ] T1.1: Criar `template.yaml` SAM com 1 DynamoDB Table `drop-hunter-stock` (PK: sku, atributos: stock, last_check, last_notified_stock)
- [ ] T1.2: Definir 2 Lambdas vazios no template: `ScraperFunction` (Container) e `NotifierFunction` (Zip)
- [ ] T1.3: `sam build` local passar sem erro

### Fase 2: Scraper - O Coração (Regra 80/20: só AJ1)
- [ ] T2.1: Dockerfile para Scraper com Playwright + Chromium headless
- [ ] T2.2: Função `get_stock_from_nike(sku)` retornando {stock: int} - mock primeiro, depois real
- [ ] T2.3: Lógica de idempotência: Ler DynamoDB, comparar stock anterior = 0 e atual > 0
- [ ] T2.4: Se condição de RARO bater, salvar no DynamoDB com Conditional Write e publicar no EventBridge `stock_returned` {sku, stock, score: 9.0, timestamp}

### Fase 3: Notifier - Entrega de Valor
- [ ] T3.1: Lambda Notifier escutando EventBridge event `stock_returned`
- [ ] T3.2: Integrar WhatsApp (Twilio ou Evolution API) - Mensagem: "🚨 RARO: {sku} voltou com {stock} unidades"
- [ ] T3.3: Atualizar DynamoDB last_notified_stock para não re-notificar (anti-spam)

### Fase 4: Agendamento e Deploy
- [ ] T4.1: Criar EventBridge Scheduler rodando Scraper a cada 10min
- [ ] T4.2: `sam deploy --guided` primeira vez na AWS
- [ ] T4.3: Teste E2E: Zerar estoque no DynamoDB manual, rodar scraper, receber notificação

## Definição de Pronto (DoD) da V1
DADO que apaguei o item do DynamoDB
QUANDO o Scheduler rodar
ENTÃO recebo WhatsApp em <10min sem duplicar notificação