// Adaptador para cua_repl, sem outro browser/login. Não cria modelos nem publica.
// O mapeamento dos anexos vem da interface observada; a conferência final usa valida_postagem.py.
const EDITOR = 'Editor editing area: main. Press Alt+0 for help.';
const TITULO_PERFIL = 'Descreva a principal diferença em comparação com os perfis de impressão existentes';
const iguais = (a, b) => JSON.stringify(a) === JSON.stringify(b);
const nomeArquivo = caminho => caminho.replaceAll('\\', '/').split('/').pop();

function conferirObservacao(observacao) {
  if (!observacao || !Array.isArray(observacao.itens) || typeof observacao.pendente !== 'boolean')
    throw new Error('O observador deve retornar itens e pendente a partir da interface.');
  if (observacao.erro) throw new Error(`O campo recusou o envio: ${observacao.erro}`);
  const ids = observacao.itens.map(x => x.identidade);
  if (ids.some(x => typeof x !== 'string' || !x) || new Set(ids).size !== ids.length)
    throw new Error('Anexos sem identidade inequívoca ou duplicados no campo.');
  return ids;
}

// Recebe somente miniaturas mapeadas, excluindo ícones, capas de outros campos e placeholders.
export async function observarImagens(miniaturas) {
  return miniaturas.evaluateAll(imagens => ({
    itens: imagens.map(e => {
      const src = e.getAttribute('src');
      return { identidade: src?.startsWith('https://') ? src.split('?')[0].split('#')[0] : '' };
    }),
    pendente: imagens.some(e => !e.complete || !e.naturalWidth || !e.getAttribute('src')?.startsWith('https://')),
  }));
}

export async function enviarArquivosCampo(tab, controle, arquivos, opcoes = {}) {
  if (!Array.isArray(arquivos) || !arquivos.length)
    throw new Error('O campo exige arquivos revisados.');
  if (typeof opcoes.observar !== 'function' || typeof opcoes.aguardar !== 'function' || !Array.isArray(opcoes.entradas))
    throw new Error('Mapeie observar/aguardar e forneça entradas revisadas antes do upload.');
  const { entradas, comprovantes = [], observar, aguardar } = opcoes;
  if (entradas.length !== arquivos.length || entradas.some((e, i) =>
    nomeArquivo(e.arquivo) !== nomeArquivo(arquivos[i]) || !/^[a-f0-9]{64}$/.test(e.sha256)))
    throw new Error('Arquivos e entradas revisadas divergem. Rode o validador local primeiro.');
  const antes = await observar();
  const idsAntes = conferirObservacao(antes);
  if (antes.pendente) throw new Error('Há um upload pendente; não reenviar o lote.');
  if (!iguais(idsAntes, comprovantes.map(x => x.identidade)) || comprovantes.length > arquivos.length ||
      comprovantes.some((e, i) => e.arquivo !== nomeArquivo(arquivos[i]) || e.sha256 !== entradas[i].sha256))
    throw new Error('Campo ocupado sem comprovantes compatíveis; revisar antes de acrescentar arquivos.');
  const restantes = arquivos.slice(comprovantes.length);
  if (!restantes.length)
    return { estado: 'envio_conferido', quantidade: idsAntes.length, comprovantes, retomado: true };
  const recibos = [...comprovantes];
  let ids = idsAntes;
  // Um arquivo por vez: com nomes CDN, só assim a nova identidade tem vínculo inequívoco.
  for (let i = comprovantes.length; i < arquivos.length; i++) {
    const pendente = tab.playwright.waitForEvent('filechooser', { timeoutMs: 10000 });
    await controle.click();
    const chooser = await pendente;
    await chooser.setFiles([arquivos[i]]);
    await tab.getAXState({ emit: false });
    // Aguardar por locators de conclusão/progresso observado, com timeout; nunca sleep fixo.
    await aguardar(i + 1);
    const depois = await observar();
    const idsDepois = conferirObservacao(depois);
    if (depois.pendente || idsDepois.length !== i + 1 || !iguais(idsDepois.slice(0, ids.length), ids))
      throw new Error('Upload incompleto ou anexos existentes alterados. Inspecione antes de tentar novamente.');
    recibos.push({ arquivo: nomeArquivo(entradas[i].arquivo), sha256: entradas[i].sha256,
      identidade: idsDepois[i] });
    ids = idsDepois;
    if (opcoes.registrar) await opcoes.registrar([...recibos]);
  }
  return { estado: 'envio_conferido', quantidade: ids.length, comprovantes: recibos };
}

