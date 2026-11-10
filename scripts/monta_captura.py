"""Monta a captura do rascunho a partir dos pedaços trazidos da página e confere os hashes.

Uso: python monta_captura.py <pedacos.txt> <saida.json> <hash1> <hash2> ... [--envios envios.json]

<pedacos.txt>: os textos de pedacoCaptura(0..n-1) colados em sequência (com ou sem << >>).
Atenção: ao gravar com a ferramenta Write, as sequências \\uXXXX viram o caractere original;
as duas formas são aceitas. Os hashes vêm de guardaCaptura() na página (4 bytes, "1a-ee-ca-0a").
Se algum pedaço divergir, o script para e diz qual: traga esse pedaço de novo.
"""
import hashlib
import json
import re
import sys


def main(a):
    envios = None
    if "--envios" in a:
        k = a.index("--envios"); envios = json.load(open(a[k + 1], encoding="utf-8")); a = a[:k] + a[k + 2:]
    origem, saida, hashes = a[0], a[1], a[2:]
    texto = open(origem, encoding="utf-8").read()
    texto = re.sub(r"<<|>>|\n", "", texto)
    texto = re.sub(r"\\u00(3d|26|3f|3b|25)", lambda m: chr(int(m.group(1), 16)), texto)
    pedacos = [texto[i:i + 900] for i in range(0, len(texto), 900)]
    obtidos = ["-".join(hashlib.sha256(p.encode()).hexdigest()[j:j + 2] for j in range(0, 8, 2)) for p in pedacos]
    if obtidos != hashes:
        ruins = [i for i, (x, y) in enumerate(zip(obtidos, hashes + [""] * len(obtidos))) if x != y]
        sys.exit(f"Pedaços divergentes: {ruins or 'quantidade'} (obtidos {len(obtidos)}, esperados {len(hashes)})")
    captura = json.loads(texto)
    if envios:
        captura["envios"] = envios
    json.dump(captura, open(saida, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{saida}: {len(pedacos)} pedaços conferidos, {len(texto)} caracteres")


if __name__ == "__main__":
    main(sys.argv[1:])
