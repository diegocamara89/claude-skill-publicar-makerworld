"""Valida o pacote local e compara uma captura do rascunho/página reaberta.

Não acessa o MakerWorld, não faz login e não envia arquivos.
"""
import argparse
import hashlib
import json
from pathlib import Path
import unicodedata
import zipfile


CAMPOS = ("titulo", "resumo", "descricao", "tags", "categoria", "licenca",
          "perfil_titulo", "perfil_descricao")
GRUPOS = ("modelos", "capa", "capa_app", "galeria", "video",
          "model_pictures", "perfil_fotos")
TIPOS = {"3mf", "stl", "foto_real", "render", "animacao", "texto"}


def ler_json(caminho):
    dados = json.loads(Path(caminho).read_text(encoding="utf-8-sig"))
    if not isinstance(dados, dict):
        raise ValueError("A raiz do JSON deve ser um objeto.")
    return dados


def sha256(caminho):
    with Path(caminho).open("rb") as arquivo:
        return hashlib.file_digest(arquivo, "sha256").hexdigest()


def caminho_local(raiz, nome):
    if not isinstance(nome, str) or not nome or Path(nome).is_absolute():
        raise ValueError("O caminho deve ser relativo à pasta da postagem.")
    caminho = (raiz / nome).resolve()
    if not caminho.is_relative_to(raiz.resolve()):
        raise ValueError("O caminho sai da pasta da postagem.")
    return caminho


def validar(arquivo_json):
    arquivo_json = Path(arquivo_json)
    pacote = ler_json(arquivo_json)
    erros, pendencias, anexos = [], [], {}
    if pacote.get("versao_schema") != 1:
        erros.append("versao_schema deve ser 1.")
    if not isinstance(pacote.get("conta"), str) or not pacote["conta"].strip():
        erros.append("Conta de destino ausente.")
    campos = pacote.get("campos", {})
    if not isinstance(campos, dict):
        campos = {}
    for nome in CAMPOS:
        valor = campos.get(nome)
        if not isinstance(valor, str) or not valor.strip():
            erros.append(f"Campo ausente ou inválido: {nome}.")
    if isinstance(campos.get("titulo"), str) and len(campos["titulo"]) > 50:
        erros.append("Título excede os 50 caracteres observados no formulário.")
    if isinstance(campos.get("tags"), str):
        tags = [x.strip() for x in campos["tags"].split(",")]
        if len(tags) > 50 or any(not x or len(x) > 100 for x in tags):
            erros.append("Tags: máximo de 50 entradas, até 100 caracteres por entrada.")

    midia = pacote.get("midia", {})
    if not isinstance(midia, dict):
        midia = {}
    fotos_modelo, fotos_galeria = set(), set()
    tem_3mf = False
    for grupo in (*GRUPOS, "fontes"):
        entradas = pacote.get("fontes", []) if grupo == "fontes" else midia.get(grupo, [])
        if not isinstance(entradas, list):
            erros.append(f"{grupo} deve ser uma lista.")
            continue
        anexos[grupo] = []
        vistos = set()
        for entrada in entradas:
            try:
                if not isinstance(entrada, dict) or entrada.get("tipo") not in TIPOS:
                    raise ValueError("Tipo de arquivo ausente ou inválido.")
                caminho = caminho_local(arquivo_json.parent, entrada.get("arquivo"))
                if not caminho.is_file() or caminho.stat().st_size == 0:
                    raise ValueError("Arquivo ausente ou vazio.")
                digest = sha256(caminho)
                if digest != entrada.get("sha256") or caminho.stat().st_size != entrada.get("bytes"):
                    raise ValueError("Conteúdo ou tamanho mudou desde a revisão.")
                if digest in vistos:
                    raise ValueError("Arquivo duplicado neste campo, inclusive com outro nome.")
                vistos.add(digest)
                if grupo in ("galeria", "model_pictures", "perfil_fotos", "capa", "capa_app") and entrada["tipo"] not in ("foto_real", "render", "animacao"):
                    raise ValueError("Este campo exige mídia visual.")
                if grupo == "video" and entrada["tipo"] != "animacao":
                    raise ValueError("Vídeo deve ser declarado como animação.")
                if grupo not in ("modelos", "fontes") and caminho.stat().st_size > 30 * 1024 * 1024:
                    raise ValueError("Mídia excede os 30 MB registrados na skill.")
                if grupo == "modelos":
                    if entrada["tipo"] not in ("3mf", "stl") or caminho.suffix.lower() != "." + entrada["tipo"]:
                        raise ValueError("Modelo deve ser 3MF ou STL, com extensão correspondente.")
                    if entrada["tipo"] == "3mf":
                        with zipfile.ZipFile(caminho) as z:
                            if z.testzip() or not {"[Content_Types].xml", "3D/3dmodel.model"}.issubset(z.namelist()):
                                raise ValueError("Estrutura 3MF inválida.")
                        tem_3mf = True
                if grupo in ("capa", "capa_app", "model_pictures", "perfil_fotos") and entrada["tipo"] not in ("foto_real", "render"):
                    raise ValueError("Este campo exige imagem, não animação ou texto.")
                if grupo in ("galeria", "model_pictures", "perfil_fotos") and entrada["tipo"] == "foto_real":
                    if grupo == "galeria":
                        fotos_galeria.add(digest)
                    elif grupo == "model_pictures":
                        fotos_modelo.add(digest)
                anexos[grupo].append(caminho.name)
            except (ValueError, OSError, zipfile.BadZipFile, KeyError) as e:
                nome = entrada.get("arquivo", "?") if isinstance(entrada, dict) else "?"
                erros.append(f"{grupo}/{nome}: {e}")
    if not tem_3mf:
        erros.append("Nenhum 3MF válido. Não substituir o perfil por STL silenciosamente.")
    for grupo in ("capa", "capa_app"):
        if len(midia.get(grupo, [])) != 1:
            erros.append(f"{grupo}: definir exatamente uma imagem.")
    if fotos_modelo & fotos_galeria:
        erros.append("Model Pictures repete uma foto da galeria.")
    for grupo in ("galeria", "model_pictures", "perfil_fotos"):
        entradas = midia.get(grupo, [])
        if not isinstance(entradas, list) or not any(isinstance(x, dict) and x.get("tipo") == "foto_real" for x in entradas):
            pendencias.append(f"{grupo}: falta foto real declarada e revisada.")
    galeria = midia.get("galeria", [])
    if isinstance(galeria, list) and sum(isinstance(x, dict) and x.get("tipo") == "foto_real" for x in galeria) < 3:
        pendencias.append("Fotos da vida real: são necessárias pelo menos 3 fotos revisadas cobrindo 3 vistas.")
    if isinstance(galeria, list) and galeria and (not isinstance(galeria[0], dict) or galeria[0].get("tipo") != "foto_real"):
        pendencias.append("A primeira imagem da galeria deve ser a foto real instalada.")
    declaradas = pacote.get("pendencias", [])
    if not isinstance(declaradas, list) or any(not isinstance(x, str) or not x.strip() for x in declaradas):
        erros.append("pendencias deve ser uma lista de textos não vazios.")
    else:
        pendencias.extend(declaradas)
    return {"integridade_ok": not erros, "apto_rascunho": not erros,
            "apto_publicar": not erros and not pendencias,
            "erros": erros, "pendencias": pendencias,
            "anexos_esperados": {g: anexos.get(g, []) for g in GRUPOS},
            "sha256_postagem": sha256(arquivo_json)}


