"""Monta o 3MF de publicação: uma placa por kit (furo 35/40/50/60 × vidro/madeira).

Cada placa: bucha, porca, tampa e disco, na orientação de impressão.
Configuração: perfil de sistema "0.20mm Standard @BBL A1" com uma única mudança listada
(wall_generator = arachne), filamento e impressora do projeto-modelo do dono (PETG, chapa texturizada).

Uso: python monta_publicacao.py <pasta_vN> <modelo_bambu.3mf> <processo_sistema.json> <saida.3mf>
     python monta_publicacao.py <pasta_vN> <modelo> <processo.json> <pasta_destino> --por-kit
"""
import json
import sys
import uuid
import zipfile
from pathlib import Path

import trimesh

DIAMETROS = (35, 40, 50, 60)
KITS = (("vidro", "tampo de vidro até 12 mm"), ("madeira", "tampo de madeira até 30 mm"))
CELULAS = ((64.0, 64.0), (192.0, 64.0), (64.0, 192.0), (192.0, 192.0))   # dentro da mesa 256×256
MESA, VAO = 256.0, 256.0 * 0.2                                          # vão entre placas do Studio
COLUNAS = 3


def malha(caminho):
    m = trimesh.load(caminho, process=True)
    m.merge_vertices()                   # nada de "sopa de triângulos": o Studio fecha furos
    lo, hi = m.bounds
    c = (lo + hi) / 2.0
    m.apply_translation(-c)              # objeto centrado, como o Studio grava
    return m, float(hi[2] - lo[2])


