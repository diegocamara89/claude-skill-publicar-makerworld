"""Cena de apresentação do passador (capa e vídeo). Roda DENTRO do Blender, pelo contrato
executar(config) de executa_com_relatorio.py (skill modelagem-3d), num Blender separado.

config:
  base      pasta com os *_montagem.stl (furo de 40)
  modo      "capa" (still Cycles com cabos) | "video" (animação EEVEE, quadros PNG)
  saida     arquivo .png (capa) ou pasta dos quadros (video)
  res       [largura, altura]
  amostras  amostras de render
  quadros   lista opcional de quadros para teste (video)
"""
import math
import os

import bpy
from mathutils import Vector

S = 0.001                                    # malhas em mm -> cena em metros
LUZ = [1.0, 0.45]                            # multiplicador de luz ("luz") e luz de baixo ("luz_baixo")


def lin(hexcor):
    h = hexcor.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92 for v in c) + (1.0,)


def material(nome, cor, rug=0.42, coat=0.25, transm=0.0, ior=1.45):
    m = bpy.data.materials.new(nome)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = cor
    b.inputs["Roughness"].default_value = rug
    for k, v in (("Coat Weight", coat), ("Transmission Weight", transm), ("IOR", ior)):
        if k in b.inputs:
            b.inputs[k].default_value = v
    return m


def importa(base, nome, mat):
    bpy.ops.wm.stl_import(filepath=os.path.join(base, f"{nome}_montagem.stl"))
    ob = bpy.context.selected_objects[0]
    ob.name = nome
    ob.scale = (S, S, S)
    try:
        bpy.ops.object.shade_smooth_by_angle(angle=math.radians(35))
    except Exception:
        pass
    ob.data.materials.append(mat)
    return ob


