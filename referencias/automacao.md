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
- `scripts/rascunho_makerworld.mjs` é um **adaptador parcial para cua_repl**, usado no piloto
  para textos/licença e arquivos em campos já mapeados. Não é uma CLI completa: categoria,
  montagem da descrição do perfil, reconhecimento de placas e envio final foram conduzidos
  pela interface. Preservar essa distinção nas próximas postagens.
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
  `perfil_titulo`, `perfil_descricao`. Preservar PT+EN e o conteúdo completo.
- `midia`: listas `modelos`, `capa`, `capa_app`, `galeria`, `video`, `model_pictures`,
  `perfil_fotos`, na ordem pretendida. Capa e capa_app têm uma entrada cada.
- Cada entrada: `arquivo` relativo ao pacote, `bytes`, `sha256` e `tipo`:
  `3mf`, `stl`, `foto_real`, `render`, `animacao` ou `texto`.
- `fontes`: lista no mesmo formato, para detectar mudanças nos textos/manifestos originais.
- `pendencias`: lista de condições concretas ainda abertas; não apagá-las sem evidência.

`foto_real` é uma classificação após inspeção da imagem, não uma conclusão do validador.
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
`campos` (mesmas chaves da entrada) e `anexos` (mesmos grupos, listas de nomes dos arquivos).
Extrair esses valores da página, nunca copiar a entrada para fingir uma captura.

```powershell
python "<pasta-da-skill>/scripts/valida_postagem.py" conferir "<pacote>/POSTAGEM.json" --captura "<captura-observada>.json"
```

O comparador verifica a captura fornecida, não o site sozinho. Nomes iguais não provam
bytes iguais no servidor; quando houver dúvida de conteúdo, baixar o anexo e comparar hash.
A representação do editor rico precisa ser observada no piloto: uma conversão de Markdown
para HTML não deve perder tabelas, ênfase ou texto. Normalizar apenas representação, sem
encurtar nem reescrever o conteúdo para fazê-lo passar na conferência.

O comparador `conferir` atual compara strings; não converte Markdown/HTML ou nomes traduzidos
de categoria/licença. No piloto, conferimos o HTML preparado contra o DOM reaberto com
`HTMLParser`: texto completo, tabelas/células, listas, ênfase e links permaneceram iguais,
desconsiderando apenas wrappers do CKEditor e espaços de representação. Guardar a captura
real e essa conferência separada; não copiar Markdown da entrada para fingir observação.

### Chamadas do adaptador realmente usadas

Carregar o módulo local no runtime autorizado de navegador e passar a aba existente:

```javascript
const adapter = await import('file:///<pasta-da-skill>/scripts/rascunho_makerworld.mjs');
await adapter.salvarTextosRascunho(tab, postagem, descricaoHtml);
await adapter.enviarArquivosCampo(tab, controleObservado, arquivosAbsolutos);
```

O segundo método devolve `envio_solicitado`, não sucesso. Conferir contagens/miniaturas,
salvar e reabrir. Para a etapa do perfil, colar HTML com `tab.paste(null, html,
{format: 'html'})` no editor focado preservou as duas tabelas, mesmo sem botão de tabela
na barra. Esperar o editor carregar após reabrir antes de capturar; a primeira árvore
durante a navegação pode mostrar campos ainda vazios.

As fotos reais usaram `getByTestId('publish-real-pictures')`; as adicionais, `.modelPicture`.
No botão Substituir arquivo, wrapper e botão nativo tinham o mesmo nome: restringir com
`.and(tab.playwright.locator('button'))`. São seletores observados, não garantia permanente.
Consultar os controles atuais quando houver divergência. Se o perfil mostrar zero placas,
seguir a exportação completa em `campos.md` antes de repetir o upload.

Concluir uma publicação autorizada só depois da conferência e das pendências resolvidas.
Confirmar a página pública e registrar URL real e resultado. Se o salvamento ficar incerto,
consultar o rascunho existente antes de repetir, evitando duplicações.
Se a plataforma encaminhar para **Verificando**, registrar **enviado_em_verificacao** e
consultar a lista de modelos publicados para obter a URL quando existir. Não reenviar nem
revogar para tentar acelerar a moderação. Um botão clicado, um rascunho que sumiu ou a
contagem de perfis enviados não comprovam publicação pública.

## Próximas postagens

Reutilizar apenas o fluxo observado e testado, preservando a conferência automática.
Registrar o script/adaptador usado, data do piloto, idioma do formulário e limitações
demonstradas. Atualizar este estado após o piloto; não declarar economia de tempo/custo
medida antes de comparar as execuções.
