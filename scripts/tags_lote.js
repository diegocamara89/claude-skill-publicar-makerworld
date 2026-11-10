// Tags em lote no formulário do MakerWorld (rota Claude in Chrome).
// Uso pelo javascript_tool: colar este arquivo e chamar, um bloco por chamada (o CDP corta em 45 s):
//   await enviaTags("arzopa, monitor portátil, ...", 0)    // tags 0..9
//   await enviaTags("arzopa, monitor portátil, ...", 10)   // tags 10..19, e assim por diante
// Devolve o contador "Tags (N / 50)" lido da tela e as tags do bloco com o modo usado.
// O site corta letras acentuadas ("portátil" -> "porttil"): aqui elas saem sem acento antes do envio.
function semAcento(t) {
  return t.normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/\s+/g, ' ').trim();
}
function campoTags() {
  const porTexto = [...document.querySelectorAll('input')]
    .find(i => (i.placeholder || '').startsWith('Press "Enter"') ||
               (i.getAttribute('role') === 'combobox' && /Tags \(/.test(i.closest('div')?.parentElement?.parentElement?.innerText || '')));
  if (porTexto) return porTexto;
  // 12/10/2026: placeholder vazio; o input é o primeiro campo de texto depois do rótulo "Tags (N / 50)"
  const rotulo = [...document.querySelectorAll('*')]
    .find(e => e.children.length === 0 && /^Tags \(\d+ \/ 50\)/.test((e.textContent || '').trim()));
  return rotulo ? [...document.querySelectorAll('input[type=text]')]
    .find(i => rotulo.compareDocumentPosition(i) & Node.DOCUMENT_POSITION_FOLLOWING) : undefined;
}
async function enviaTags(lista, inicio = 0, bloco = 10) {
  const tags = [...new Set(lista.split(',').map(semAcento).filter(Boolean))];
  const inp = campoTags();
  if (!inp) throw new Error('Campo de tags não encontrado: abra a etapa Model Information');
  const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
  const espera = ms => new Promise(r => setTimeout(r, ms));
  const feitos = [];
  for (const t of tags.slice(inicio, inicio + bloco)) {
    inp.focus(); setter.call(inp, t); inp.dispatchEvent(new Event('input', { bubbles: true }));
    await espera(1300);                                   // a lista de sugestões vem da rede
    const exata = [...document.querySelectorAll('li[role="option"]')]
      .find(o => o.textContent.replace(/\s*\(\d+\)\s*$/, '').trim().toLowerCase() === t.toLowerCase());
    if (exata) { exata.dispatchEvent(new MouseEvent('mousedown', { bubbles: true })); exata.click(); feitos.push(t + ' (sugestão)'); }
    else { inp.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true })); feitos.push(t + ' (nova)'); }
    await espera(500);
  }
  return { total_lista: tags.length, proximo: Math.min(inicio + bloco, tags.length),
           contador: document.body.innerText.match(/Tags \(\d+ \/ 50\)/)?.[0], bloco: feitos, sobra_no_campo: inp.value };
}
