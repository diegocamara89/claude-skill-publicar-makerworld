"""Trata as fotos reais para o MakerWorld: corte 4:3 na peça, poeira fora da peça,
luz/contraste, vinheta suave e nitidez. A peça em si não é retocada (tem de ser a foto real)."""
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).parent
ENTRADA, SAIDA = AQUI / "Fotos reais", AQUI / "final" / "fotos"

# por foto: centro e raio da peça (px da original) e caixa de corte 4:3 (x0, y0, largura)
FOTOS = {
    "WhatsApp Image 2026-09-27 at 08.45.13(1).jpeg": dict(pecas=[(493, 448, 165), (800, 547, 130)], corte=(195, 130, 900)),
    "WhatsApp Image 2026-09-27 at 08.45.13(2).jpeg": dict(pecas=[(635, 493, 215)], corte=(195, 140, 880)),
    "WhatsApp Image 2026-09-27 at 08.45.13(3).jpeg": dict(pecas=[(587, 360, 270)], corte=(107, 20, 960)),
    "WhatsApp Image 2026-09-27 at 08.45.13.jpeg": dict(pecas=[(456, 636, 240)], corte=(0, 280, 960)),
}


def tira_poeira(im, pecas):
    g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    topo = cv2.morphologyEx(g, cv2.MORPH_TOPHAT, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
    fundo_escuro = cv2.blur(g, (41, 41)) < 95
    cand = ((topo > 38) & fundo_escuro).astype(np.uint8)
    for (x, y, r) in pecas:                              # nunca mexe na peça
        cv2.circle(cand, (x, y), int(r * 1.12), 0, -1)
    n, rot, st, _ = cv2.connectedComponentsWithStats(cand, 8)
    mask = np.zeros_like(cand)
    for i in range(1, n):
        a, w, h = st[i, cv2.CC_STAT_AREA], st[i, cv2.CC_STAT_WIDTH], st[i, cv2.CC_STAT_HEIGHT]
        if 2 <= a <= 160 and max(w, h) <= 22:            # pontinho, não reflexo comprido
            mask[rot == i] = 255
    mask = cv2.dilate(mask, np.ones((5, 5), np.uint8))
    return cv2.inpaint(im, mask, 4, cv2.INPAINT_TELEA), int(mask.astype(bool).sum())


def tom(im):
    lab = cv2.cvtColor(im, cv2.COLOR_BGR2LAB)
    L, a, b = cv2.split(lab)
    L = cv2.createCLAHE(clipLimit=1.3, tileGridSize=(8, 8)).apply(L)
    lut = np.clip(((np.arange(256) / 255.0) ** 0.88) * 255 * 1.04, 0, 255).astype(np.uint8)   # abre sombras
    L = cv2.LUT(L, lut)
    a = cv2.addWeighted(a, 0.85, np.full_like(a, 128), 0.15, 0)                                  # tira o azulado
    b = cv2.addWeighted(b, 0.85, np.full_like(b, 128), 0.15, 0)
    return cv2.cvtColor(cv2.merge([L, a, b]), cv2.COLOR_LAB2BGR)


def vinheta(im, forca=0.35):
    h, w = im.shape[:2]
    y, x = np.ogrid[:h, :w]
    d = np.sqrt(((x - w / 2) / (w / 2)) ** 2 + ((y - h / 2) / (h / 2)) ** 2)
    k = 1 - forca * np.clip((d - 0.55) / 0.9, 0, 1) ** 1.6
    return (im * k[..., None]).astype(np.uint8)


def foco(im, pecas, fator=0.22, sigma=70):
    """Escurece o que está fora da peça (fundo quase liso, sem apagar a peça real)."""
    h, w = im.shape[:2]
    m = np.zeros((h, w), np.float32)
    for (x, y, r) in pecas:
        cv2.circle(m, (int(x), int(y)), int(r), 1.0, -1)
    m = cv2.GaussianBlur(m, (0, 0), sigma)
    m = np.clip(m / max(m.max(), 1e-6) * 1.6, 0, 1)[..., None]
    cinza = cv2.cvtColor(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR)
    fundo = (0.6 * cinza + 0.4 * im) * fator + np.array([22, 21, 20]) * (1 - fator)
    return (im * m + fundo * (1 - m)).clip(0, 255).astype(np.uint8)


def nitidez(im):
    borrada = cv2.GaussianBlur(im, (0, 0), 1.4)
    return cv2.addWeighted(im, 1.35, borrada, -0.35, 0)


def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    for k, (nome, cfg) in enumerate(FOTOS.items(), 1):
        im = cv2.imread(str(ENTRADA / nome))
        im, n_px = tira_poeira(im, cfg["pecas"])
        x0, y0, lw = cfg["corte"]
        lh = int(lw * 3 / 4)
        im = im[y0:y0 + lh, x0:x0 + lw]
        im = cv2.resize(im, (1600, 1200), interpolation=cv2.INTER_LANCZOS4)
        esc = 1600 / lw
        pecas = [((x - x0) * esc, (y - y0) * esc, r * esc * 1.25) for (x, y, r) in cfg["pecas"]]
        im = nitidez(foco(tom(im), pecas))
        out = SAIDA / f"foto_real_{k}_1600x1200.jpg"
        cv2.imwrite(str(out), im, [cv2.IMWRITE_JPEG_QUALITY, 94])
        print(out.name, "poeira removida (px):", n_px)


if __name__ == "__main__":
    main()
