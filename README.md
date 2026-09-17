# Pipeline de Dados Financeiros

Pipeline simples (MVP) que coleta dados financeiros publicos, salva localmente em
CSV e sobe para um bucket S3 provisionado via Terraform.

## O que o projeto faz

1. **Coleta de acoes** ([scripts/coleta_acoes.py](scripts/coleta_acoes.py)): baixa os
   precos historicos dos ultimos 30 dias de PETR4.SA, VALE3.SA e ITUB4.SA via
   [yfinance](https://pypi.org/project/yfinance/) e salva um CSV por ticker em
   `data/acoes/`.
2. **Coleta da Selic** ([scripts/coleta_selic.py](scripts/coleta_selic.py)): baixa a
   serie historica diaria da taxa Selic (serie SGS 11) na API do Banco Central e
   salva em `data/selic/`.
3. **Infraestrutura** ([terraform/](terraform/)): cria um bucket S3 com
   versionamento habilitado e bloqueio de acesso publico.
4. **Upload** ([scripts/upload_s3.py](scripts/upload_s3.py)): sobe os CSVs gerados
   localmente para o bucket, organizados em `acoes/` e `selic/`.

## Estrutura

```
projeto-financeiro/
├── terraform/
│   ├── main.tf          # bucket S3 + versionamento + bloqueio de acesso publico
│   ├── variables.tf
│   ├── outputs.tf
│   └── terraform.tfvars # nome do bucket (ajuste antes de aplicar)
├── scripts/
│   ├── coleta_acoes.py
│   ├── coleta_selic.py
│   ├── upload_s3.py
│   └── requirements.txt
├── data/                 # gerado localmente pelos scripts de coleta (nao versionado)
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

### 2. Provisionar a infraestrutura (Terraform)

```bash
cd terraform
terraform init
terraform apply
```

Edite `terraform.tfvars` antes de aplicar — `bucket_name` precisa ser
**globalmente unico** em toda a AWS.

### 3. Rodar a coleta de dados

```bash
cd scripts
python coleta_acoes.py
python coleta_selic.py
```

Isso gera os CSVs em `data/acoes/` e `data/selic/`.

### 4. Subir os dados para o S3

```bash
cd scripts
python upload_s3.py <nome-do-bucket>
# ou: export S3_BUCKET_NAME=<nome-do-bucket> && python upload_s3.py
```

Confirme com:

```bash
aws s3 ls s3://<nome-do-bucket>/acoes/
aws s3 ls s3://<nome-do-bucket>/selic/
```

## Proximos passos

- **Valuation DCF**: modulo de valuation por fluxo de caixa descontado a partir
  dos dados coletados.
- **Simulador de carteira**: simulacao de alocacao/retorno de carteira usando os
  precos historicos e a Selic como taxa livre de risco.
- Automacao (agendamento, orquestracao, IaC de pipeline completo) fica para uma
  proxima iteracao — este MVP roda tudo manualmente.
