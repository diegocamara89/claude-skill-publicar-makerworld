# Validação e automação da postagem

## Estado verificado em 03/10/2026

- `scripts/valida_postagem.py` funciona localmente, usa somente a biblioteca padrão do
  Python 3.11+ e não acessa a conta nem envia arquivos. Os casos negativos estão em
  `scripts/test_valida_postagem.py`.
- O primeiro piloto autenticado salvou e reabriu o rascunho 9880155 do suporte: três STL,
  título, categoria, oito tags, descrição PT+EN com quatro tabelas, duas capas, vídeo de
  22 s, quatro fotos reais e duas fotos adicionais persistiram. O perfil reaberto manteve
  3MF com uma placa, título, uma foto real e descrição PT+EN com duas tabelas. O dono
  confirmou: “Guia e perfil final testados”. O botão Publicar levou à lista **Verificando**,
  com o produto e o perfil enviados. Depois, o modelo apareceu em Modelos Publicados e a
  página pública foi aberta e conferida, incluindo perfil de uma placa e licença BY-NC:
  https://makerworld.com/pt/models/3391376-suporte-o49-5-mm-grades-horizontais-e-verticais#profileId-3859959 .
- `scripts/rascunho_makerworld.mjs` reutiliza o **cua_repl** autorizado. Agora envia lotes,
  confere a conclusão por controles observados, registra comprovantes para retomada,
  salva/reabre textos de modelo e perfil e verifica o título, o 3MF e as placas do perfil.
  `valida_postagem.py` confere o HTML e a captura consolidada. Não cria modelos nem publica.
  A criação do rascunho, a categoria e as transições entre etapas continuam dependendo do
  mapeamento da interface; não há API pública de postagem implementada.
- Esta revisão passou em **30 testes Python e 12 testes Node**, com dados/dublês locais.
  O comparador passou também nas duas capturas reais salvas do suporte. O módulo carregou
  no cua_repl e leu uma miniatura da página pública do passador, sem alterá-la. O fluxo
  integrado desta revisão ainda precisa do primeiro uso autenticado numa nova postagem:
  não confundir esses testes com um novo upload/salvamento real.
- As mudanças de licença durante essa rodada também foram feitas manualmente pelo dono,
  conforme ele esclareceu. Não atribuí-las a falha do navegador ou da automação. Coordenar
  edição da mesma aba e conferir a licença efetiva no conteúdo salvo e reaberto.
- O menu explícito de licença permite selecionar CC BY-NC, identificada no DOM por
  `li[role="option"][data-value="BY-NC"]`, depois de abrir
  `#mui-component-select-license`. Identificadores observados em 03/10/2026; conferir
  novamente se o formulário mudar. Evitar clicar no link externo dentro da opção.
