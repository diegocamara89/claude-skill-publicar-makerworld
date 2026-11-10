"""Valida o pacote local e compara uma captura do rascunho/página reaberta.

Não acessa o MakerWorld, não faz login e não envia arquivos.
"""
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import unicodedata
import zipfile


CAMPOS = ("titulo", "resumo", "descricao", "tags", "categoria", "licenca",
          "perfil_titulo", "perfil_descricao")
GRUPOS = ("modelos", "capa", "capa_app", "galeria", "video",
          "model_pictures", "perfil_fotos", "perfil_arquivo")
TIPOS = {"3mf", "stl", "scad", "foto_real", "render", "animacao", "texto"}
LICENCAS = {"CC BY-NC 4.0": "BY-NC", "CC BY-NC-SA 4.0": "BY-NC-SA"}


class HtmlEditor(HTMLParser):
    """Compara conteúdo e estrutura; ignora wrappers e controles do CKEditor."""
    # O editor do piloto descartou <hr>; divisores decorativos não fazem parte da assinatura.
    semanticos = set("p h1 h2 h3 h4 h5 h6 ul ol li table caption tr th td strong em u s a br img blockquote pre code".split())
    vazios = set("area base br col embed hr img input link meta param source track wbr".split())

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.pilha, self.eventos, self.buffer, self.texto = [], [], [], []

    def flush(self):
        self.eventos.extend(("texto", x) for x in re.findall(r"\w+|[^\w\s]", unicodedata.normalize("NFC", "".join(self.buffer))))
        self.buffer.clear()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        ignorado = bool(self.pilha and self.pilha[-1][2]) or tag in {"script", "style", "svg"} or any(
            x.startswith("ck-widget__") or x == "ck-table-column-resizer" for x in attrs.get("class", "").split())
        canonico = {"b": "strong", "i": "em", "strike": "s"}.get(tag, tag)
        emitir = not ignorado and canonico in self.semanticos
        if emitir:
            self.flush()
            relevantes = tuple((k, attrs[k]) for k in ("href", "src", "alt", "rowspan", "colspan", "start") if k in attrs)
            self.eventos.append(("abre", canonico, relevantes))
            if canonico not in {"strong", "em", "u", "s", "a", "code", "img"}:
                self.texto.append(" ")
        if tag not in self.vazios:
            self.pilha.append((tag, canonico if emitir else None, ignorado))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.vazios:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag in self.vazios:
            return
        if not self.pilha or self.pilha[-1][0] != tag:
            raise ValueError(f"HTML com fechamento inesperado: {tag}.")
        _, canonico, _ = self.pilha.pop()
        if canonico:
            self.flush()
            self.eventos.append(("fecha", canonico))
            if canonico not in {"strong", "em", "u", "s", "a", "code"}:
                self.texto.append(" ")

    def handle_data(self, data):
        if not self.pilha or not self.pilha[-1][2]:
            self.buffer.append(data)
            self.texto.append(data)


def assinatura_html(html):
    if not isinstance(html, str) or not html.strip():
        raise ValueError("HTML ausente ou vazio.")
    parser = HtmlEditor()
    parser.feed(html)
    parser.close()
    parser.flush()
    if parser.pilha:
        raise ValueError("HTML com elementos não fechados.")
    texto = re.findall(r"\w+|[^\w\s]", unicodedata.normalize("NFC", "".join(parser.texto)))
    return parser.eventos, texto