export async function enviarLoteCampos(tab, campos) {
  const envios = {};
  for (const [nome, campo] of Object.entries(campos)) {
    if (!campo.arquivos.length) {
      const observado = await campo.observar();
      if (conferirObservacao(observado).length || observado.pendente)
        throw new Error(`O campo ${nome} deveria estar vazio.`);
      envios[nome] = [];
    } else {
      envios[nome] = (await enviarArquivosCampo(tab, campo.controle, campo.arquivos, campo)).comprovantes;
    }
    // Persistir cada campo permite retomar se o próximo falhar, sem perder comprovantes.
    if (campo.registrar) await campo.registrar(envios[nome]);
  }
  return envios;
}

export async function capturarAnexos(campos) {
  const anexos = {};
  for (const [nome, campo] of Object.entries(campos)) {
    const observado = await campo.observar();
    conferirObservacao(observado);
    if (observado.pendente) throw new Error(`O campo ${nome} ainda tem envio pendente.`);
    anexos[nome] = observado.itens;
  }
  return anexos;
}

export function consolidarCapturas(modelo, perfil, contaObservada, anexos, envios) {
  if (!modelo.id || modelo.id !== perfil.id || modelo.url !== perfil.url ||
      modelo.reaberto !== true || perfil.reaberto !== true || !contaObservada)
    throw new Error('As capturas precisam vir do mesmo rascunho reaberto e da conta observada.');
  return { url: modelo.url, id: modelo.id, conta: contaObservada,
    estado: 'rascunho_salvo', reaberto: true,
    campos: { ...modelo.campos, ...perfil.campos }, perfil: perfil.perfil,
    anexos, envios, conferencia_completa: false };
}

export async function capturarRascunho(tab) {
  const url = await tab.url();
  const campos = await tab.playwright.evaluate(() => ({
    titulo: document.querySelector('input[name="title"]')?.value,
    licenca: document.querySelector('input[name="license"]')?.value,
    tags: Array.from(document.querySelectorAll('.tagItem-content')).map(e => e.textContent),
  }));
  campos.categoria = await tab.playwright.getByRole('combobox', {
    name: 'Pesquisa rápida inserindo palavras-chave da categoria', exact: true,
  }).evaluate(e => e.value);
  campos.descricao_html = await tab.playwright.getByRole('textbox', {
    name: EDITOR, exact: true,
  }).evaluate(e => e.innerHTML);
  campos.resumo = await tab.playwright.getByRole('textbox', { name: EDITOR, exact: true })
    .evaluate(e => e.querySelector('p')?.textContent);
  return { url, id: url.match(/\/drafts\/(\d+)/)?.[1], campos };
}

async function colarEditor(tab, html) {
  const editor = tab.playwright.getByRole('textbox', { name: EDITOR, exact: true });
  await editor.waitFor({ state: 'visible', timeoutMs: 45000 });
  await editor.click();
  await editor.press('ControlOrMeta+A');
  await tab.paste(null, html, { format: 'html' });
  await tab.getAXState({ emit: false });
}

async function salvarEReabrir(tab, url, opcoes) {
  await tab.playwright.getByRole('button', { name: 'Salvar em rascunho', exact: true }).click();
  await tab.getAXState({ emit: false });
  if (opcoes.aguardarSalvamento) await opcoes.aguardarSalvamento();
  if (await tab.url() === url) await tab.reload();
  else await tab.goto(url);
  await tab.getAXState({ emit: false });
  if (opcoes.reabrirEtapa) {
    await opcoes.reabrirEtapa();
    await tab.getAXState({ emit: false });
  }
  await tab.playwright.getByRole('textbox', { name: EDITOR, exact: true })
    .waitFor({ state: 'visible', timeoutMs: 45000 });
}

