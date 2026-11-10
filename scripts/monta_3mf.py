"""Monta um 3MF de publicação (1 placa) com qualquer conjunto de peças e, opcionalmente, exporta pelo Bambu Studio.

As peças entram JÁ na orientação de impressão (o script não gira nada) e são enfileiradas em Y no centro da mesa.
A configuração vem de um 3MF-gabarito com impressora, filamento de SISTEMA e chapa certos (ex.: um 3MF de
publicação anterior). O processo pode ser trocado por um perfil de sistema achatado (flatten-profile.mjs).
Nenhuma mudança fora do sistema fica sem lista: `different_settings_to_system` sai vazio.

Uso:
  python monta_3mf.py --gabarito modelo.3mf --peca "Suporte A=A.stl" --peca "Suporte B=B.stl" \
      --placa "Par de suportes - sem suporte" --titulo "Suporte X" --saida par_020.3mf \
      [--processo sys_028.json --processo-nome "0.28mm Extra Draft @BBL A1"] [--vao 20] \
      [--exportar ByteLayer_x.3mf --bambu "C:/Program Files/Bambu Studio/bambu-studio.exe"]

--exportar fatia e grava o 3MF completo (placa, miniaturas e G-code embutidos: sem isso o site mostrou
"Placas (0)") na pasta de --saida, e imprime tempo, gramas e se há suporte, lidos do G-code.
"""
import argparse
import json
import re
import subprocess
import uuid
import zipfile
from pathlib import Path

import trimesh

MESA = 256.0
NS = ('xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
      'xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" '
      'xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" requiredextensions="p"')
FIXOS = ("name", "inherits", "from", "setting_id", "instantiation")


def malha(caminho):
    m = trimesh.load(caminho, process=True)
    m.merge_vertices()                      # sopa de triângulos faz o Studio fechar furos
    lo, hi = m.bounds
    m.apply_translation(-(lo + hi) / 2)
    return m, hi - lo


def configura(cfg, processo, processo_nome):
    if processo:
        d = json.load(open(processo, encoding="utf-8"))
        for k, v in d.items():
            if k in cfg and k not in FIXOS:
                cfg[k] = v
        cfg["print_settings_id"] = processo_nome or d.get("name", cfg.get("print_settings_id"))
    cfg["different_settings_to_system"] = ["", "", ""]
    return cfg


