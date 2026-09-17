# Pipeline de Dados Financeiros

Pipeline (MVP) que coleta dados financeiros publicos, sobe para um bucket S3
provisionado via Terraform, roda automaticamente todo dia util via Lambda +
EventBridge, e expoe um dashboard publico com os dados coletados.

## O que o projeto faz

1. **Coleta de acoes** ([scripts/coleta_acoes.py](scripts/coleta_acoes.py)): baixa os
   precos historicos dos ultimos 30 dias de PETR4.SA, VALE3.SA e ITUB4.SA via
   [yfinance](https://pypi.org/project/yfinance/) e salva um CSV por ticker em
   `data/acoes/`.
2. **Coleta da Selic** ([scripts/coleta_selic.py](scripts/coleta_selic.py)): baixa a
   serie historica diaria da taxa Selic (serie SGS 11) na API do Banco Central e
   salva em `data/selic/`.
3. **Infraestrutura** ([terraform/](terraform/)): cria o bucket S3 de dados
   (privado, versionamento habilitado) e o bucket do dashboard (publico, site
   estatico).
4. **Upload** ([scripts/upload_s3.py](scripts/upload_s3.py)): sobe os CSVs gerados
   localmente para o bucket, organizados em `acoes/` e `selic/`. Uso manual/pontual
   — a coleta automatizada (item 6) nao depende deste script.
5. **Analise** ([scripts/analise_retorno_volatilidade.py](scripts/analise_retorno_volatilidade.py)):
   calcula retorno acumulado e volatilidade anualizada por acao a partir dos CSVs
   locais — preview do simulador de carteira.
6. **Coleta automatizada** ([lambda/handler.py](lambda/handler.py)): mesma logica
   das coletas de acoes e Selic, rodando como Lambda, disparada pelo EventBridge
   todo dia util as 18h (horario de Brasilia), escrevendo direto no S3 sem
   depender de execucao manual.
7. **Dashboard** ([dashboard/index.html](dashboard/index.html)): pagina estatica
   com o desempenho indexado das acoes, Selic e retorno/volatilidade, publicada
   no bucket de site estatico (ver `dashboard_url` nos outputs do Terraform). E
   um instantaneo gerado a partir dos dados coletados — nao le o S3 ao vivo.

## Estrutura

```
projeto-financeiro/
├── terraform/
│   ├── main.tf          # bucket S3 de dados: versionamento + bloqueio de acesso publico
│   ├── lambda.tf         # Lambda de coleta diaria + IAM + regra do EventBridge
│   ├── dashboard.tf       # bucket S3 do dashboard (site estatico publico)
│   ├── variables.tf
│   ├── outputs.tf
│   └── terraform.tfvars  # nomes dos buckets (ajuste antes de aplicar)
├── scripts/
│   ├── coleta_acoes.py
│   ├── coleta_selic.py
│   ├── upload_s3.py
│   ├── analise_retorno_volatilidade.py
│   └── requirements.txt
├── lambda/
│   ├── handler.py               # logica de coleta + upload, roda na Lambda
│   ├── requirements.txt
│   └── build_lambda_package.ps1  # empacota handler + deps (Linux/manylinux) em build.zip
├── dashboard/
│   └── index.html         # dashboard estatico publicado no bucket do site
├── data/                   # gerado localmente pelos scripts de coleta (nao versionado)
└── README.md
```

## Como rodar

### 1. Setup do ambiente Python

```bash
cd scripts
python -m pip install -r requirements.txt
```

Credenciais AWS precisam estar configuradas (`aws configure` ou variaveis de
ambiente `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`) para o Terraform e para o
`upload_s3.py`.

> **Nota (Windows + antivirus com inspecao SSL):** se o `aws cli`, `boto3`,
> `terraform` ou o `yfinance` falharem com erros do tipo `CERTIFICATE_VERIFY_FAILED`
> / `unable to get local issuer certificate`, o motivo mais provavel e um
> antivirus (ex.: Norton) fazendo inspecao de trafego HTTPS com um certificado
> raiz proprio que nao esta no bundle de CAs publico usado pelo Python. Duas
> saidas: (a) exportar o certificado raiz do antivirus do Windows e apontar
> `SSL_CERT_FILE` / `REQUESTS_CA_BUNDLE` / `AWS_CA_BUNDLE` para um bundle
> combinado (certifi + esse certificado), ou (b) desabilitar temporariamente a
> inspecao SSL/TLS do antivirus (feature costuma se chamar "Intrusion
> Prevention" / "Encrypted traffic scanning" / "SSL scanning") ou adicionar uma
> excecao para `terraform.exe` e os plugins de provider — essa mudanca de
> configuracao do antivirus precisa ser feita por voce, manualmente.

### 2. Empacotar a Lambda (antes do terraform apply)

```powershell
cd lambda
.\build_lambda_package.ps1
```

Gera `lambda/build.zip` (nao versionado) com `handler.py` + dependencias
compiladas para Linux x86_64 (baixadas via `pip --platform manylinux2014_x86_64`,
sem precisar de Docker). O `terraform apply` do proximo passo depende desse zip
existir.

### 3. Provisionar a infraestrutura (Terraform)

```bash
cd terraform
terraform init
terraform apply
```

Edite `terraform.tfvars` antes de aplicar — `bucket_name` e
`dashboard_bucket_name` precisam ser **globalmente unicos** em toda a AWS. Isso
cria: bucket de dados (privado), Lambda + EventBridge (coleta automatizada
diaria) e bucket do dashboard (publico). O output `dashboard_url` traz o link
do dashboard.

### 4. Rodar a coleta manualmente (opcional)

A coleta ja roda sozinha via Lambda, mas para rodar na sua maquina (ex.: gerar
dados mais recentes para o dashboard sem esperar o horario agendado):

```bash
cd scripts
python coleta_acoes.py
python coleta_selic.py
python upload_s3.py <nome-do-bucket-de-dados>
```

Confirme com:

```bash
aws s3 ls s3://<nome-do-bucket-de-dados>/acoes/
aws s3 ls s3://<nome-do-bucket-de-dados>/selic/
```

### 5. Analise rapida (retorno e volatilidade)

```bash
cd scripts
python analise_retorno_volatilidade.py
```

Le os CSVs locais em `data/acoes/` e imprime retorno acumulado e volatilidade
anualizada por ticker.

## Proximos passos

- **Valuation DCF**: modulo de valuation por fluxo de caixa descontado a partir
  dos dados coletados.
- **Simulador de carteira**: simulacao de alocacao/retorno de carteira usando os
  precos historicos e a Selic como taxa livre de risco (a analise de
  retorno/volatilidade ja e um primeiro passo nessa direcao).
- **Enxugar o pacote da Lambda**: `lambda/requirements.txt` puxa dependencias do
  `yfinance` que nao usamos (`beautifulsoup4`, `lxml`, `protobuf`, `peewee`,
  `websockets`), inflando o zip para ~48MB e deixando o upload lento. Vale
  vendorizar so o necessario.
- **Dominio proprio para o dashboard**: hoje ele fica no endpoint padrao do S3
  (`http://<bucket>.s3-website-<regiao>.amazonaws.com`, sem HTTPS). Um dominio
  proprio exigiria CloudFront + ACM (certificado HTTPS) + Route53 na frente do
  bucket.
