"""Vídeo de remix no Blender: peças lado a lado, faces novas em laranja, câmera por quadros-chave.
Roda DENTRO do Blender pelo contrato executar(config) (skill modelagem-3d: trabalho_blender.py --script este
--config cena.json --resultado res.json --tempo-limite 3500). Sem `-I` no Python do hospedeiro: o executor importa
roda_blender da própria pasta.

cena.json (mm; as malhas vêm de destaca_mudancas.py, já na pose do vídeo):
{
  "pecas": [{"base": ".../A_base.stl", "novo": ".../A_novo.stl", "dx": -170, "girar_z": false},
            {"base": ".../B_base.stl", "novo": ".../B_novo.stl", "dx": 170, "girar_z": true}],
  "cameras": [[0, [-270,-400,210], [0,0,50], 40], [130, [270,-400,190], [0,0,50], 40], ...],
  "saida": ".../quadros", "res": [1920,1080], "amostras": 32, "quadros": [0,100,250]   (opcional: teste)
}
Teste com 6 quadros em 960x540 antes do lote (9 s); o lote de 571 quadros 1080p levou 6 min em 11/10/2026.
Lições: peça clara demais apaga o laranja (base #1f2124 + fundo #2a2d33 + emissão 1,2 no laranja);
deixe espaço livre para a legenda em cada plano; a câmera deve olhar a face onde está a mudança.
"""
import math
import os

import bpy
from mathutils import Vector

S = 0.001


def lin(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92 for v in c) + (1.0,)


def material(nome, cor, rug=0.45, emis=0.0):
    m = bpy.data.materials.new(nome)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = cor
    b.inputs["Roughness"].default_value = rug
    if emis:
        b.inputs["Emission Color"].default_value = cor
        b.inputs["Emission Strength"].default_value = emis
    return m


def importa(caminho, mat, nome):
    bpy.ops.wm.stl_import(filepath=caminho)
    ob = bpy.context.selected_objects[0]
    ob.name = nome
    ob.data.materials.clear()
    ob.data.materials.append(mat)
    return ob


def luzes():
    for nome, loc, energia, tam, cor in (("chave", (-0.35, -0.55, 0.55), 45, 0.8, (1, 1, 1)),
                                         ("recorte", (0.40, 0.45, 0.30), 40, 0.3, (1.0, 0.62, 0.35)),
                                         ("preench", (0.55, -0.35, 0.10), 18, 0.6, (1, 1, 1)),
                                         ("baixo", (-0.10, -0.25, -0.40), 22, 0.5, (1, 1, 1))):
        d = bpy.data.lights.new(nome, "AREA")
        d.energy, d.size, d.color = energia, tam, cor
        o = bpy.data.objects.new(nome, d)
        bpy.context.collection.objects.link(o)
        o.location = loc
        o.rotation_euler = (Vector((0, 0, 0.05)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        o.visible_camera = False


def executar(cfg):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    base = material("base", lin(cfg.get("cor_base", "#1f2124")), 0.42)
    novo = material("novo", lin(cfg.get("cor_novo", "#ff8a3d")), 0.35, emis=1.2)
    for k, p in enumerate(cfg["pecas"]):
        vazio = bpy.data.objects.new(f"peca{k}", None)
        bpy.context.collection.objects.link(vazio)
        for arq, mat, nome in ((p["base"], base, f"p{k}_base"), (p["novo"], novo, f"p{k}_novo")):
            importa(arq, mat, nome).parent = vazio
        vazio.scale = (S, S, S)
        vazio.rotation_euler = (0, 0, math.pi if p.get("girar_z") else 0)
        vazio.location = (p.get("dx", 0) * S, p.get("dy", 0) * S, 0)
    luzes()
    w = bpy.data.worlds.new("mundo")
    sc.world = w
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = lin(cfg.get("fundo", "#2a2d33"))
    cd = bpy.data.cameras.new("cam")
    cam = bpy.data.objects.new("cam", cd)
    bpy.context.collection.objects.link(cam)
    sc.camera = cam
    alvo = bpy.data.objects.new("alvo", None)
    bpy.context.collection.objects.link(alvo)
    c = cam.constraints.new("TRACK_TO")
    c.target, c.track_axis, c.up_axis = alvo, "TRACK_NEGATIVE_Z", "UP_Y"
    for f, pos, tgt, lente in cfg["cameras"]:
        cam.location = Vector(pos) * S
        cam.keyframe_insert("location", frame=f)
        alvo.location = Vector(tgt) * S
        alvo.keyframe_insert("location", frame=f)
        cd.lens = lente
        cd.keyframe_insert("lens", frame=f)
    fim = cfg["cameras"][-1][0]
    sc.frame_start, sc.frame_end = 0, fim
    sc.render.fps = 30
    sc.render.resolution_x, sc.render.resolution_y = cfg.get("res", [1920, 1080])
    sc.render.resolution_percentage = 100
    for eng in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
        try:
            sc.render.engine = eng
            break
        except TypeError:
            continue
    try:
        sc.eevee.taa_render_samples = cfg.get("amostras", 32)
    except Exception:
        pass
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Medium High Contrast"
    sc.render.image_settings.file_format = "PNG"
    os.makedirs(cfg["saida"], exist_ok=True)
    quadros = cfg.get("quadros") or list(range(0, fim + 1))
    for f in quadros:
        sc.frame_set(f)
        sc.render.filepath = os.path.join(cfg["saida"], f"q_{f:04d}.png")
        bpy.ops.render.render(write_still=True)
    return {"quadros": len(quadros), "motor": sc.render.engine, "versao": bpy.app.version_string}