def monta(a):
    zm = zipfile.ZipFile(a.gabarito)
    cfg = configura(json.loads(zm.read("Metadata/project_settings.config")), a.processo, a.processo_nome)
    pecas = []
    for p in a.peca:
        nome, arq = p.split("=", 1)
        pecas.append((nome.strip(), *malha(arq.strip())))
    total_y = sum(t[1] for _, _, t in pecas) + a.vao * (len(pecas) - 1)
    maior_x = max(t[0] for _, _, t in pecas)
    if total_y > MESA - 10 or maior_x > MESA - 10:
        raise SystemExit(f"Não cabe na mesa: {maior_x:.0f} x {total_y:.0f} mm (máx. {MESA - 10:.0f}).")
    arquivos, objetos, itens, cfg_obj, insts = {}, [], [], [], []
    y, oid = MESA / 2 - total_y / 2, 1
    for i, (nome, m, tam) in enumerate(pecas):
        cy = y + tam[1] / 2
        y += tam[1] + a.vao
        mid, obj = oid, oid + 1
        oid += 2
        v = "\n".join(f'     <vertex x="{p[0]:.6f}" y="{p[1]:.6f}" z="{p[2]:.6f}"/>' for p in m.vertices)
        t = "\n".join(f'     <triangle v1="{f[0]}" v2="{f[1]}" v3="{f[2]}"/>' for f in m.faces)
        cam = f"/3D/Objects/object_{obj}.model"
        arquivos[cam[1:]] = (f'<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" {NS}>\n'
                             f' <metadata name="BambuStudio:3mfVersion">1</metadata>\n <resources>\n'
                             f'  <object id="{mid}" p:UUID="{uuid.uuid4()}" type="model">\n   <mesh>\n    <vertices>\n{v}\n'
                             f'    </vertices>\n    <triangles>\n{t}\n    </triangles>\n   </mesh>\n  </object>\n'
                             f' </resources>\n <build/>\n</model>\n')
        objetos.append(f'  <object id="{obj}" p:UUID="{uuid.uuid4()}" type="model">\n   <components>\n'
                       f'    <component p:path="{cam}" objectid="{mid}" p:UUID="{uuid.uuid4()}" '
                       f'transform="1 0 0 0 1 0 0 0 1 0 0 0"/>\n   </components>\n  </object>\n')
        itens.append(f'  <item objectid="{obj}" p:UUID="{uuid.uuid4()}" '
                     f'transform="1 0 0 0 1 0 0 0 1 {MESA / 2} {cy:.4f} {tam[2] / 2:.6f}" printable="1"/>\n')
        cfg_obj.append(f'  <object id="{obj}">\n    <metadata key="name" value="{nome}"/>\n'
                       f'    <metadata key="extruder" value="1"/>\n    <part id="{mid}" subtype="normal_part">\n'
                       f'      <metadata key="name" value="{nome}"/>\n'
                       f'      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>\n    </part>\n  </object>\n')
        insts.append(f'    <model_instance>\n      <metadata key="object_id" value="{obj}"/>\n'
                     f'      <metadata key="instance_id" value="0"/>\n      <metadata key="identify_id" value="{100 + i}"/>\n'
                     f'    </model_instance>\n')
    placa = (f'  <plate>\n    <metadata key="plater_id" value="1"/>\n    <metadata key="plater_name" value="{a.placa}"/>\n'
             f'    <metadata key="locked" value="false"/>\n' + "".join(insts) + '  </plate>\n')
    modelo = (f'<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" {NS}>\n'
              ' <metadata name="Application">BambuStudio-02.08.02.61</metadata>\n'
              ' <metadata name="BambuStudio:3mfVersion">1</metadata>\n'
              f' <metadata name="Title">{a.titulo}</metadata>\n <resources>\n' + "".join(objetos) +
              ' </resources>\n <build>\n' + "".join(itens) + ' </build>\n</model>\n')
    rels = ('<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
            + "".join(f' <Relationship Target="/{c}" Id="rel-{k + 1}" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>\n'
                      for k, c in enumerate(arquivos)) + '</Relationships>\n')
    with zipfile.ZipFile(a.saida, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", zm.read("[Content_Types].xml"))
        z.writestr("_rels/.rels", '<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
                   ' <Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>\n</Relationships>\n')
        z.writestr("3D/3dmodel.model", modelo)
        z.writestr("3D/_rels/3dmodel.model.rels", rels)
        for c, x in arquivos.items():
            z.writestr(c, x)
        z.writestr("Metadata/model_settings.config", '<?xml version="1.0" encoding="UTF-8"?>\n<config>\n'
                   + "".join(cfg_obj) + placa + '</config>\n')
        z.writestr("Metadata/project_settings.config", json.dumps(cfg, indent=4, ensure_ascii=False))
        z.writestr("Metadata/slice_info.config", zm.read("Metadata/slice_info.config"))
    print(f"{a.saida}: {len(pecas)} peças, {cfg.get('print_settings_id')}, {cfg.get('filament_settings_id')}")


def exporta(a):
    pasta = Path(a.saida).resolve().parent
    subprocess.run([a.bambu, "--slice", "0", "--export-3mf", a.exportar, "--outputdir", str(pasta), str(Path(a.saida).resolve())],
                   check=False)
    r = json.load(open(pasta / "result.json", encoding="utf-8"))
    if r.get("return_code") != 0:
        raise SystemExit(f"Bambu Studio falhou: {r.get('error_string')}")
    g = zipfile.ZipFile(pasta / a.exportar).read("Metadata/plate_1.gcode").decode("utf-8", "ignore")
    tempo = re.search(r"^; model printing time: ([^;]+);", g, re.M)
    peso = re.search(r"^; total filament weight \[g\] : ([\d.]+)", g, re.M)
    suporte = len(re.findall(r"^; FEATURE: Support", g, re.M))
    print(f"{a.exportar}: tempo {tempo.group(1).strip() if tempo else '?'}, {peso.group(1) if peso else '?'} g, "
          f"trechos de suporte: {suporte}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--gabarito", required=True)
    ap.add_argument("--peca", action="append", required=True, help='"Nome=arquivo.stl", já na orientação de impressão')
    ap.add_argument("--placa", required=True)
    ap.add_argument("--titulo", required=True)
    ap.add_argument("--saida", required=True)
    ap.add_argument("--processo")
    ap.add_argument("--processo-nome")
    ap.add_argument("--vao", type=float, default=20.0)
    ap.add_argument("--exportar")
    ap.add_argument("--bambu", default="C:/Program Files/Bambu Studio/bambu-studio.exe")
    args = ap.parse_args()
    monta(args)
    if args.exportar:
        exporta(args)
