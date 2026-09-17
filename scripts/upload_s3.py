"""Sobe os CSVs gerados localmente para o bucket S3, organizados por tipo (acoes/ e selic/)."""

import os
import sys

import boto3

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "..", "data")

PASTAS = {
    "acoes": os.path.join(DATA_DIR, "acoes"),
    "selic": os.path.join(DATA_DIR, "selic"),
}


def upload_csvs(bucket_name: str):
    s3 = boto3.client("s3")

    for prefixo, pasta_local in PASTAS.items():
        if not os.path.isdir(pasta_local):
            print(f"aviso: pasta {pasta_local} nao existe, pulando")
            continue

        for nome_arquivo in os.listdir(pasta_local):
            if not nome_arquivo.endswith(".csv"):
                continue

            caminho_local = os.path.join(pasta_local, nome_arquivo)
            chave_s3 = f"{prefixo}/{nome_arquivo}"

            print(f"Enviando {caminho_local} -> s3://{bucket_name}/{chave_s3}")
            s3.upload_file(caminho_local, bucket_name, chave_s3)

    print("Upload concluido.")


if __name__ == "__main__":
    bucket = os.environ.get("S3_BUCKET_NAME") or (sys.argv[1] if len(sys.argv) > 1 else None)
    if not bucket:
        print("Uso: python upload_s3.py <nome-do-bucket>")
        print("(ou defina a variavel de ambiente S3_BUCKET_NAME)")
        sys.exit(1)

    upload_csvs(bucket)
