"""Coleta a serie historica diaria da taxa Selic via API do Banco Central e salva em CSV local."""

import os
from datetime import datetime

import requests

# A API do BCB limita series diarias sem filtro de data e o endpoint "ultimos"
# a no maximo 20 valores por chamada; 20 dias uteis cobre aprox. os ultimos 30 dias corridos.
URL_SELIC = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados/ultimos/20?formato=json"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "..", "data", "selic")


def coletar_selic():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Baixando serie historica da Selic (BCB SGS 11)...")
    resposta = requests.get(URL_SELIC, timeout=30)
    resposta.raise_for_status()
    dados = resposta.json()

    if not dados:
        print("  aviso: nenhum dado retornado pela API do BCB")
        return

    data_execucao = datetime.now().strftime("%Y%m%d")
    nome_arquivo = f"selic_{data_execucao}.csv"
    caminho = os.path.join(OUTPUT_DIR, nome_arquivo)

    with open(caminho, "w", encoding="utf-8") as f:
        f.write("data,valor\n")
        for registro in dados:
            f.write(f"{registro['data']},{registro['valor']}\n")

    print(f"  salvo em {caminho} ({len(dados)} linhas)")


if __name__ == "__main__":
    coletar_selic()