def xml_malha(oid, m):
    v = "\n".join(f'     <vertex x="{x:.6f}" y="{y:.6f}" z="{z:.6f}"/>' for x, y, z in m.vertices)
    t = "\n".join(f'     <triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in m.faces)
    return (f'  <object id="{oid}" p:UUID="{uuid.uuid4()}" type="model">\n   <mesh>\n    <vertices>\n{v}\n'
            f'    </vertices>\n    <triangles>\n{t}\n    </triangles>\n   </mesh>\n  </object>\n')


NS = ('xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
      'xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" '
      'xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" requiredextensions="p"')


def main(pasta, modelo, proc_json, saida, so=None, pecas=("bucha", "porca", "tampa", "disco"), fil_json=None):
    pasta, saida = Path(pasta), Path(saida)
    zm = zipfile.ZipFile(modelo)
    cfg = json.loads(zm.read("Metadata/project_settings.config"))
    std = json.load(open(proc_json, encoding="utf-8"))
    for k, v in std.items():                      # processo = perfil de sistema...
        if k in cfg and k not in ("name", "inherits", "from", "setting_id", "instantiation"):
            cfg[k] = v
    cfg["print_settings_id"] = "0.20mm Standard @BBL A1"
    cfg["wall_generator"] = "arachne"             # ...com uma mudança só, e listada
    dif = list(cfg.get("different_settings_to_system", ["", "", ""]))
    dif[0] = "wall_generator"
    if fil_json:                                  # publicação: filamento de sistema, sem ajuste
        fil = json.load(open(fil_json, encoding="utf-8"))
        for k, v in fil.items():
            if k in cfg and k not in ("name", "inherits", "from", "setting_id", "instantiation",
                                      "filament_settings_id"):
                cfg[k] = v
        cfg["filament_settings_id"] = ["Generic PETG @BBL A1"]
        if "filament_ids" in cfg and fil.get("filament_id"):
            cfg["filament_ids"] = [fil["filament_id"]]
        dif[1] = ""
    cfg["different_settings_to_system"] = dif

    objetos, itens, cfg_obj, placas, arquivos = [], [], [], [], {}
    oid, ident = 1, 100
    lista = [(d, k) for d in DIAMETROS for k in KITS if so is None or (d, k[0]) in so]
    for i, (d, (kit, texto)) in enumerate(lista):
        col, lin = i % COLUNAS, i // COLUNAS
        ox, oy = col * (MESA + VAO), -lin * (MESA + VAO)
        insts = []
        for (nome, arq), (cx, cy) in zip((("bucha", f"bucha_{kit}.stl"), ("porca", "porca.stl"),
                                          ("tampa", "tampa.stl"), ("disco", "disco.stl")), CELULAS):
            if nome not in pecas:
                continue
            m, h = malha(pasta / f"furo_{d}" / arq)
            rotulo = f"{nome}_{d}mm_{kit}" if nome == "bucha" else f"{nome}_{d}mm"
            malha_id, obj_id = oid, oid + 1
            oid += 2
            caminho = f"/3D/Objects/object_{obj_id}.model"
            arquivos[caminho[1:]] = (f'<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" '
                                     f'xml:lang="en-US" {NS}>\n <metadata name="BambuStudio:3mfVersion">1</metadata>\n'
                                     f' <resources>\n{xml_malha(malha_id, m)} </resources>\n <build/>\n</model>\n')
            objetos.append(f'  <object id="{obj_id}" p:UUID="{uuid.uuid4()}" type="model">\n   <components>\n'
                           f'    <component p:path="{caminho}" objectid="{malha_id}" p:UUID="{uuid.uuid4()}" '
                           f'transform="1 0 0 0 1 0 0 0 1 0 0 0"/>\n   </components>\n  </object>\n')
            itens.append(f'  <item objectid="{obj_id}" p:UUID="{uuid.uuid4()}" '
                         f'transform="1 0 0 0 1 0 0 0 1 {ox + cx:.4f} {oy + cy:.4f} {h / 2:.6f}" printable="1"/>\n')
            cfg_obj.append(f'  <object id="{obj_id}">\n    <metadata key="name" value="{rotulo}"/>\n'
                           f'    <metadata key="extruder" value="1"/>\n    <part id="{malha_id}" subtype="normal_part">\n'
                           f'      <metadata key="name" value="{rotulo}"/>\n'
                           f'      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>\n    </part>\n  </object>\n')
            insts.append(f'    <model_instance>\n      <metadata key="object_id" value="{obj_id}"/>\n'
                         f'      <metadata key="instance_id" value="0"/>\n'
                         f'      <metadata key="identify_id" value="{ident}"/>\n    </model_instance>\n')
            ident += 1
        placas.append(f'  <plate>\n    <metadata key="plater_id" value="{i + 1}"/>\n'
                      f'    <metadata key="plater_name" value="Furo {d} mm - {texto}"/>\n'
                      f'    <metadata key="locked" value="false"/>\n' + "".join(insts) + '  </plate>\n')

    modelo_xml = (f'<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" {NS}>\n'
                  ' <metadata name="Application">BambuStudio-02.08.02.61</metadata>\n'
                  ' <metadata name="BambuStudio:3mfVersion">1</metadata>\n'
                  ' <metadata name="Title">Passador de cabo com rosca - furos 35, 40, 50 e 60 mm</metadata>\n'
                  ' <resources>\n' + "".join(objetos) + ' </resources>\n <build>\n' + "".join(itens) + ' </build>\n</model>\n')
    rels = ('<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
            + "".join(f' <Relationship Target="/{c}" Id="rel-{k + 1}" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>\n'
                      for k, c in enumerate(arquivos)) + '</Relationships>\n')
    with zipfile.ZipFile(saida, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", zm.read("[Content_Types].xml"))
        z.writestr("_rels/.rels", '<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
                   ' <Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>\n</Relationships>\n')
        z.writestr("3D/3dmodel.model", modelo_xml)
        z.writestr("3D/_rels/3dmodel.model.rels", rels)
        for c, conteudo in arquivos.items():
            z.writestr(c, conteudo)
        z.writestr("Metadata/model_settings.config", '<?xml version="1.0" encoding="UTF-8"?>\n<config>\n'
                   + "".join(cfg_obj) + "".join(placas) + '</config>\n')
        z.writestr("Metadata/project_settings.config", json.dumps(cfg, indent=4, ensure_ascii=False))
        z.writestr("Metadata/slice_info.config", zm.read("Metadata/slice_info.config"))
    print(f"{saida}: {len(placas)} placas, {len(itens)} objetos")


if __name__ == "__main__":
    if len(sys.argv) > 5 and sys.argv[5] == "--por-kit":   # um 3MF por kit, placa única
        destino = Path(sys.argv[4])
        for d in DIAMETROS:
            for kit, _ in KITS:
                pasta_kit = destino / kit.capitalize()
                pasta_kit.mkdir(parents=True, exist_ok=True)
                main(sys.argv[1], sys.argv[2], sys.argv[3], pasta_kit / f"passador_furo{d}_{kit}.3mf", so={(d, kit)})
    elif len(sys.argv) > 6 and sys.argv[5] == "--publicacao":   # pasta pronta para o MakerWorld
        destino, fil = Path(sys.argv[4]), sys.argv[6]
        destino.mkdir(parents=True, exist_ok=True)
        main(sys.argv[1], sys.argv[2], sys.argv[3], destino / "ByteLayer_passador_de_cabo_TODOS_35-40-50-60.3mf", fil_json=fil)
        for d in DIAMETROS:
            for kit, _ in KITS:
                main(sys.argv[1], sys.argv[2], sys.argv[3], destino / f"ByteLayer_passador_de_cabo_{d}mm_{kit}.3mf",
                     so={(d, kit)}, fil_json=fil)
    elif len(sys.argv) > 6 and sys.argv[5] == "--so-disco":  # só o disco de um furo, para teste
        main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], so={(int(sys.argv[6]), "vidro")}, pecas=("disco",))
    else:
        main(*sys.argv[1:5])
