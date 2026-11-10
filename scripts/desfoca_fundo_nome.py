"""Tratamento local por máscaras de polígonos. Uso: python desfoca_fundo_nome.py foto.json"""

import json
import sys
from pathlib import Path

import cv2
import numpy as np


def tratar(config_path):
    config_path = Path(config_path).resolve()
    cfg = json.loads(config_path.read_text(encoding="utf-8-sig"))
    origem = (config_path.parent / cfg["origem"]).resolve()
    saida = (config_path.parent / cfg["saida"]).resolve()
    if origem == saida:
        raise ValueError("A saída deve ser uma cópia; preserve o original.")
    im = cv2.imdecode(np.fromfile(origem, dtype=np.uint8), cv2.IMREAD_COLOR)
    if im is None:
        raise ValueError(f"Não foi possível abrir: {origem}")
    h, w = im.shape[:2]
    if cfg["tamanho"] != [w, h]:
        raise ValueError(f"Máscara para {cfg['tamanho']}; foto atual: {[w, h]}.")

    def mascara(poligonos):
        m = np.zeros((h, w), np.uint8)
        for p in poligonos:
            pontos = np.asarray(p, dtype=np.int32)
            if pontos.ndim != 2 or pontos.shape[1] != 2 or len(pontos) < 3:
                raise ValueError("Cada polígono precisa de pelo menos três pares [x, y].")
            if (pontos < 0).any() or (pontos[:, 0] >= w).any() or (pontos[:, 1] >= h).any():
                raise ValueError("Polígono fora da foto.")
            cv2.fillPoly(m, [pontos], 255)
        return m

    if not cfg["preservar"]:
        raise ValueError("Defina os contornos do produto e dos acessórios a preservar.")
    fg = mascara(cfg["preservar"])
    fundo = cv2.GaussianBlur(im, (0, 0), cfg.get("sigma_fundo", 18))
    alpha = cv2.GaussianBlur(fg.astype(np.float32) / 255, (0, 0),
                             cfg.get("sigma_borda", 4))[..., None]
    res = (im.astype(np.float32) * alpha + fundo.astype(np.float32) * (1 - alpha)).astype(np.uint8)

    nomes = cfg.get("ocultar_nome", [])
    if nomes:
        nm = mascara(nomes)
        # Reconstrução local da textura: apenas na identificação autorizada.
        clean = cv2.inpaint(res, nm, cfg.get("raio_nome", 2), cv2.INPAINT_TELEA)
        edge = cv2.GaussianBlur(nm.astype(np.float32) / 255, (0, 0),
                               cfg.get("sigma_nome", 2))[..., None]
        res = (res.astype(np.float32) * (1 - edge) + clean.astype(np.float32) * edge).astype(np.uint8)

    if saida.suffix.lower() not in (".jpg", ".jpeg"):
        raise ValueError("Use saída JPEG (.jpg ou .jpeg).")
    saida.parent.mkdir(parents=True, exist_ok=True)
    ok, encoded = cv2.imencode(".jpg", res, [cv2.IMWRITE_JPEG_QUALITY, 95])
    if not ok:
        raise RuntimeError("Falha ao codificar a foto.")
    encoded.tofile(saida)  # Nova imagem sem EXIF/GPS; suporta caminhos com acentos.
    print(saida)


if __name__ == "__main__":
    tratar(sys.argv[1])
