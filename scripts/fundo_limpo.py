"""Model Pictures do MakerWorld: a peça real recortada da foto (GrabCut) sobre fundo liso
de uma cor, com sombra suave, 4:3. A peça não é retocada; só o fundo é trocado."""
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).parent
ENTRADA, SAIDA = AQUI / "Fotos reais", AQUI / "final" / "model_pictures"
FUNDO = (236, 236, 234)            # cinza muito claro (BGR), liso

# retângulo que contém a(s) peça(s): x0, y0, x1, y1 (px da foto original)
FOTOS = {
    "WhatsApp Image 2026-09-27 at 08.45.13(1).jpeg": (300, 260, 1000, 690),
    "WhatsApp Image 2026-09-27 at 08.45.13(2).jpeg": (400, 250, 890, 740),
    "WhatsApp Image 2026-09-27 at 08.45.13(3).jpeg": (300, 70, 890, 650),
    "WhatsApp Image 2026-09-27 at 08.45.13.jpeg": (210, 450, 720, 850),
}


def recorta(im, caixa):
    x0, y0, x1, y1 = caixa
    mask = np.zeros(im.shape[:2], np.uint8)
    bgd, fgd = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
    cv2.grabCut(im, mask, (x0, y0, x1 - x0, y1 - y0), bgd, fgd, 8, cv2.GC_INIT_WITH_RECT)
    m = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)
    # fica só com os maiores pedaços (a peça), fecha furinhos e suaviza a borda
    n, rot, st, _ = cv2.connectedComponentsWithStats(m, 8)
    if n > 1:
        areas = st[1:, cv2.CC_STAT_AREA]
        keep = [i + 1 for i, a in enumerate(areas) if a >= 0.15 * areas.max()]
        m = np.isin(rot, keep).astype(np.uint8) * 255
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
    return m


def compoe(im, m):
    ys, xs = np.nonzero(m)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    pw, ph = x1 - x0, y1 - y0
    W, H = 1600, 1200
    esc = min(W * 0.70 / pw, H * 0.66 / ph)
    peca = cv2.resize(im[y0:y1 + 1, x0:x1 + 1], None, fx=esc, fy=esc, interpolation=cv2.INTER_LANCZOS4)
    alfa = cv2.resize(m[y0:y1 + 1, x0:x1 + 1], (peca.shape[1], peca.shape[0]), interpolation=cv2.INTER_LINEAR)
    alfa = cv2.GaussianBlur(alfa, (0, 0), 1.2).astype(np.float32)[..., None] / 255.0
    # luz: abre um pouco as sombras da peça (preta), sem mudar a cor
    lab = cv2.cvtColor(peca, cv2.COLOR_BGR2LAB)
    L = cv2.createCLAHE(clipLimit=1.6, tileGridSize=(6, 6)).apply(lab[..., 0])
    lab[..., 0] = np.clip(L.astype(np.float32) * 1.08 + 6, 0, 255).astype(np.uint8)
    peca = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    tela = np.full((H, W, 3), FUNDO, np.float32)
    # degradê muito leve de cima para baixo (continua lendo como fundo liso)
    grad = np.linspace(1.02, 0.95, H)[:, None, None]
    tela = np.clip(tela * grad, 0, 255)
    ox, oy = (W - peca.shape[1]) // 2, int(H * 0.52 - peca.shape[0] / 2)
    # sombra suave de contato, logo abaixo da peça
    sombra = np.zeros((H, W), np.float32)
    sa = cv2.resize(alfa[..., 0], None, fx=1.0, fy=0.35)
    sy = oy + peca.shape[0] - sa.shape[0] // 2 - 8
    sombra[sy:sy + sa.shape[0], ox:ox + sa.shape[1]] = sa[: max(0, min(sa.shape[0], H - sy))]
    sombra = cv2.GaussianBlur(sombra, (0, 0), 28) * 0.45
    tela *= (1 - sombra[..., None])
    reg = tela[oy:oy + peca.shape[0], ox:ox + peca.shape[1]]
    tela[oy:oy + peca.shape[0], ox:ox + peca.shape[1]] = reg * (1 - alfa) + peca.astype(np.float32) * alfa
    return tela.astype(np.uint8)


def mascara_elipse(im, el):
    """Recorte geométrico: a borda da aba é uma elipse na foto (ajustada por RANSAC na borda real)."""
    m = np.zeros(im.shape[:2], np.uint8)
    (cx, cy), (w, h), ang = el
    cv2.ellipse(m, ((cx, cy), (w - 2, h - 2), ang), 255, -1, cv2.LINE_AA)
    return m


def main():
    import json
    SAIDA.mkdir(parents=True, exist_ok=True)
    elipses = json.load(open(AQUI / "final" / "elipses.json", encoding="utf-8"))
    for k, (nome, caixa) in enumerate(FOTOS.items(), 1):
        im = cv2.imread(str(ENTRADA / nome))
        (c, e, a) = elipses[nome]
        m = mascara_elipse(im, (tuple(c), tuple(e), a))
        cv2.imwrite(str(SAIDA / f"mascara_{k}.png"), m)
        cv2.imwrite(str(SAIDA / f"model_picture_{k}_1600x1200.jpg"), compoe(im, m), [cv2.IMWRITE_JPEG_QUALITY, 94])
        print(k, "peça:", int((m > 0).sum()), "px")


if __name__ == "__main__":
    main()