export async function salvarTextosRascunho(tab, postagem, descricaoHtml, opcoes = {}) {
  if (await tab.url() !== postagem.rascunho?.url)
    throw new Error('A aba não corresponde ao rascunho registrado.');
  const c = postagem.campos;
  const licencas = { 'CC BY-NC 4.0': 'BY-NC', 'CC BY-NC-SA 4.0': 'BY-NC-SA' };
  const licenca = licencas[c.licenca];
  const tags = c.tags.split(',').map(x => x.trim());
  if (!c.titulo || c.titulo.length > 50 || !licenca || !descricaoHtml ||
      tags.length > 50 || tags.some(x => !x || x.length > 100))
    throw new Error('Revise título, licença, descrição e tags antes de salvar.');
  const antes = await capturarRascunho(tab);
  const mesmaLista = (a, b) => iguais(a.map(x => x.toLowerCase()), b.map(x => x.toLowerCase()));
  const categoria = postagem.formulario?.categoria ?? c.categoria;
  if (antes.campos.categoria !== categoria) {
    if (!opcoes.selecionarCategoria) throw new Error('Mapeie a categoria pelo rótulo observado.');
    await opcoes.selecionarCategoria(categoria);
    await tab.getAXState({ emit: false });
  }
  if (!mesmaLista(antes.campos.tags, tags)) {
    if (antes.campos.tags.length)
      throw new Error('Tags existentes divergem da entrada; revise antes de substituí-las.');
    const input = tab.playwright.getByRole('combobox', { name: /^Pressione/ });
    for (const tag of tags) { await input.fill(tag); await input.press('Enter'); }
  }
  await tab.playwright.locator('input[name="title"]').fill(c.titulo);
  if (antes.campos.licenca !== licenca) {
    await tab.playwright.locator('#mui-component-select-license').click();
    await tab.playwright.locator(`li[role="option"][data-value="${licenca}"]`).click();
  }
  await colarEditor(tab, descricaoHtml);
  await salvarEReabrir(tab, postagem.rascunho.url, opcoes);
  const depois = await capturarRascunho(tab);
  if (depois.campos.titulo !== c.titulo || depois.campos.licenca !== licenca ||
      !mesmaLista(depois.campos.tags, tags) || depois.campos.categoria !== categoria || depois.campos.resumo !== c.resumo)
    throw new Error('Há divergência no rascunho reaberto; confira a captura.');
  return { ...depois, reaberto: true, estado: 'rascunho_salvo',
    escopo: 'modelo', conferencia_completa: false };
}

export async function capturarPerfil(tab) {
  const titulo = await tab.playwright.getByRole('textbox', { name: TITULO_PERFIL, exact: true })
    .evaluate(e => e.value);
  const html = await tab.playwright.getByRole('textbox', { name: EDITOR, exact: true })
    .evaluate(e => e.innerHTML);
  const perfil = await tab.playwright.evaluate(() => {
    const texto = document.body.innerText;
    const placas = texto.match(/Placas de impressão\s*\((\d+)\)/);
    const arquivos = texto.split('\n').map(x => x.trim()).filter(x => /^[^<>]+\.3mf$/i.test(x));
    return { placas: placas ? Number(placas[1]) : null, arquivos };
  });
  const url = await tab.url();
  return { url, id: url.match(/\/drafts\/(\d+)/)?.[1],
    campos: { perfil_titulo: titulo, perfil_descricao_html: html }, perfil };
}

export async function salvarTextosPerfil(tab, postagem, perfilHtml, opcoes = {}) {
  if (await tab.url() !== postagem.rascunho?.url || !perfilHtml ||
      !postagem.campos.perfil_titulo || postagem.campos.perfil_titulo.length > 60 ||
      typeof postagem.perfil?.arquivo !== 'string' || !postagem.perfil.arquivo ||
      !Number.isInteger(postagem.perfil?.placas) || postagem.perfil.placas < 1)
    throw new Error('Revise rascunho, HTML, título e placas esperadas do perfil.');
  await tab.playwright.getByRole('textbox', { name: TITULO_PERFIL, exact: true }).fill(postagem.campos.perfil_titulo);
  await colarEditor(tab, perfilHtml);
  await salvarEReabrir(tab, postagem.rascunho.url, opcoes);
  const depois = await capturarPerfil(tab);
  if (depois.campos.perfil_titulo !== postagem.campos.perfil_titulo || depois.perfil.placas !== postagem.perfil.placas)
    throw new Error('Título ou placas divergem no perfil reaberto.');
  const arquivo = postagem.perfil.arquivo;
  if (!arquivo || !iguais(depois.perfil.arquivos, [nomeArquivo(arquivo)]))
    throw new Error('O 3MF observado no perfil difere do arquivo revisado.');
  return { ...depois, reaberto: true, estado: 'rascunho_salvo', escopo: 'perfil', conferencia_completa: false };
}
