"""Capa do MakerWorld (4:3, 1600x1200): render 3D + logo, título e selos."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = Path(__file__).parent
F = "C:/Windows/Fonts/"
CREME, LARANJA, CARVAO, PESSEGO = (246, 238, 230), (255, 138, 61), (30, 32, 36), (255, 201, 163)


def fonte(nome, tam):
    return ImageFont.truetype(F + nome, tam)


def pilula(d, x, y, texto, f, borda, fundo, cor):
    l, t, r, b = d.textbbox((0, 0), texto, font=f)
    w, h = r - l + 44, b - t + 26
    d.rounded_rectangle((x, y, x + w, y + h), radius=h // 2, fill=fundo, outline=borda, width=3)
    d.text((x + 22 - l, y + 13 - t), texto, font=f, fill=cor)
    return x + w + 16


def main(render="capa_render.png", saida_nome="capa_MakerWorld_1600x1200.png", retrato=False):
    base = Image.open(AQUI / "final" / render).convert("RGBA")
    W, H = base.size
    # escurece o canto de cima à esquerda, onde vai o texto (gradiente radial suave)
    sombra = Image.new("L", (W, H), 0)
    ds = ImageDraw.Draw(sombra)
    ds.ellipse((-700, -650, 1250, 700) if not retrato else (-500, -700, 1700, 900), fill=190)
    sombra = sombra.filter(ImageFilter.GaussianBlur(160))
    base = Image.composite(Image.new("RGBA", (W, H), CARVAO + (255,)), base, sombra)
    d = ImageDraw.Draw(base)

    logo = Image.open(AQUI / "logo_bytelayer.png").convert("RGBA").resize((118, 118), Image.LANCZOS)
    base.alpha_composite(logo, (72, 64))
    d.text((208, 98), "ByteLayer", font=fonte("seguibl.ttf", 50), fill=CREME)

    y = 250
    d.text((70, y), "PASSADOR DE CABO", font=fonte("seguibl.ttf", 96), fill=CREME)
    d.text((70, y + 104), "COM ROSCA", font=fonte("seguibl.ttf", 96), fill=LARANJA)
    d.rectangle((74, y + 232, 250, y + 238), fill=LARANJA)
    d.text((72, y + 258), "Prende em vidro e madeira. Sem cola.", font=fonte("segoeuib.ttf", 40), fill=CREME)

    fp = fonte("segoeuib.ttf", 30)
    x = 72
    x = pilula(d, x, y + 340, "35 · 40 · 50 · 60 mm", fp, LARANJA, LARANJA, CARVAO)
    x = pilula(d, x, y + 340, "Vidro e Madeira", fp, PESSEGO, (0, 0, 0, 0), PESSEGO)
    pilula(d, 72, y + 412, "Imprime sem suporte", fp, PESSEGO, (0, 0, 0, 0), PESSEGO)

    saida = AQUI / "final" / saida_nome
    base.convert("RGB").save(saida, quality=95)
    print(saida)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "3x4":
        main("capa_render_3x4.png", "capa_App_3x4_1200x1600.png", retrato=True)
    else:
        main()
