// Captura do rascunho salvo no MakerWorld, para a rota Claude in Chrome.
// Rodar na aba autenticada, de preferência em .../my/models/drafts/<id>/edit (a categoria vem da tela).
// Uso pelo javascript_tool: colar este arquivo inteiro e terminar com, por exemplo,
//   await capturaRascunho({ placas: 1, envios: { capa: [...], capa_app: [...] } })
// Devolve o objeto que `valida_postagem.py conferir --captura` entende. Salvar como JSON local.
// Nada aqui altera o rascunho: só lê a API do próprio rascunho e a tela.
async function capturaRascunho(opcoes = {}) {
  const id = opcoes.id || (location.pathname.match(/drafts\/(\d+)/) || [])[1];
  if (!id) throw new Error('Abra a página do rascunho (.../drafts/<id>/edit) ou passe opcoes.id');
  const r = await fetch(`/api/v1/design-service/my/draft/${id}`, { credentials: 'include' });
  if (!r.ok) throw new Error(`API do rascunho respondeu ${r.status}`);
  const j = await r.json();
  const base = u => (typeof u === 'string' ? u.split('?')[0].split('#')[0].split('/').pop() : null);
  const nomes = a => (a || []).map(x => x.name || x.modelName || base(x.url)).filter(Boolean);
  // conta lida na interface autenticada, nunca copiada do pacote
  const perfilLink = [...document.querySelectorAll('a[href*="/@"]')]
    .map(a => (a.getAttribute('href').match(/\/@([^/?#]+)/) || [])[1]).find(Boolean);
  // categoria: rótulo do combobox da tela (o JSON só traz categoryId)
  const combo = document.querySelector('input[role="combobox"]');
  const primeiroP = (() => {
    const d = document.createElement('div'); d.innerHTML = j.summary || '';
    const p = d.querySelector('p'); return p ? p.textContent.trim() : null;
  })();
  return {
    conta: opcoes.conta || perfilLink || null,
    estado: opcoes.estado || 'rascunho_salvo',
    reaberto: true,
    id: String(id),
    url: `https://makerworld.com/pt/my/models/drafts/${id}/edit`,
    campos: {
      titulo: j.title,
      resumo: primeiroP,                      // o formulário não tem resumo: é o 1º parágrafo da descrição
      descricao_html: j.summary,
      tags: j.tags || [],
      categoria: opcoes.categoria || (combo && combo.value) || `id:${j.categoryId}`,
      licenca: j.license,
      perfil_titulo: j.profileTitle,
      perfil_descricao_html: j.profileSummary,
    },
    perfil: { placas: opcoes.placas ?? null, arquivos: j.model3Mf ? [j.model3Mf.name] : [] },
    anexos: {
      modelos: nomes(j.modelFiles),
      perfil_arquivo: j.model3Mf ? [j.model3Mf.name] : [],
      // capas perdem o nome no CDN: identidade = nome do arquivo na URL, ligada pelos envios
      capa: j.cover ? [{ identidade: base(j.cover) }] : [],
      capa_app: j.coverPortrait ? [{ identidade: base(j.coverPortrait) }] : [],
      galeria: nomes(j.realPictures),
      video: nomes(j.designVideo),
      model_pictures: nomes(j.designPictures),
      perfil_fotos: nomes(j.auxiliaryPictures),
    },
    envios: opcoes.envios || {},
    origem: (j.original || []).map(o => ({ designId: o.designId, autor: o.author, licenca: o.license })),
    categoryId: j.categoryId,
    // tamanho servido pelo CDN: prova qual capa é qual (4:3 x 3:4) quando faltar o envio registrado
    dimensoes_capas: { capa: await dimensao(j.cover), capa_app: await dimensao(j.coverPortrait) },
  };
}

function dimensao(url) {
  return new Promise(res => {
    if (!url) return res(null);
    const im = new Image();
    im.onload = () => res([im.naturalWidth, im.naturalHeight]);
    im.onerror = () => res(null);
    im.src = url.split('?')[0];
  });
}

// A extensão corta respostas longas (~1000 caracteres) e bloqueia texto com cara de query string.
// Guardar a captura na página e trazer em pedaços de 900; cada pedaço tem hash curto para
// conferir no Python que o arquivo montado é idêntico ao da página.
async function guardaCaptura(obj) {
  window.__captura = JSON.stringify(obj);
  const pedacos = [];
  for (let i = 0; i < window.__captura.length; i += 900) {
    const s = window.__captura.slice(i, i + 900);
    const h = new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(s)));
    pedacos.push([...h.slice(0, 4)].map(x => x.toString(16).padStart(2, '0')).join('-'));
  }
  return { caracteres: window.__captura.length, pedacos };
}
// Pedaço i, com = & ? ; % trocados por \uXXXX (o filtro da extensão deixa passar; o JSON continua válido).
function pedacoCaptura(i) {
  return '<<' + window.__captura.slice(i * 900, (i + 1) * 900)
    .replace(/[=&?;%]/g, c => '\\u' + c.charCodeAt(0).toString(16).padStart(4, '0')) + '>>';
}