def normalizar(valor):
    return unicodedata.normalize("NFC", valor.replace("\r\n", "\n")).strip() if isinstance(valor, str) else valor


def conferir(arquivo_json, captura_json):
    pacote, captura = ler_json(arquivo_json), ler_json(captura_json)
    resultado = validar(arquivo_json)
    erros = list(resultado["erros"])
    if not isinstance(captura.get("campos"), dict) or not isinstance(captura.get("anexos"), dict):
        raise ValueError("A captura precisa conter campos e anexos como objetos.")
    estado = captura.get("estado")
    if estado not in ("rascunho_salvo", "publicado") or captura.get("reaberto") is not True:
        erros.append("A captura deve vir do rascunho salvo ou modelo publicado, reaberto.")
    from urllib.parse import urlparse
    url = urlparse(captura.get("url", ""))
    if url.scheme != "https" or url.hostname != "makerworld.com" or not captura.get("id"):
        erros.append("Faltam URL MakerWorld e identificador observado na página salva.")
    if captura.get("conta") != pacote.get("conta"):
        erros.append("Conta observada difere da conta de destino.")
    for nome in CAMPOS:
        esperado = pacote.get("campos", {}).get(nome)
        observado = captura.get("campos", {}).get(nome)
        if normalizar(esperado) != normalizar(observado):
            erros.append(f"Campo salvo divergente: {nome}.")
    for grupo in GRUPOS:
        if captura.get("anexos", {}).get(grupo) != resultado["anexos_esperados"][grupo]:
            erros.append(f"Anexos salvos divergentes ou fora de ordem: {grupo}.")
    if estado == "publicado" and not resultado["apto_publicar"]:
        erros.append("Publicação declarada com pendências locais ainda abertas.")
    resultado.update({"conferencia_ok": not erros, "erros": erros, "estado_observado": estado})
    return resultado


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("acao", choices=("validar", "conferir"))
    parser.add_argument("postagem", type=Path)
    parser.add_argument("--captura", type=Path)
    parser.add_argument("--exigir-publicacao", action="store_true")
    parser.add_argument("--saida", type=Path)
    args = parser.parse_args()
    if args.acao == "conferir" and not args.captura:
        parser.error("conferir exige --captura.")
    try:
        resultado = conferir(args.postagem, args.captura) if args.acao == "conferir" else validar(args.postagem)
    except (ValueError, OSError, TypeError) as e:
        resultado = {"integridade_ok": False, "apto_publicar": False, "erros": [str(e)]}
    texto = json.dumps(resultado, ensure_ascii=False, indent=2)
    if args.saida:
        args.saida.parent.mkdir(parents=True, exist_ok=True)
        args.saida.write_text(texto + "\n", encoding="utf-8")
    print(texto)
    ok = resultado.get("conferencia_ok", resultado["integridade_ok"])
    return 0 if ok and (not args.exigir_publicacao or resultado["apto_publicar"]) else 2


if __name__ == "__main__":
    raise SystemExit(main())
