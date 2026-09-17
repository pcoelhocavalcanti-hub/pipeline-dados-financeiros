"""Coleta precos historicos de acoes via yfinance e salva em CSV local."""

import os
from datetime import datetime

import yfinance as yf

TICKERS = ["PETR4.SA", "VALE3.SA", "ITUB4.SA"]
PERIODO = "30d"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "..", "data", "acoes")


def coletar_acoes():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    data_execucao = datetime.now().strftime("%Y%m%d")

    for ticker in TICKERS:
        print(f"Baixando {ticker}...")
        df = yf.Ticker(ticker).history(period=PERIODO)

        if df.empty:
            print(f"  aviso: nenhum dado retornado para {ticker}")
            continue

        df.reset_index(inplace=True)
        nome_arquivo = f"{ticker.replace('.SA', '')}_{data_execucao}.csv"
        caminho = os.path.join(OUTPUT_DIR, nome_arquivo)
        df.to_csv(caminho, index=False)
        print(f"  salvo em {caminho} ({len(df)} linhas)")


if __name__ == "__main__":
    coletar_acoes()
