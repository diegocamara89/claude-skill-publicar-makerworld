// Testes locais com dublês da API documentada; não acessam nem alteram o MakerWorld.
import assert from 'node:assert/strict';
import test from 'node:test';
import { enviarArquivosCampo, enviarLoteCampos, capturarAnexos, consolidarCapturas, salvarTextosPerfil } from './rascunho_makerworld.mjs';

const hash = 'a'.repeat(64);
const entradas = [1, 2, 3].map(i => ({ arquivo: `fotos/${i}.png`, sha256: hash }));
const arquivos = entradas.map(e => `C:/pacote/${e.arquivo}`);
const identidade = i => `https://cdn.example.test/${i}.png`;
const recibos = entradas.map((e, i) => ({ arquivo: `${i + 1}.png`, sha256: e.sha256, identidade: identidade(i + 1) }));

function campoTeste(antes = [], depois = [1, 2, 3], comprovantes = []) {
  let enviados = [], aguardou = false, cliques = 0, quantidade = antes.length;
  const tab = { playwright: { waitForEvent: async () => ({
    isMultiple: () => false, setFiles: async files => { enviados.push(...files); },
  }) }, getAXState: async () => {} };
  const campo = {
    arquivos, entradas, comprovantes, controle: { click: async () => { cliques++; } },
    observar: async () => ({ itens: (aguardou ? depois.slice(0, quantidade) : antes).map(i => ({ identidade: identidade(i) })), pendente: false }),
    aguardar: async total => { quantidade = total; aguardou = true; },
  };
  return { tab, campo, estado: () => ({ enviados, aguardou, cliques }) };
}

test('aguarda conclusão e registra identidades realmente observadas', async () => {
  const f = campoTeste();
  const r = await enviarArquivosCampo(f.tab, f.campo.controle, arquivos, f.campo);
  assert.deepEqual(r.comprovantes, recibos);
  assert.deepEqual(f.estado(), { enviados: arquivos, aguardou: true, cliques: 3 });
});

test('retomada parcial envia somente os arquivos restantes', async () => {
  const f = campoTeste([1], [1, 2, 3], recibos.slice(0, 1));
  const r = await enviarArquivosCampo(f.tab, f.campo.controle, arquivos, f.campo);
  assert.deepEqual(r.comprovantes, recibos);
  assert.deepEqual(f.estado().enviados, arquivos.slice(1));
});

test('lote já conferido não é reenviado', async () => {
  const f = campoTeste([1, 2, 3], [1, 2, 3], recibos);
  const r = await enviarArquivosCampo(f.tab, f.campo.controle, arquivos, f.campo);
  assert.equal(r.retomado, true);
  assert.equal(f.estado().cliques, 0);
});

test('campo ocupado sem vínculo ou com arquivo alterado bloqueia antes do clique', async () => {
  for (const comprovantes of [[], [{ ...recibos[0], sha256: 'b'.repeat(64) }]]) {
    const f = campoTeste([1], [1, 2, 3], comprovantes);
    await assert.rejects(enviarArquivosCampo(f.tab, f.campo.controle, arquivos, f.campo), /comprovantes/);
    assert.equal(f.estado().cliques, 0);
  }
});

test('upload parcial, pendente, duplicado ou fora de ordem não é sucesso', async () => {
  for (const depois of [[1, 2], [1, 2, 2], [2, 1, 3]]) {
    const f = campoTeste([1], depois, recibos.slice(0, 1));
    await assert.rejects(enviarArquivosCampo(f.tab, f.campo.controle, arquivos, f.campo));
    assert.ok(f.estado().cliques >= 1 && f.estado().cliques <= 2);
  }
  const f = campoTeste();
  f.campo.observar = async () => ({ itens: [], pendente: true });
  await assert.rejects(enviarArquivosCampo(f.tab, f.campo.controle, arquivos, f.campo), /pendente/);
  assert.equal(f.estado().cliques, 0);
});

