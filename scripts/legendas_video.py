"""Legendas e cartela final sobre os quadros do Blender, depois MP4 + GIF com ffmpeg.

Uso: python legendas_video.py <legendas.json> <quadros> <saida_quadros> <logo.png> [--mp4 video.mp4] [--gif video.gif]

legendas.json:
{
  "legendas": [[8, 150, "Título do plano", "subtítulo em laranja", "baixo_esq"],
               [315, 430, "Recorte com rampas de 60°", "e laterais retas", "baixo_dir"], ...],
  "cartela": {"inicio": 522, "titulo": "Suporte de parede · monitor 16\\"", "linha2": "Remix de X e Y · MakerWorld"}
}
Posições: baixo_esq (padrão), baixo_dir, cima_dir. Conferir 5 quadros extraídos do MP4: legenda não pode
cobrir a peça (no suporte Arzopa duas legendas tiveram de mudar de canto e uma de encurtar).
"""
import json
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

F = "C:/Windows/Fonts/"
CREME, LARANJA, CARVAO = (246, 238, 230), (255, 138, 61), (22, 24, 28)
FADE = 12


def main(a):
    def tira(flag):
        nonlocal a
        if flag in a:
            k = a.index(flag); v = a[k + 1]; a = a[:k] + a[k + 2:]; return v
    mp4, gif = tira("--mp4"), tira("--gif")
    cfg = json.load(open(a[0], encoding="utf-8"))
    orig, saida, logo_arq = a[1], a[2], a[3]
    f1, f2 = ImageFont.truetype(F + "seguibl.ttf", 58), ImageFont.truetype(F + "segoeuib.ttf", 38)
    logo = Image.open(logo_arq).convert("RGBA").resize((150, 150), Image.LANCZOS)
    os.makedirs(saida, exist_ok=True)

    def alfa(f, i, fim):
        return 0.0 if f < i or f > fim else min(1.0, (f - i) / FADE, (fim - f) / FADE)

    def legenda(im, k, t1, t2, pos):
        cam = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(cam)
        w = max(d.textlength(t1, font=f1), d.textlength(t2, font=f2))
        x, y = 70, im.size[1] - 210
        if pos == "cima_dir":
            x, y = im.size[0] - 70 - w, 74
        elif pos == "baixo_dir":
            x = im.size[0] - 70 - w
        d.rounded_rectangle((x - 30, y - 24, x + w + 40, y + 150), radius=22, fill=CARVAO + (int(205 * k),))
        d.rectangle((x - 30, y - 24, x - 22, y + 150), fill=LARANJA + (int(255 * k),))
        d.text((x, y), t1, font=f1, fill=CREME + (int(255 * k),))
        d.text((x, y + 82), t2, font=f2, fill=LARANJA + (int(255 * k),))
        return Image.alpha_composite(im, cam)

    def cartela(im, k, c):
        W, H = im.size
        cam = Image.new("RGBA", im.size, CARVAO + (int(225 * k),)); d = ImageDraw.Draw(cam)
        lg = logo.copy(); lg.putalpha(lg.getchannel("A").point(lambda v: int(v * k)))
        cam.alpha_composite(lg, (W // 2 - 360, H // 2 - 170))
        d.text((W // 2 - 190, H // 2 - 140), "ByteLayer", font=ImageFont.truetype(F + "seguibl.ttf", 86), fill=CREME + (int(255 * k),))
        d.text((W // 2 - 360, H // 2 + 20), c["titulo"], font=f2, fill=LARANJA + (int(255 * k),))
        d.text((W // 2 - 360, H // 2 + 80), c.get("linha2", ""), font=ImageFont.truetype(F + "segoeui.ttf", 30), fill=CREME + (int(200 * k),))
        return Image.alpha_composite(im, cam)

    nomes = sorted(n for n in os.listdir(orig) if n.startswith("q_") and n.endswith(".png"))
    for n in nomes:
        f = int(n[2:6]); im = Image.open(os.path.join(orig, n)).convert("RGBA")
        for i, fim, t1, t2, *pos in cfg["legendas"]:
            k = alfa(f, i, fim)
            if k > 0:
                im = legenda(im, k, t1, t2, pos[0] if pos else "baixo_esq")
        c = cfg.get("cartela")
        if c and f >= c["inicio"]:
            im = cartela(im, min(1.0, (f - c["inicio"]) / FADE), c)
        im.convert("RGB").save(os.path.join(saida, n))
    print(len(nomes), "quadros com legenda")
    if mp4:
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "30", "-start_number", nomes[0][2:6],
                        "-i", os.path.join(saida, "q_%04d.png"), "-c:v", "libx264", "-crf", "18", "-preset", "slow",
                        "-pix_fmt", "yuv420p", "-movflags", "+faststart", mp4], check=True)
        print(mp4)
    if gif and mp4:
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp4, "-vf",
                        "fps=12,scale=800:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=160:stats_mode=diff[p];"
                        "[b][p]paletteuse=dither=sierra2_4a", "-loop", "0", gif], check=True)
        print(gif)


if __name__ == "__main__":
    main(sys.argv[1:])
