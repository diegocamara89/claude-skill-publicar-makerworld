"""Separa as faces que mudaram num remix (para pintar de laranja no vídeo).

Uso: python destaca_mudancas.py <original.stl> <novo.stl> <prefixo_saida> [--mover x,y,z] [--girar eixo:graus ...]
                                [--tol 0.05] [--final eixo:graus ...]

- --girar / --mover levam o ORIGINAL ao referencial do novo (nesta ordem: girar, depois mover).
  Ex. do suporte Arzopa: peça B = --girar x:90 --mover 7,0,57.5.
- Face nova = centro da face a mais de --tol mm da superfície do original (corte, chanfro, rampa, base nova).
  Faces coplanares com o original contam como antigas, mesmo recortadas.
- --final gira as duas saídas para a pose do vídeo (ex. a orientação de impressão: --final y:90).
Saída: <prefixo>_base.stl e <prefixo>_novo.stl (cascas abertas, só para render) e a área nova em mm².
Confira a mediana de distância das antigas (~0): se não for, o alinhamento está errado.
"""
import sys

import numpy as np
import trimesh

T = trimesh.transformations
EIXO = {"x": [1, 0, 0], "y": [0, 1, 0], "z": [0, 0, 1]}


def giros(lista):
    m = np.eye(4)
    for g in lista:
        e, graus = g.split(":")
        m = T.rotation_matrix(np.radians(float(graus)), EIXO[e]) @ m
    return m


def main(a):
    def tira(flag, varios=False):
        nonlocal a
        vals = []
        while flag in a:
            k = a.index(flag); vals.append(a[k + 1]); a = a[:k] + a[k + 2:]
        return vals if varios else (vals[0] if vals else None)
    mover, tol = tira("--mover"), float(tira("--tol") or 0.05)
    girar, final = tira("--girar", True), tira("--final", True)
    orig, novo = trimesh.load(a[0]), trimesh.load(a[1])
    orig.apply_transform(giros(girar))
    if mover:
        orig.apply_translation([float(v) for v in mover.split(",")])
    _, d, _ = trimesh.proximity.closest_point(orig, novo.triangles_center)
    nov = d > tol
    print(f"faces {len(novo.faces)}, novas {nov.sum()}, área nova {novo.area_faces[nov].sum():.0f} mm², "
          f"mediana das antigas {np.median(d[~nov]):.4f} mm")
    m_final = giros(final)
    pose = novo.copy(); pose.apply_transform(m_final); zmin = pose.bounds[0][2]
    for nome, mask in (("base", ~nov), ("novo", nov)):
        sm = novo.submesh([np.where(mask)[0]], append=True)
        sm.apply_transform(m_final); sm.apply_translation([0, 0, -zmin])
        sm.export(f"{a[2]}_{nome}.stl")


if __name__ == "__main__":
    main(sys.argv[1:])
