"""Gera cópias leves das fotos reais para o envio (a extensão do Chrome manda no máximo 10 MB por chamada).

Uso: python fotos_leves.py <saida> <foto1.jpg> [foto2.jpg ...] [--lado 2000] [--qualidade 88]

- Gira conforme o EXIF do celular e grava SEM metadados (sai junto a localização GPS da foto).
- Maior lado = --lado (padrão 2000 px, acima dos 1600 px da galeria); JPEG qualidade 88.
- Não retoca a peça: só reamostra. Mantém o nome do arquivo (o site mostra o nome no rascunho).
"""
import sys
from pathlib import Path

from PIL import Image, ImageOps


def main(a):
    lado = int(a[a.index("--lado") + 1]) if "--lado" in a else 2000
    q = int(a[a.index("--qualidade") + 1]) if "--qualidade" in a else 88
    a = [x for i, x in enumerate(a) if x not in ("--lado", "--qualidade") and (i == 0 or a[i - 1] not in ("--lado", "--qualidade"))]
    saida = Path(a[0]); saida.mkdir(parents=True, exist_ok=True)
    for f in map(Path, a[1:]):
        im = ImageOps.exif_transpose(Image.open(f)).convert("RGB")
        im.thumbnail((lado, lado), Image.LANCZOS)
        destino = saida / (f.stem + ".jpg")
        im.save(destino, "JPEG", quality=q, optimize=True)          # sem exif=: metadados ficam de fora
        print(f"{f.name}: {f.stat().st_size / 1e6:.1f} MB -> {destino.stat().st_size / 1e6:.1f} MB, {im.size[0]}x{im.size[1]}")


if __name__ == "__main__":
    main(sys.argv[1:])
