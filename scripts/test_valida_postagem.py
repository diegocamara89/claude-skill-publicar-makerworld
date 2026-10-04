"""Casos negativos essenciais; dados e capturas são sintéticos, sem acesso à conta."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from valida_postagem import CAMPOS, GRUPOS, conferir, sha256, validar


class ValidaPostagemTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.raiz = Path(self.temp.name)
        with zipfile.ZipFile(self.raiz / "kit.3mf", "w") as z:
            z.writestr("[Content_Types].xml", "<Types/>")
            z.writestr("3D/3dmodel.model", "<model/>")
        self.pacote = {
            "versao_schema": 1, "conta": "CONTA_DE_TESTE",
            "campos": {x: "Conteúdo de teste: " + x for x in CAMPOS},
            "midia": {g: [] for g in GRUPOS}, "fontes": [], "pendencias": [],
        }
        self.pacote["midia"]["modelos"] = [self.entrada("kit.3mf", "3mf")]
        for grupo in ("capa", "capa_app", "galeria", "model_pictures", "perfil_fotos"):
            (self.raiz / (grupo + ".png")).write_bytes(("fixture de " + grupo).encode())
            self.pacote["midia"][grupo] = [self.entrada(grupo + ".png", "foto_real")]
        self.json = self.raiz / "POSTAGEM.json"
        for n in (1, 2):
            nome = f"galeria_{n}.png"
            (self.raiz / nome).write_bytes(f"outra vista {n}".encode())
            self.pacote["midia"]["galeria"].append(self.entrada(nome, "foto_real"))

    def entrada(self, nome, tipo):
        arquivo = self.raiz / nome
        return {"arquivo": nome, "tipo": tipo, "sha256": sha256(arquivo), "bytes": arquivo.stat().st_size}

    def salvar(self):
        self.json.write_text(json.dumps(self.pacote, ensure_ascii=False), encoding="utf-8")

    def captura(self):
        self.salvar()
        return {"conta": "CONTA_DE_TESTE", "estado": "rascunho_salvo", "reaberto": True,
                "id": "TESTE_SINTETICO", "url": "https://makerworld.com/pt/models/TESTE_SINTETICO",
                "campos": copy.deepcopy(self.pacote["campos"]),
                "anexos": validar(self.json)["anexos_esperados"]}

    def conferir_captura(self, captura):
        arquivo = self.raiz / "captura_sintetica.json"
        arquivo.write_text(json.dumps(captura), encoding="utf-8")
        return conferir(self.json, arquivo)

    def test_pacote_integro(self):
        self.salvar()
        self.assertTrue(validar(self.json)["apto_publicar"])

    def test_arquivo_alterado(self):
        self.salvar()
        (self.raiz / "galeria.png").write_bytes(b"alterado")
        self.assertFalse(validar(self.json)["integridade_ok"])

    def test_arquivo_ausente(self):
        self.salvar()
        (self.raiz / "kit.3mf").unlink()
        self.assertFalse(validar(self.json)["integridade_ok"])

    def test_caminho_fora_do_pacote(self):
        self.pacote["midia"]["modelos"][0]["arquivo"] = "../fora.3mf"
        self.salvar()
        self.assertFalse(validar(self.json)["integridade_ok"])

    def test_stl_nao_substitui_perfil(self):
        (self.raiz / "kit.stl").write_bytes(b"solid teste")
        self.pacote["midia"]["modelos"] = [self.entrada("kit.stl", "stl")]
        self.salvar()
        self.assertFalse(validar(self.json)["integridade_ok"])

    def test_render_nao_substitui_foto(self):
        self.pacote["midia"]["perfil_fotos"][0]["tipo"] = "render"
        self.salvar()
        resultado = validar(self.json)
        self.assertTrue(resultado["apto_rascunho"])
        self.assertFalse(resultado["apto_publicar"])

    def test_duas_fotos_nao_atendem_minimo(self):
        self.pacote["midia"]["galeria"] = self.pacote["midia"]["galeria"][:2]
        self.salvar()
        self.assertFalse(validar(self.json)["apto_publicar"])

    def test_foto_duplicada_com_outro_nome(self):
        (self.raiz / "copia.png").write_bytes((self.raiz / "galeria.png").read_bytes())
        self.pacote["midia"]["galeria"].append(self.entrada("copia.png", "foto_real"))
        self.salvar()
        self.assertFalse(validar(self.json)["integridade_ok"])

    def test_model_pictures_repetido(self):
        self.pacote["midia"]["model_pictures"] = [copy.deepcopy(self.pacote["midia"]["galeria"][0])]
        self.salvar()
        self.assertFalse(validar(self.json)["integridade_ok"])

    def test_tags_truncadas_nao_passam(self):
        self.pacote["campos"]["tags"] = "x" * 101
        self.salvar()
        self.assertFalse(validar(self.json)["integridade_ok"])

    def test_titulo_acima_do_limite(self):
        self.pacote["campos"]["titulo"] = "x" * 51
        self.salvar()
        self.assertFalse(validar(self.json)["integridade_ok"])

    def test_tags_total_acima_de_100_e_valido(self):
        self.pacote["campos"]["tags"] = ",".join("tag " + str(x) for x in range(30))
        self.salvar()
        self.assertTrue(validar(self.json)["integridade_ok"])

    def test_tags_quantidade_acima_do_limite(self):
        self.pacote["campos"]["tags"] = ",".join(str(x) for x in range(51))
        self.salvar()
        self.assertFalse(validar(self.json)["integridade_ok"])

    def test_captura_conferida(self):
        self.assertTrue(self.conferir_captura(self.captura())["conferencia_ok"])

    def test_campo_salvo_errado(self):
        captura = self.captura()
        captura["campos"]["licenca"] = "Outra licença"
        self.assertFalse(self.conferir_captura(captura)["conferencia_ok"])

    def test_anexo_salvo_ausente(self):
        captura = self.captura()
        captura["anexos"]["modelos"] = []
        self.assertFalse(self.conferir_captura(captura)["conferencia_ok"])

    def test_nao_aceita_apenas_formulario_preenchido(self):
        captura = self.captura()
        captura["reaberto"] = False
        self.assertFalse(self.conferir_captura(captura)["conferencia_ok"])

    def test_publicado_com_pendencia(self):
        captura = self.captura()
        captura["estado"] = "publicado"
        self.pacote["pendencias"] = ["Foto final pendente"]
        self.salvar()
        self.assertFalse(self.conferir_captura(captura)["conferencia_ok"])


if __name__ == "__main__":
    unittest.main()
