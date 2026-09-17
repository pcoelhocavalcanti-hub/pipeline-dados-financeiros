"""Calcula retorno acumulado e volatilidade anualizada por acao a partir dos CSVs
gerados por coleta_acoes.py em data/acoes/."""

import glob
import os

import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ACOES_DIR = os.path.join(SCRIPT_DIR, "..", "data", "acoes")

DIAS_UTEIS_ANO = 252


def arquivo_mais_recente_por_ticker():
    """Mapeia cada ticker (ex. PETR4) para o CSV mais recente encontrado."""
    arquivos = glob.glob(os.path.join(ACOES_DIR, "*.csv"))
    mais_recente = {}
    for caminho in arquivos:
        ticker = os.path.basename(caminho).split("_")[0]
        if ticker not in mais_recente or os.path.getmtime(caminho) > os.path.getmtime(mais_recente[ticker]):
            mais_recente[ticker] = caminho
    return mais_recente


def analisar(caminho_csv):
    df = pd.read_csv(caminho_csv, parse_dates=["Date"])
    df = df.sort_values("Date")

    retornos_diarios = df["Close"].pct_change().dropna()

    retorno_acumulado = (df["Close"].iloc[-1] / df["Close"].iloc[0] - 1) * 100
    volatilidade_diaria = retornos_diarios.std()
    volatilidade_anualizada = volatilidade_diaria * (DIAS_UTEIS_ANO ** 0.5) * 100

    return {
        "periodo_inicio": df["Date"].iloc[0].date(),
        "periodo_fim": df["Date"].iloc[-1].date(),
        "preco_inicial": df["Close"].iloc[0],
        "preco_final": df["Close"].iloc[-1],
        "retorno_acumulado_pct": retorno_acumulado,
        "volatilidade_anualizada_pct": volatilidade_anualizada,
    }


def main():
    arquivos_por_ticker = arquivo_mais_recente_por_ticker()

    if not arquivos_por_ticker:
        print(f"Nenhum CSV encontrado em {ACOES_DIR}. Rode coleta_acoes.py primeiro.")
        return

    resultados = []
    for ticker, caminho in sorted(arquivos_por_ticker.items()):
        resultados.append({"ticker": ticker, **analisar(caminho)})

    print(f"{'Ticker':<8}{'Periodo':<25}{'Retorno acum.':>15}{'Volatilidade a.a.':>20}")
    print("-" * 68)
    for r in resultados:
        periodo = f"{r['periodo_inicio']} a {r['periodo_fim']}"
        print(
            f"{r['ticker']:<8}{periodo:<25}"
            f"{r['retorno_acumulado_pct']:>14.2f}%"
            f"{r['volatilidade_anualizada_pct']:>19.2f}%"
        )


if __name__ == "__main__":
    main()
