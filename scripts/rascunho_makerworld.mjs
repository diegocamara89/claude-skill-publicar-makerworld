// Adaptador parcial para o cua_repl: textos/licença de um rascunho existente
// e envio de arquivos por um controle observado. Não cria modelos nem publica.
export async function enviarArquivosCampo(tab, controle, arquivos) {
  if (!Array.isArray(arquivos) || !arquivos.length)
    throw new Error('O campo exige arquivos revisados.');
  const pendente = tab.playwright.waitForEvent('filechooser', { timeoutMs: 10000 });
  await controle.click();
  const chooser = await pendente;
  if (arquivos.length > 1 && !chooser.isMultiple())
    throw new Error('Este campo não aceita o lote de arquivos.');
  await chooser.setFiles(arquivos);
  await tab.getAXState({ emit: false });
  // A interface precisa comprovar o envio e, depois, a persistência no rascunho.
  return { estado: 'envio_solicitado', quantidade: arquivos.length };
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
    name: 'Editor editing area: main. Press Alt+0 for help.', exact: true,
  }).evaluate(e => e.innerHTML);
  return { url, campos };
}

export async function salvarTextosRascunho(tab, postagem, descricaoHtml) {
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
  const iguais = (a, b) => JSON.stringify(a.map(x => x.toLowerCase())) === JSON.stringify(b.map(x => x.toLowerCase()));
  // A escolha da categoria e os anexos permanecem no fluxo observado da interface.
  if (!iguais(antes.campos.tags, tags)) {
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
  const editor = tab.playwright.getByRole('textbox', {
    name: 'Editor editing area: main. Press Alt+0 for help.', exact: true,
  });
  await editor.click();
  await editor.press('ControlOrMeta+A');
  await tab.paste(null, descricaoHtml, { format: 'html' });
  await tab.getAXState({ emit: false });
  await tab.playwright.getByRole('button', { name: 'Salvar em rascunho', exact: true }).click();
  await tab.getAXState({ emit: false });
  await tab.reload();
  await tab.getAXState({ emit: false });
  const depois = await capturarRascunho(tab);
  if (depois.campos.titulo !== c.titulo || depois.campos.licenca !== licenca ||
      !iguais(depois.campos.tags, tags) || depois.campos.categoria !== antes.campos.categoria)
    throw new Error('Há divergência no rascunho reaberto; confira a captura.');
  return { ...depois, reaberto: true, estado: 'rascunho_salvo',
    escopo: 'textos_licenca', conferencia_completa: false };
}