- Nas fontes consultadas, não encontramos API pública documentada de publicação.
  A [CLI oficial do Bambu Studio](https://github.com/bambulab/BambuStudio/blob/master/src/libslic3r/PrintConfig.cpp#L9941-L10100)
  prepara/fatia/exporta arquivos; isso não é postagem.
- [makerworld-api-reverse](https://github.com/kloshi-io/makerworld-api-reverse/blob/main/src/api.ts)
  consulta/baixa modelos, sem implementar publicação. Uma consulta pública posterior pode
  complementar a conferência, depois de testar quais campos ela retorna.
- [makerworld-autopilot](https://github.com/vTanco/makerworld-autopilot/blob/main/uploader/playwright_uploader.py#L347-L358)
  usa Playwright/Chromium por trás da CLI e pode retornar sucesso sem comprovar salvamento.
  Não usar essa resposta como prova de publicação nem instalar o projeto como solução pronta.

## Entrada única: POSTAGEM.json

Criar na pasta do pacote, sem credenciais ou caminhos absolutos. Usar estas chaves:

- `versao_schema`: `1`; `conta`: conta de destino, por exemplo `ByteLayer`.
- `campos`: textos revisados `titulo`, `resumo`, `descricao`, `tags` (texto separado por
  vírgulas), `categoria` (nome/caminho escolhido), `licenca` (nome confirmado),
  `perfil_titulo`, `perfil_descricao`. Texto só em português; preservar o conteúdo completo.
- `midia`: listas `modelos`, `capa`, `capa_app`, `galeria`, `video`, `model_pictures`,
  `perfil_fotos`, na ordem pretendida. Capa e capa_app têm uma entrada cada. Nas novas
  entradas, separar o 3MF de impressão em `perfil_arquivo` (uma entrada) dos Model Files
  enviados na etapa do modelo. Pacotes antigos com o 3MF em `modelos` continuam válidos.
- Cada entrada: `arquivo` relativo ao pacote, `bytes`, `sha256` e `tipo`:
  `3mf`, `stl`, `foto_real`, `render`, `animacao` ou `texto`.
- `fontes`: lista no mesmo formato, para detectar mudanças nos textos/manifestos originais.
- `pendencias`: lista de condições concretas ainda abertas; não apagá-las sem evidência.
- Para automação com editor rico, `editores.descricao` e `editores.perfil_descricao`:
  entradas de arquivo HTML no mesmo formato, com `tipo: "texto"`, tamanho e SHA-256.
  Preparar e revisar o HTML completo contra os textos originais antes de registrar os
  hashes. Começar a descrição pelo resumo quando o formulário não tiver campo separado.
- `perfil`: `{ "arquivo": "kit.3mf", "placas": 8 }`, com o caminho relativo do 3MF
  revisado em `modelos` ou `perfil_arquivo` e a quantidade esperada de placas reconhecidas.
  Ausência de G-code incorporado, sozinha, não invalida um perfil: o passador publicado
  teve oito placas reconhecidas sem G-code no ZIP. Conferir o site e o fatiamento real.
- `rascunho`: `{ "id": "123", "url": "https://makerworld.com/pt/my/models/drafts/123/edit" }`,
  observado após criar o rascunho. Usar o existente na retomada.
- Opcional `formulario.categoria`: rótulo da categoria observado no idioma do formulário,
  caso difira de `campos.categoria`. Não inventar tradução ou selecionar pela posição.

`foto_real` é uma classificação após inspeção da imagem, não uma conclusão do validador.
Para a rota observada “Tenho arquivos STL/CAD ou outros tipos de arquivos 3MF”, o modelo
pode publicar arquivos para download sem perfil de impressão direta. Declarar `sem_perfil: true`,
com `perfil`, `midia.perfil_fotos` e `midia.perfil_arquivo` vazios; conferir na UI que não há
etapa de perfil. O validador dispensa somente os campos/anexos desse perfil. Não marcar a
declaração de impressão do perfil usando fotos de uma versão anterior aos ajustes.
Ele não reconhece fotos pelo nome ou pela extensão e não prova qualidade de impressão.
O caso do suporte usa também o teste da guia final como pendência específica; não transformar
esse teste em regra obrigatória para todo produto.

```powershell
python "<pasta-da-skill>/scripts/valida_postagem.py" validar "<pacote>/POSTAGEM.json"
python "<pasta-da-skill>/scripts/valida_postagem.py" validar "<pacote>/POSTAGEM.json" --exigir-publicacao
```

Sem `--exigir-publicacao`, um pacote íntegro com fotos/testes pendentes pode servir para
preparar um rascunho. Com a opção, pendências produzem saída 2. Saída 0 comprova somente
as verificações locais descritas no relatório, nunca um envio.

## Primeiro piloto: observar, salvar, reabrir e conferir

Usar a conta autenticada pelo dono e o navegador/API de automação permitido no ambiente.
Não guardar senha, copiar perfil/cookies ou instalar outra ferramenta para contornar login.
Mapear controles a partir do formulário observado, por rótulo/identidade inequívoca;
não usar a segunda categoria do menu ou a posição de um input como regra.

Enviar o pacote em lote somente quando o formulário real estiver mapeado. Não truncar
descrição/tags, trocar 3MF por STL, duplicar fotos nem substituir foto real por render.
Se um campo não aceitar o formato/tamanho, registrar a divergência e adaptar explicitamente
o pacote. Não omitir o campo em silêncio. Para um seletor ambíguo, upload incompleto,
login/CAPTCHA ou alteração do formulário, parar a etapa e pedir apenas a intervenção necessária.

Salvar como rascunho, registrar o identificador real, reabrir pela interface e conferir os
campos persistidos, os anexos e sua ordem. A captura estruturada deve conter:
`conta`, `estado` (`rascunho_salvo` ou `publicado`), `reaberto: true`, `id`, `url`,
`campos` (campos observados, com `descricao_html` e `perfil_descricao_html` para os editores),
`perfil` (placas e lista `arquivos` de nomes de 3MF observados) e `anexos` por grupo.
Extrair esses valores da página, nunca copiar a entrada para fingir uma captura.

```powershell
python "<pasta-da-skill>/scripts/valida_postagem.py" conferir "<pacote>/POSTAGEM.json" --captura "<captura-observada>.json"
```

Para arquivos com nome legível, `anexos[grupo]` pode continuar sendo uma lista de nomes
observados. Para fotos/vídeos renomeados pelo CDN, usar listas de `{ "identidade": "..." }`
extraídas da interface reaberta. Guardar separadamente `envios[grupo]`, os comprovantes
produzidos no envio: `{ "arquivo": "nome-local.jpg", "sha256": "hash-local", "identidade": "..." }`.
O comparador exige a correspondência completa e na ordem; contagem sozinha não basta.
Não fabricar comprovantes para anexos que já estavam no campo. Se faltarem, inspecionar o
conteúdo antes de retomar. As identidades de mídia removem query/fragmento das URLs visíveis;
não registrar cookies, tokens ou URLs assinadas.

O comparador verifica a captura fornecida, não o site sozinho. Comprovantes vinculam o
arquivo local à identidade observada, mas não provam o hash dos bytes no servidor.
Quando houver dúvida, baixar o anexo e comparar conteúdo/hash. Imagens podem ser recodificadas.

O HTML é comparado ao HTML revisado de `editores`, preservando texto, ordem de células e
listas, ênfase e destinos de links. Aceita wrappers/controles do CKEditor, espaços de
representação, `b`/`strong`, `i`/`em` e `tbody` inserido pelo editor. O piloto descartou
`hr`: divisores decorativos são ignorados; CSS, cores e layout exigem inspeção visual.
Sem referência HTML, uma captura em HTML falha em vez de simular equivalência com Markdown.
Licenças BY-NC/BY-NC-SA e tags em lista são normalizadas pela representação observada.

Para conferir uma captura parcial já existente, sem declarar a postagem toda conferida:

```powershell
python "<skill>/scripts/valida_postagem.py" conferir-html "<HTML-revisado>" --captura "<captura-real>.json" --campo descricao_html
python "<skill>/scripts/valida_postagem.py" conferir-html "<HTML-perfil-revisado>" --captura "<captura-perfil-real>.json" --campo perfil_descricao_html
```

### Chamadas do adaptador realmente usadas

Carregar o módulo local no runtime autorizado de navegador e passar a aba existente:

```javascript
const adapter = await import('file:///<pasta-da-skill>/scripts/rascunho_makerworld.mjs');
const modelo = await adapter.salvarTextosRascunho(tab, postagem, descricaoHtml, opcoesModelo);
// Abrir a etapa do perfil pelos controles observados, sem criar outro rascunho.
const perfil = await adapter.salvarTextosPerfil(tab, postagem, perfilHtml, opcoesPerfil);
```

`opcoesModelo.selecionarCategoria(rotulo)` usa o controle mapeado, se a categoria atual
divergir. `aguardarSalvamento()` espera o sinal de conclusão observado, com timeout.
`reabrirEtapa()` volta à etapa correta após reabrir; no perfil, mapear essa transição antes
de chamar o script. Os métodos devolvem HTML observado e `conferencia_completa: false`:
é preciso executar a conferência Python. Para o perfil, a colagem HTML preservou as duas
tabelas no piloto mesmo sem botão de tabela na barra. Esperar o editor carregado antes de
capturar; a primeira árvore após navegação pode mostrar campos ainda vazios.

### Lotes, conclusão e retomada

Mapear uma vez os controles, miniaturas e indicador de progresso de cada campo na página
real. Reutilizar esse mapa enquanto a interface permanecer igual. Não presumir seletores
novos, usar todas as imagens da página nem incluir o ícone de adicionar foto na contagem.
Cada campo recebe `controle`, `arquivos` absolutos, `entradas` revisadas, `observar()` e
`aguardar(total)`. Exemplo para um campo de imagens com seus locators já observados:

```javascript
const campo = {
  controle: botaoObservado, arquivos: arquivosAbsolutos, entradas: postagem.midia.galeria,
  comprovantes: comprovantesAnteriores.galeria ?? [],
  observar: () => adapter.observarImagens(miniaturasObservadas),
  aguardar: async total => {
    await miniaturasObservadas.nth(total - 1).waitFor({ state: 'visible', timeoutMs: 45000 });
    await progressoObservado.waitFor({ state: 'hidden', timeoutMs: 45000 });
  },
  registrar: async recibos => { /* persistir recibos localmente após este campo */ },
};
const envios = await adapter.enviarLoteCampos(tab, { galeria: campo });
```

`observar()` retorna `{ itens: [{identidade: "..."}], pendente: false, erro: null }`
com valores extraídos da interface; para arquivos/vídeo, implementar a leitura do controle
observado. `aguardar` espera condição real, sem sleep fixo. `enviarArquivosCampo` agora
exige essas opções e retorna `envio_conferido` apenas após verificar conclusão, quantidade
e preservação dos anexos existentes. Chamadas antigas sem observador falham antes do clique.
Não há repetição automática após timeout/erro: inspecionar e retomar com comprovantes.

Salvar os comprovantes de **cada arquivo**, pelo callback `registrar`, antes de avançar ao
próximo. Um campo vazio pode receber o lote; um prefixo conferido envia somente o restante;
um lote completo é reutilizado. Campo ocupado sem vínculo compatível bloqueia o envio.
O lote é executado automaticamente em sequência, com um arquivo por seletor: a única nova
identidade pode ser ligada ao arquivo solicitado, mesmo quando o CDN muda o nome. Isso
usa mais operações de upload que uma seleção simultânea, mas dispensa presumir a ordem de
conclusão e também funciona em campos que não aceitam múltiplos arquivos.
Não reenviar o 3MF já carregado automaticamente no perfil: primeiro conferir o nome e as placas.

Após salvar e reabrir as duas etapas, capturar novamente todos os anexos com
`adapter.capturarAnexos(camposMapeados)`. Incluir campos esperados vazios na observação.
Consolidar somente dados observados do mesmo rascunho:

```javascript
const captura = adapter.consolidarCapturas(modelo, perfil, contaObservada, anexosObservados, enviosPersistidos);
// Salvar captura em JSON local e rodar valida_postagem.py conferir antes de publicar.
```

A conta deve ser lida na interface autenticada, nunca copiada de `postagem.conta`.
Se houver alterações depois da captura, recapturar os campos afetados antes de conferir.

As fotos reais usaram `getByTestId('publish-real-pictures')`; as adicionais, `.modelPicture`.
No botão Substituir arquivo, wrapper e botão nativo tinham o mesmo nome: restringir com
`.and(tab.playwright.locator('button'))`. São seletores observados, não garantia permanente.
Consultar os controles atuais quando houver divergência. Se o perfil mostrar zero placas,
seguir a exportação completa em `campos.md` antes de repetir o upload. O script exige a
quantidade esperada e o nome do 3MF; aceite do arquivo não basta.

Concluir uma publicação autorizada só depois da conferência e das pendências resolvidas.
Confirmar a página pública e registrar URL real e resultado. Se o salvamento ficar incerto,
consultar o rascunho existente antes de repetir, evitando duplicações.
Se a plataforma encaminhar para **Verificando**, registrar **enviado_em_verificacao** e
consultar a lista de modelos publicados para obter a URL quando existir. Não reenviar nem
revogar para tentar acelerar a moderação. Um botão clicado, um rascunho que sumiu ou a
contagem de perfis enviados não comprovam publicação pública.

## Rota principal: Claude in Chrome

Decisão do dono (11/10/2026): **o Claude posta ele mesmo por esta rota e não delega ao Codex**.
O Codex fica sem navegador conectado (`cua_repl` com `browsers: []`) e todas as tentativas
falharam. O `rascunho_makerworld.mjs` acima fica como referência de seletores e de conferência,
não como caminho de envio. Usada com sucesso em 06/10/2026 (travas de gaiola) e em 11/10/2026
(suporte Arzopa, rascunho 9987571 enviado à verificação).

- Imagens, 3MF e STL: `file_upload` da extensão no `input[type=file]` funciona (capas abrem
  diálogo de recorte: clicar Submit).
- **Vídeo não entra só com `file_upload`.** Causa medida: a aba do grupo da extensão fica
  `document.visibilityState === "hidden"`, e o Chrome não carrega metadados de vídeo em aba
  oculta; a validação do site espera a duração e descarta o arquivo em silêncio (nenhuma
  chamada de rede). Receita que funcionou (v2 3404362 e v1 3404388): (1) `file_upload` no input
  de vídeo para obter o `File`; (2) via JS, guardar `input.files[0]`, sobrescrever
  `HTMLInputElement.prototype.click` para, no input de vídeo, colocar esse arquivo em `files` e
  disparar `change`; (3) sobrescrever o setter de `HTMLMediaElement.prototype.src` para, em
  `blob:`, expor a duração e as dimensões REAIS do arquivo (medidas com ffprobe) e disparar
  `loadedmetadata`; (4) clicar no cartão "Add video". Conferir `POST .../my/upload` + `PUT` no
  S3 e a prévia do vídeo antes de salvar.
- Campo de tags: Enter não limpa o texto (as tags se acumulam numa só). Digitar, esperar a
  lista e clicar a primeira sugestão; sem sugestão, Enter cria a tag personalizada.
- Nome do perfil vem preenchido em inglês: definir pelo setter nativo do input + `input`/`change`.
- Descrições: `document.querySelector('.ck-editor__editable').ckeditorInstance.setData(html)`
  preserva tabelas e links.
- Remix (11/10/2026, suporte Arzopa): Upload → "3D remix model" → "Yes (3mf)"; o campo **Model Origin**
  aceita a URL colada e pede clicar a sugestão; com origem BY-NC-SA, o site só habilita a licença SA.
  Categoria: digitar "Office" e clicar Household > Office (id 404).
- **Tags:** colar `scripts/tags_lote.js` e chamar `await enviaTags("<tags do pacote>", 0)`, depois 10, 20…
  (blocos de 10: o CDP corta a chamada em 45 s; ~2 s por tag). Ele tira os acentos, porque o site corta
  letras acentuadas ("portátil" → "porttil"), e devolve o contador `Tags (N / 50)` lido da tela.
  - **Uma chamada por vez, nunca em paralelo** (12/10/2026, plataforma de carretéis): com a aba oculta há
    mais de ~5 min, o Chrome passa a segurar os `setTimeout` da página; a chamada estoura os 45 s, mas o
    laço continua rodando na página, e duas chamadas se misturaram no mesmo campo (faltaram 4 tags e
    entrou uma "PET" a mais). Se uma chamada estourar, esperar o campo parar de mudar antes de qualquer
    outra; para completar poucas tags, digitar pelo `computer` (type → clicar a sugestão; sem sugestão, Enter).
  - Depois, ler `.tagItem-content` e comparar o conjunto com o pacote (sem caixa: o site grava a caixa
    da sugestão, ex. "Recycle", "BAMBU LAB"). Tag a mais sai pelo X do chip (`img.tagItem-deleteIcon`).
  - O placeholder do campo veio vazio (o texto virou rótulo): `campoTags()` agora acha o input pelo rótulo
    `Tags (N / 50)`.
- `file_upload` da extensão tem limite de **10 MB por chamada**: rodar `scripts/fotos_leves.py` antes
  (8 MB → 0,4 MB, 2000 px, sem EXIF/GPS) e enviar em lote. O MakerWorld reprocessa e tira o GPS
  (conferido em 11/10/2026), mas o arquivo leve já sai sem ele.
- **3MF acima de 10 MB** (12/10/2026: 13–14 MB, a maior parte era G-code embutido): regravar o ZIP sem
  `Metadata/plate_N.gcode` e `.gcode.md5`, mantendo `slice_info.config` com os `<plate>` (deflate nível 9).
  O site reconheceu as 4 placas. Antes de subir, refatiar o 3MF enxuto no CLI e conferir placas, gramas e
  zero suporte iguais aos do original; guardar o original com G-code numa subpasta.
- **Fotos por campo** (12/10/2026): "Real life photos" só recebe foto real; "Model Pictures", outra foto
  real que não está na galeria; imagens explicativas e renders vão em Print Profile Pictures, depois da
  foto real (a capa copiada automaticamente para o perfil sai pelo X + Delete).
- **Comprovante das capas:** o CDN troca o nome da capa. Logo após cada upload de capa, ler a rede
  (`read_network_requests`, filtro `s3`): o nome do `PUT` (ex. `85451cae1da5cd02.png`) é a identidade
  que aparece no rascunho. Registrar `{arquivo, sha256, identidade}` em `envios.capa`/`envios.capa_app`.
  Sem esse registro, `captura_rascunho.js` traz `dimensoes_capas` (1600×1200 = 4:3; 3:4 = app) como prova.
- Perfil: o nome em inglês só muda pelo setter nativo; a capa renderizada é copiada para as fotos do
  perfil (remover no X + Delete). A caixa "I've read Print Profile Guidelines" pode não marcar pelo ref:
  clicar na coordenada e conferir por zoom antes de Publicar.
- **Conferência antes de Publicar (obrigatória):**
  1. Salvar, abrir `.../my/models/drafts/<id>/edit` (a categoria vem do combobox da tela).
  2. Colar `scripts/captura_rascunho.js` + `await guardaCaptura(await capturaRascunho({placas: 1}))`:
     devolve o tamanho e o hash curto de cada pedaço de 900 caracteres. Só lê a API do próprio rascunho.
  3. Trazer cada pedaço com `pedacoCaptura(i)` (a extensão corta respostas longas e bloqueia texto com
     cara de query string; os `= & ? ; %` saem como \uXXXX) e gravar todos, em ordem, num .txt.
  4. `python scripts/monta_captura.py pedacos.txt captura.json <hashes...> --envios envios.json`: para se
     algum pedaço divergir. A ferramenta Write desfaz os \uXXXX; o script aceita as duas formas.
  5. `valida_postagem.py conferir POSTAGEM.json --captura captura.json` tem de dar `conferencia_ok: true`.
     No POSTAGEM, `rascunho.id` e `formulario.categoria` = rótulo da tela (ex. "Office").
  Teste real (11/10/2026, rascunho 9987571): pegou as 2 tags que o site gravou sem acento e fora de
  ordem; depois de alinhar o pacote ao que foi gravado, `conferencia_ok: true`.
- Editar modelo publicado: menu ⋮ → Edit → Edit; ao publicar, responder "No" para geometria
  alterada quando só mídia mudou. A edição volta para "Verifying".

## Próximas postagens

Reutilizar apenas o fluxo observado e testado, preservando a conferência automática.
Registrar o script/adaptador usado, data do piloto, idioma do formulário e limitações
demonstradas. Atualizar este estado após o piloto; não declarar economia de tempo/custo
medida antes de comparar as execuções.