test('falha no segundo campo preserva o comprovante do primeiro', async () => {
  const f = campoTeste();
  let registrado;
  f.campo.registrar = async r => { registrado = r; };
  const segundo = { ...f.campo, observar: async () => ({ itens: [], pendente: true }) };
  await assert.rejects(enviarLoteCampos(f.tab, { galeria: f.campo, model_pictures: segundo }));
  assert.deepEqual(registrado, recibos);
});

test('falha dentro do lote preserva os comprovantes de cada arquivo concluído', async () => {
  const f = campoTeste([], [1, 2]);
  let registrado;
  f.campo.registrar = async r => { registrado = r; };
  await assert.rejects(enviarArquivosCampo(f.tab, f.campo.controle, arquivos, f.campo));
  assert.deepEqual(registrado, recibos.slice(0, 2));
});

test('captura reaberta usa a interface e recusa upload pendente', async () => {
  const f = campoTeste([1, 2, 3]);
  assert.deepEqual(await capturarAnexos({ galeria: f.campo }), {
    galeria: recibos.map(e => ({ identidade: e.identidade })),
  });
  f.campo.observar = async () => ({ itens: [], pendente: true });
  await assert.rejects(capturarAnexos({ galeria: f.campo }), /pendente/);
});

test('campo que deveria estar vazio não passa com anexos existentes', async () => {
  const f = campoTeste([1]);
  await assert.rejects(enviarLoteCampos(f.tab, { video: { ...f.campo, arquivos: [] } }), /vazio/);
});

function perfilTeste({ placas = 1, arquivo = 'kit.3mf', titulo = 'Kit completo' } = {}) {
  const postagem = { rascunho: { url: 'https://makerworld.com/pt/my/models/drafts/123/edit' },
    campos: { perfil_titulo: 'Kit completo' }, perfil: { placas: 1, arquivo: 'kit.3mf' } };
  let reaberto = false;
  const locator = nome => ({ fill: async () => {}, click: async () => {}, press: async () => {},
    waitFor: async () => {}, evaluate: async () => nome.includes('Editor') ? '<p>Perfil salvo</p>' : titulo });
  const tab = {
    url: async () => postagem.rascunho.url, reload: async () => { reaberto = true; },
    paste: async () => {}, getAXState: async () => {},
    playwright: { getByRole: (_, opcoes) => locator(opcoes.name), evaluate: async () => ({ placas, arquivos: [arquivo] }) },
  };
  return { tab, postagem, reaberto: () => reaberto };
}

test('perfil salvo é reaberto e captura HTML observado para conferência Python', async () => {
  const f = perfilTeste();
  const r = await salvarTextosPerfil(f.tab, f.postagem, '<p>Perfil esperado</p>');
  assert.equal(f.reaberto(), true);
  assert.equal(r.campos.perfil_descricao_html, '<p>Perfil salvo</p>');
  assert.equal(r.conferencia_completa, false);
});

test('perfil com zero placas, título errado ou outro 3MF é recusado', async () => {
  for (const dados of [{ placas: 0 }, { titulo: 'Outro kit' }, { arquivo: 'outro.3mf' }]) {
    const f = perfilTeste(dados);
    await assert.rejects(salvarTextosPerfil(f.tab, f.postagem, '<p>Perfil</p>'));
  }
});

test('consolidação recusa mistura de rascunhos e conserva os dados observados', () => {
  const modelo = { id: '123', url: 'https://makerworld.com/pt/my/models/drafts/123/edit', reaberto: true, campos: { descricao_html: '<p>Modelo observado</p>' } };
  const perfil = { ...modelo, campos: { perfil_descricao_html: '<p>Perfil observado</p>' }, perfil: { placas: 1 } };
  const captura = consolidarCapturas(modelo, perfil, 'CONTA_OBSERVADA', { galeria: [] }, {});
  assert.equal(captura.campos.descricao_html, modelo.campos.descricao_html);
  assert.equal(captura.campos.perfil_descricao_html, perfil.campos.perfil_descricao_html);
  assert.equal(captura.conferencia_completa, false);
  assert.throws(() => consolidarCapturas(modelo, { ...perfil, id: '456' }, 'CONTA_OBSERVADA', {}, {}), /mesmo rascunho/);
});