def conferir_html(esperado, observado):
    return assinatura_html(esperado) == assinatura_html(observado)


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
    sem_perfil = pacote.get("sem_perfil") is True
    for nome in CAMPOS:
        if sem_perfil and nome.startswith("perfil_"):
            continue
        valor = campos.get(nome)
        if not isinstance(valor, str) or not valor.strip():
            erros.append(f"Campo ausente ou inválido: {nome}.")
    if isinstance(campos.get("titulo"), str) and len(campos["titulo"]) > 50:
        erros.append("Título excede os 50 caracteres observados no formulário.")
    if isinstance(campos.get("perfil_titulo"), str) and len(campos["perfil_titulo"]) > 60:
        erros.append("Título do perfil excede os 60 caracteres observados no formulário.")
    if isinstance(campos.get("tags"), str):
        tags = [x.strip() for x in campos["tags"].split(",")]
        if len(tags) > 50 or any(not x or len(x) > 100 for x in tags):
            erros.append("Tags: máximo de 50 entradas, até 100 caracteres por entrada.")

    midia = pacote.get("midia", {})
    if not isinstance(midia, dict):
        midia = {}
    if sem_perfil and (pacote.get("perfil") or midia.get("perfil_fotos") or midia.get("perfil_arquivo")):
        erros.append("sem_perfil exige perfil e anexos de perfil vazios.")
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
                if grupo not in ("modelos", "perfil_arquivo", "fontes") and caminho.stat().st_size > 30 * 1024 * 1024:
                    raise ValueError("Mídia excede os 30 MB registrados na skill.")
                if grupo in ("modelos", "perfil_arquivo"):
                    if entrada["tipo"] not in ("3mf", "stl", "scad") or caminho.suffix.lower() != "." + entrada["tipo"]:
                        raise ValueError("Modelo deve ser 3MF, STL ou SCAD, com extensão correspondente.")
                    if grupo == "perfil_arquivo" and entrada["tipo"] != "3mf":
                        raise ValueError("Perfil de impressão exige 3MF.")
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
    if midia.get("perfil_arquivo") and len(midia["perfil_arquivo"]) != 1:
        erros.append("perfil_arquivo: definir um 3MF por perfil nesta entrada.")
    if fotos_modelo & fotos_galeria:
        erros.append("Model Pictures repete uma foto da galeria.")
    for grupo in ("galeria", "model_pictures", "perfil_fotos"):
        if sem_perfil and grupo == "perfil_fotos":
            continue
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
    editores = pacote.get("editores", {})
    if not isinstance(editores, dict):
        erros.append("editores deve ser um objeto.")
        editores = {}
    for nome, entrada in editores.items():
        try:
            if nome not in ("descricao", "perfil_descricao") or not isinstance(entrada, dict) or entrada.get("tipo") != "texto":
                raise ValueError("Editor desconhecido ou entrada de HTML inválida.")
            caminho = caminho_local(arquivo_json.parent, entrada.get("arquivo"))
            if caminho.stat().st_size != entrada.get("bytes") or sha256(caminho) != entrada.get("sha256"):
                raise ValueError("HTML mudou desde a revisão.")
            assinatura_html(caminho.read_text(encoding="utf-8-sig"))
        except (ValueError, OSError) as e:
            erros.append(f"editores/{nome}: {e}")
    perfil = pacote.get("perfil", {})
    if not isinstance(perfil, dict) or (perfil and (type(perfil.get("placas")) is not int or perfil["placas"] < 1)):
        erros.append("perfil.placas deve ser o número positivo de placas esperado no site.")
    elif perfil:
        entradas_modelo = [e for g in ("modelos", "perfil_arquivo") for e in midia.get(g, []) if isinstance(e, dict)]
        if not any(e.get("arquivo") == perfil.get("arquivo") and e.get("tipo") == "3mf" for e in entradas_modelo):
            erros.append("perfil.arquivo deve apontar para um 3MF revisado em modelos ou perfil_arquivo.")
    if not isinstance(pacote.get("formulario", {}), dict):
        erros.append("formulario deve ser um objeto.")
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
    if not resultado["integridade_ok"]:
        resultado["conferencia_ok"] = False
        return resultado
    if not isinstance(captura.get("campos"), dict) or not isinstance(captura.get("anexos"), dict):
        raise ValueError("A captura precisa conter campos e anexos como objetos.")
    if not isinstance(captura.get("envios", {}), dict) or not isinstance(captura.get("perfil", {}), dict):
        raise ValueError("envios e perfil da captura devem ser objetos.")
    estado = captura.get("estado")
    if estado not in ("rascunho_salvo", "publicado") or captura.get("reaberto") is not True:
        erros.append("A captura deve vir do rascunho salvo ou modelo publicado, reaberto.")
    from urllib.parse import urlparse
    url = urlparse(captura.get("url", ""))
    if url.scheme != "https" or url.hostname != "makerworld.com" or not captura.get("id"):
        erros.append("Faltam URL MakerWorld e identificador observado na página salva.")
    if captura.get("conta") != pacote.get("conta"):
        erros.append("Conta observada difere da conta de destino.")
    if pacote.get("sem_perfil") is True and captura.get("perfil"):
        erros.append("A captura inclui um perfil para postagem declarada sem_perfil.")
    if estado == "rascunho_salvo" and pacote.get("rascunho", {}).get("id") and str(captura.get("id")) != str(pacote["rascunho"]["id"]):
        erros.append("A captura pertence a outro rascunho.")
    for nome in CAMPOS:
        if pacote.get("sem_perfil") is True and nome.startswith("perfil_"):
            continue
        esperado = pacote.get("campos", {}).get(nome)
        observado = captura.get("campos", {}).get(nome)
        entrada_html = pacote.get("editores", {}).get(nome)
        if entrada_html:
            try:
                html = caminho_local(Path(arquivo_json).parent, entrada_html["arquivo"]).read_text(encoding="utf-8-sig")
                if not conferir_html(html, captura["campos"].get(nome + "_html")):
                    erros.append(f"HTML salvo divergente: {nome}.")
            except (ValueError, OSError, KeyError) as e:
                erros.append(f"HTML/{nome}: {e}")
            continue
        if captura["campos"].get(nome + "_html") is not None:
            erros.append(f"Falta HTML revisado em editores/{nome}; não comparar Markdown com HTML.")
            continue
        if nome == "licenca":
            esperado = LICENCAS.get(esperado, esperado)
            observado = LICENCAS.get(observado, observado)
        if nome == "categoria":
            esperado = pacote.get("formulario", {}).get("categoria", esperado)
        if nome == "tags" and isinstance(observado, list) and all(isinstance(x, str) for x in observado):
            esperado = [normalizar(x).lower() for x in esperado.split(",")]
            observado = [normalizar(x).lower() for x in observado]
        if normalizar(esperado) != normalizar(observado):
            erros.append(f"Campo salvo divergente: {nome}.")
    for grupo in GRUPOS:
        if grupo == "perfil_arquivo" and not pacote.get("midia", {}).get(grupo):
            continue  # Compatibilidade com os pacotes anteriores, que agrupavam o 3MF em modelos.
        observados = captura["anexos"].get(grupo)
        if isinstance(observados, list) and observados and isinstance(observados[0], dict):
            # As URLs CDN não conservam o nome local: conferir pelo vínculo observado no envio.
            recibos = captura.get("envios", {}).get(grupo, [])
            if not isinstance(recibos, list) or any(not isinstance(x, dict) for x in (*recibos, *observados)):
                erros.append(f"Comprovantes ou anexos inválidos: {grupo}.")
                continue
            esperados = pacote.get("midia", {}).get(grupo, [])
            nomes = [x.get("arquivo") for x in recibos]
            hashes = [x.get("sha256") for x in recibos]
            ids = [x.get("identidade") for x in recibos]
            ids_observados = [x.get("identidade") for x in observados]
            ok = (nomes == resultado["anexos_esperados"][grupo] and
                  hashes == [x["sha256"] for x in esperados] and ids == ids_observados and
                  all(isinstance(x, str) and x for x in ids) and len(set(ids)) == len(ids))
        else:
            ok = observados == resultado["anexos_esperados"][grupo]
        if not ok:
            erros.append(f"Anexos salvos divergentes ou fora de ordem: {grupo}.")
    if pacote.get("perfil"):
        if captura.get("perfil", {}).get("placas") != pacote["perfil"]["placas"]:
            erros.append("Placas reconhecidas no perfil divergem do pacote.")
        nome_3mf = Path(pacote["perfil"].get("arquivo", "")).name
        if captura.get("perfil", {}).get("arquivos") != [nome_3mf]:
            erros.append("O arquivo 3MF observado no perfil diverge do pacote.")
    if estado == "publicado" and not resultado["apto_publicar"]:
        erros.append("Publicação declarada com pendências locais ainda abertas.")
    resultado.update({"conferencia_ok": not erros, "erros": erros, "estado_observado": estado})
    return resultado


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("acao", choices=("validar", "conferir", "conferir-html"))
    parser.add_argument("postagem", type=Path)
    parser.add_argument("--captura", type=Path)
    parser.add_argument("--exigir-publicacao", action="store_true")
    parser.add_argument("--saida", type=Path)
    parser.add_argument("--campo", choices=("descricao_html", "perfil_descricao_html"), default="descricao_html")
    args = parser.parse_args()
    if args.acao in ("conferir", "conferir-html") and not args.captura:
        parser.error("A conferência exige --captura.")
    if args.acao == "conferir-html" and args.exigir_publicacao:
        parser.error("Conferir apenas HTML não comprova aptidão para publicar.")
    try:
        if args.acao == "conferir-html":
            captura = ler_json(args.captura)
            observado = captura.get("campos", {}).get(args.campo)
            if observado is None and args.campo == "perfil_descricao_html":
                editores = captura.get("editores", [])
                if isinstance(editores, list) and len(editores) == 1 and isinstance(editores[0], dict):
                    observado = editores[0].get("html")
            ok = conferir_html(args.postagem.read_text(encoding="utf-8-sig"), observado)
            resultado = {"integridade_ok": True, "conferencia_ok": ok,
                         "erros": [] if ok else ["HTML salvo difere do HTML revisado."]}
        else:
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