def vidro():
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, -(3.3 + 3.0) * S))
    v = bpy.context.active_object
    v.name = "vidro"
    v.scale = (0.26, 0.26, 6.0 * S)
    bpy.ops.object.transform_apply(scale=True)
    bpy.ops.mesh.primitive_cylinder_add(radius=20.0 * S, depth=0.05, vertices=128, location=(0, 0, 0))
    furo = bpy.context.active_object
    mod = v.modifiers.new("furo", "BOOLEAN")
    mod.object = furo
    mod.operation = "DIFFERENCE"
    bpy.context.view_layer.objects.active = v
    bpy.ops.object.modifier_apply(modifier="furo")
    bpy.data.objects.remove(furo, do_unlink=True)
    # vidro = transparente + brilho (funciona igual em EEVEE e Cycles, sem refração)
    m = bpy.data.materials.new("vidro")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    mix = nt.nodes.new("ShaderNodeMixShader")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    tr.inputs["Color"].default_value = (0.86, 0.95, 0.97, 1.0)
    gl = nt.nodes.new("ShaderNodeBsdfPrincipled")
    gl.inputs["Base Color"].default_value = (0.05, 0.10, 0.11, 1.0)
    gl.inputs["Roughness"].default_value = 0.16    # reflexo suave: lâmpada não vira retângulo no vidro
    fres = nt.nodes.new("ShaderNodeLayerWeight")
    fres.inputs["Blend"].default_value = 0.25
    nt.links.new(fres.outputs["Fresnel"], mix.inputs["Fac"])
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(gl.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    v.data.materials.clear()          # a booleana deixou um espaço de material vazio herdado do cilindro
    v.data.materials.append(m)
    return v


def cabo(y, mat):
    cu = bpy.data.curves.new(f"cabo{y}", "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = 2.5 * S
    cu.bevel_resolution = 10
    cu.resolution_u = 24
    sp = cu.splines.new("BEZIER")
    pts = [(-11.5, y, -90), (-11.5, y, 2), (-26, y * 1.6, 14), (-110, y * 5.0, 20), (-320, y * 12.0, 24)]
    sp.bezier_points.add(len(pts) - 1)
    for bp, (x, yy, z) in zip(sp.bezier_points, pts):
        bp.co = Vector((x * S, yy * S, z * S))
        bp.handle_left_type = bp.handle_right_type = "AUTO"
    ob = bpy.data.objects.new(f"cabo{y}", cu)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(mat)
    return ob


def luzes():
    def area(nome, loc, energia, tam, cor=(1, 1, 1)):
        d = bpy.data.lights.new(nome, "AREA")
        d.energy, d.size, d.color = energia, tam, cor
        o = bpy.data.objects.new(nome, d)
        bpy.context.collection.objects.link(o)
        o.location = loc
        o.rotation_euler = (Vector((0, 0, -0.004)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        o.visible_camera = False              # a lâmpada não aparece no quadro, só a luz dela
        if nome == "recorte":
            o.visible_glossy = False          # (Cycles) o contraluz não se espelha no vidro
    k = LUZ[0]
    area("chave", (-0.16, -0.22, 0.26), 2.6 * k, 0.30)
    area("recorte", (0.18, 0.20, 0.16), 2.2 * k, 0.10, (1.0, 0.62, 0.35))   # contraluz laranja da marca
    area("preenchimento", (0.25, -0.12, 0.05), 0.5 * k, 0.40)
    area("baixo", (0.0, -0.10, -0.15), LUZ[1] * k, 0.30)                    # mostra a porca sob o vidro
    area("baixo2", (0.12, 0.08, -0.12), LUZ[1] * 0.6 * k, 0.25, (1.0, 0.8, 0.65))


def camera(az, el, dist, alvo=(0, 0, -0.004), lente=50):
    cd = bpy.data.cameras.new("cam")
    cd.lens = lente
    cam = bpy.data.objects.new("cam", cd)
    bpy.context.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    tgt = bpy.data.objects.new("alvo", None)
    bpy.context.collection.objects.link(tgt)
    tgt.location = alvo
    c = cam.constraints.new("TRACK_TO")
    c.target, c.track_axis, c.up_axis = tgt, "TRACK_NEGATIVE_Z", "UP_Y"
    cam.location = pos_cam(az, el, dist, alvo)
    return cam, tgt


def pos_cam(az, el, dist, alvo=(0, 0, -0.004)):
    a, e = math.radians(az), math.radians(el)
    return (alvo[0] + dist * math.cos(e) * math.cos(a), alvo[1] + dist * math.cos(e) * math.sin(a),
            alvo[2] + dist * math.sin(e))


def chave(ob, f, **kw):
    for k, v in kw.items():
        setattr(ob, k, v)
        ob.keyframe_insert(k, frame=f)


def executar(cfg):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    base, modo = cfg["base"], cfg["modo"]
    LUZ[0] = cfg.get("luz", 1.0)
    LUZ[1] = cfg.get("luz_baixo", 0.45)
    carvao, laranja, pessego = lin("#26282c"), lin("#ff8a3d"), lin("#ffc9a3")
    pecas = {"bucha": importa(base, "bucha_vidro", material("carvao", carvao, 0.45)),
             "porca": importa(base, "porca", material("carvao2", carvao, 0.5)),
             "disco": importa(base, "disco", material("pessego", pessego, 0.4)),
             "tampa": importa(base, "tampa", material("laranja", laranja, 0.38, 0.35))}
    vidro()
    luzes()
    w = bpy.data.worlds.new("mundo")
    sc.world = w
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = lin("#1b1d21")
    w.node_tree.nodes["Background"].inputs[1].default_value = 1.0
    sc.render.resolution_x, sc.render.resolution_y = cfg["res"]
    sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Medium High Contrast"

    if modo == "capa":
        preto = material("cabo", lin("#0e0f11"), 0.55, 0.1)
        cabo(-3.6, preto)
        cabo(3.6, preto)
        camera(cfg.get("az", 225), cfg.get("el", 34), cfg.get("dist", 0.15), alvo=(cfg.get("dx", 0.0), cfg.get("dy", 0.0), -0.004 + cfg.get("dz", 0.0)))
        sc.render.engine = "CYCLES"
        sc.cycles.samples = cfg.get("amostras", 128)
        sc.cycles.use_denoising = True
        try:
            prefs = bpy.context.preferences.addons["cycles"].preferences
            for tipo in ("OPTIX", "CUDA", "HIP", "ONEAPI"):
                try:
                    prefs.compute_device_type = tipo
                    prefs.get_devices()
                    if any(d.type == tipo for d in prefs.devices):
                        for d in prefs.devices:
                            d.use = True
                        sc.cycles.device = "GPU"
                        break
                except Exception:
                    continue
        except Exception:
            pass
        sc.render.filepath = cfg["saida"]
        bpy.ops.render.render(write_still=True)
        return {"capa": cfg["saida"], "existe": os.path.exists(cfg["saida"]), "device": sc.cycles.device}

    # --- vídeo ---
    motores = [i.identifier for i in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items]
    sc.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in motores else "BLENDER_EEVEE"
    try:
        sc.eevee.taa_render_samples = cfg.get("amostras", 32)
        sc.eevee.use_raytracing = True
    except Exception:
        pass
    sc.render.fps = 30
    sc.frame_start, sc.frame_end = 1, 480
    b, p, d, t = pecas["bucha"], pecas["porca"], pecas["disco"], pecas["tampa"]
    passo = 3.0 * S
    # explodido -> montado, uma peça por vez
    chave(b, 1, location=(0, 0, 0.016)); chave(b, 60, location=(0, 0, 0.016)); chave(b, 130, location=(0, 0, 0))
    curso = 0.012
    chave(p, 1, location=(0, 0, -curso), rotation_euler=(0, 0, 0)); chave(p, 130, location=(0, 0, -curso), rotation_euler=(0, 0, 0))
    chave(p, 220, location=(0, 0, 0), rotation_euler=(0, 0, 2 * math.pi * curso / passo))
    chave(d, 1, location=(0, 0, 0.028)); chave(d, 220, location=(0, 0, 0.028)); chave(d, 280, location=(0, 0, 0))
    chave(t, 1, location=(0, 0, 0.040), rotation_euler=(0, 0, 0)); chave(t, 280, location=(0, 0, 0.040), rotation_euler=(0, 0, 0))
    chave(t, 340, location=(0, 0, 0), rotation_euler=(0, 0, 0))
    chave(t, 385, rotation_euler=(0, 0, math.radians(140))); chave(t, 395, rotation_euler=(0, 0, math.radians(140)))
    chave(t, 440, rotation_euler=(0, 0, 0))
    cam, tgt = camera(-60, 26, 0.24, alvo=(0, 0, 0.004))
    # a câmera desce por baixo do tampo enquanto a porca rosqueia (de cima, o vidro reflete e esconde)
    for f, (az, el, dist, az_alvo) in ((1, (-60, 24, 0.32, 0.018)), (60, (-50, 24, 0.30, 0.016)),
                                        (130, (-20, 10, 0.25, 0.000)), (175, (5, -14, 0.24, -0.010)),
                                        (220, (25, -10, 0.23, -0.008)), (280, (45, 22, 0.21, 0.004)),
                                        (340, (60, 30, 0.19, 0.000)), (440, (120, 52, 0.16, 0.000)),
                                        (480, (130, 55, 0.16, 0.000))):
        chave(tgt, f, location=(0, 0, az_alvo))
        chave(cam, f, location=pos_cam(az, el, dist, (0, 0, az_alvo)))
    pasta = cfg["saida"]
    os.makedirs(pasta, exist_ok=True)
    quadros = cfg.get("quadros") or list(range(1, 481))
    for f in quadros:
        sc.frame_set(f)
        sc.render.filepath = os.path.join(pasta, f"q_{f:04d}.png")
        bpy.ops.render.render(write_still=True)
    return {"quadros": len(quadros), "motor": sc.render.engine, "pasta": pasta}
