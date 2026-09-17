"""Handler da Lambda: coleta acoes (yfinance) e Selic (BCB) e sobe os CSVs
direto para o S3, sem passar por disco local. Reune a logica que localmente
fica separada em coleta_acoes.py, coleta_selic.py e upload_s3.py."""

import os
from datetime import datetime

import boto3
import requests
import yfinance as yf

TICKERS = ["PETR4.SA", "VALE3.SA", "ITUB4.SA"]
PERIODO = "30d"

# Mesma limitacao da API do BCB documentada em coleta_selic.py: o endpoint
# "ultimos" aceita no maximo 20 valores por chamada.
URL_SELIC = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados/ultimos/20?formato=json"

BUCKET_NAME = os.environ["BUCKET_NAME"]

s3 = boto3.client("s3")


def coletar_acoes(data_execucao):
    arquivos = []
    for ticker in TICKERS:
        df = yf.Ticker(ticker).history(period=PERIODO)
        if df.empty:
            print(f"aviso: nenhum dado retornado para {ticker}")
            continue

        df.reset_index(inplace=True)
        nome_arquivo = f"{ticker.replace('.SA', '')}_{data_execucao}.csv"
        arquivos.append((f"acoes/{nome_arquivo}", df.to_csv(index=False)))

    return arquivos


def coletar_selic(data_execucao):
    resposta = requests.get(URL_SELIC, timeout=30)
    resposta.raise_for_status()
    dados = resposta.json()

    if not dados:
        print("aviso: nenhum dado retornado pela API do BCB")
        return []

    linhas = ["data,valor"] + [f"{d['data']},{d['valor']}" for d in dados]
    conteudo = "\n".join(linhas)
    return [(f"selic/selic_{data_execucao}.csv", conteudo)]


def handler(event, context):
    data_execucao = datetime.now().strftime("%Y%m%d")
    arquivos = coletar_acoes(data_execucao) + coletar_selic(data_execucao)

    for chave, conteudo in arquivos:
        s3.put_object(Bucket=BUCKET_NAME, Key=chave, Body=conteudo.encode("utf-8"))
        print(f"enviado s3://{BUCKET_NAME}/{chave}")

    return {"arquivos_enviados": [chave for chave, _ in arquivos]}
