# Campos do MakerWorld — especificações

Levantado em 27/09/2026 no formulário de upload e nas regras da plataforma. Se o formulário
mostrar outro limite, o formulário vence: anotar a mudança aqui.

## Arquivos

- **Um 3MF por kit** (o que a pessoa realmente imprime) e, se houver vários kits,
  **um 3MF com todas as placas** (quem quer tudo baixa uma vez). Com um único kit,
  o mesmo arquivo já reúne todas as peças; não gerar um TODOS idêntico.
  Nome: `<Marca>_<modelo>_<tamanho>_<versao>.3mf`.
- Cada placa = kit completo, na orientação de impressão, sem suporte se o desenho permitir.
  Nome da placa descreve o kit (ex. "Furo 40 mm - tampo de vidro até 12 mm").
- **Processo:** perfil de sistema (ex. "0.20mm Standard @BBL A1") com as mudanças listadas
  em `different_settings_to_system`. Mudança fora da lista some na GUI.
- **Filamento:** perfil de sistema genérico (ex. "Generic PETG @BBL A1"), achatado com
  `flatten-profile.mjs` (skill `bambu-a1`). Nunca o perfil calibrado do dono: o de outra pessoa
  não existe na máquina de quem baixa.
- Malha com vértices soldados (`merge_vertices`); sopa de triângulos faz o Studio fechar furos.
- Script-exemplo que monta tudo isso: `scripts/monta_publicacao.py`
  (`--publicacao <destino> <filamento_sistema.json>` gera o TODOS + um por kit).
- **Conferir cada arquivo, um por vez:**
  `bambu-studio.exe --slice 0 --outputdir <dir> <arquivo>.3mf` → `result.json`
  (`sliced_plates`), `plate_N.gcode`: objetos por placa, suporte ausente, tempo, gramas,
  furos abertos (leitor de G-code com G2/G3 e controle positivo — skill `bambu-a1`).

### 3MF aceito, mas perfil com zero placas

No piloto de 03/10/2026, o 3MF editável tinha malhas e configurações, mas
`Metadata/slice_info.config` continha apenas o cabeçalho. O site aceitou o upload e mostrou
**Placas de impressão (0)**. Exportar pelo Bambu Studio após fatiar resolveu: placa,
miniaturas e G-code ficaram no ZIP; o rascunho salvo e reaberto mostrou **1 placa**.

```powershell
& '<bambu-studio.exe>' --slice 0 --export-3mf 'perfil_completo.3mf' --outputdir '<saida>' '<entrada.3mf>'
```

`--export-3mf` recebe **nome relativo**, pois a CLI o combina com `--outputdir`.
No Windows, conferir o `result.json` final (`return_code: 0`) e o arquivo exportado:
retorno do shell sozinho não confirmou a conclusão neste piloto. Preservar o original,
comparar malhas, orientação e configurações do exportado e conferir o novo G-code antes
de substituir. Refatiamento não garante G-code idêntico: neste caso mudou um trecho da
porca, progresso e ventilação, com geometria e configurações preservadas. Não exigir
igualdade de bytes como substituto da conferência funcional.

Fonte da combinação dos caminhos:
https://github.com/bambulab/BambuStudio/blob/master/src/BambuStudio.cpp .

## Título e resumo

- Título: benefício concreto + materiais/versões + tamanhos, respeitando o máximo de
  **50 caracteres**, observado no formulário em 03/10/2026. Recompor o título se necessário;
  não cortar automaticamente.
- Resumo: 1 frase. A plataforma traduz título, resumo, descrição e comentários
  automaticamente; escrever em português é aceitável, com versão EN na descrição.
  Na etapa de informações do piloto não havia campo separado: usar a frase como primeiro
  parágrafo da descrição, registrando essa adaptação.

## Capa e App cover

| Campo | Proporção | Tamanho usado | Observação |
|---|---|---|---|
| Cover | 4:3 | 1600×1200 | aparece na lista e na página |
| App cover | 3:4 | 1200×1600 | campo à parte, para o app; recompor o render em retrato |

Renders são permitidos se forem fiéis ao modelo; foto real é recomendada como capa quando
estiver bonita. Na prática: capa = render com marca; foto real em 1º lugar na galeria.

## Galeria e vídeo

- O formulário observado em 03/10/2026 distingue **Fotos da vida real** de **Fotos de
  modelos**. O primeiro campo pede **pelo menos 3 fotos reais cobrindo 3 vistas**, até 16.
  Não completar esse requisito com renders ou cópias da mesma foto.
- Imagens png/jpg/webp/gif, até 30 MB cada, 4:3 recomendado.
- Vídeo aceito na página do modelo (recurso lançado em jul/2026): MP4 H.264, 1080p,
  `yuv420p`, `+faststart`. Conteúdo focado no modelo, sem propaganda alheia.
- GIF de reserva (≤ 30 MB): 800 px de largura, 12 fps, paleta de 160 cores.

## Model Pictures (campo separado!)

- Texto do campo: "Photos of the printed model, png/jpg/webp/gif, ≤ 30MB/piece, 4:3 ratio
  recommended", até 16 imagens.
- Fundo simples e proporção 4:3 são recomendações de apresentação. Fotos reais adicionais
  instaladas foram aceitas no piloto, sem recorte, preservando o contexto da fixação.
  Usar fotos diferentes das da galeria. A peça não é retocada. Se fizer sentido trocar o
  fundo, seguir `midia.md` § Model Pictures.

## Print Profile Pictures

- Até 37 imagens. **Pelo menos uma foto real** da peça impressa, senão o perfil pode ser
  derrubado. A 1ª imagem vira a miniatura do perfil.
- Ordem: foto real instalada → foto real das peças soltas → renders.
- O formulário copiou a capa renderizada automaticamente para o perfil no piloto. Conferir
  o campo e deixar foto real como primeira imagem; upload novo não remove o render sozinho.

## Print Profile Description

Modelo em `textos.md`. Leva: impressora/bico, filamento, camada, paredes, preenchimento,
chapa, brim, suporte, orientação, tabela tempo/gramas por placa e dicas de montagem.

## Tags

- O formulário em 03/10/2026 mostrou **até 50 tags e até 100 caracteres por entrada**
  (`8/50` no conjunto e `0/100` no input). O limite anterior de 100 no total foi corrigido.
  A busca casa as palavras digitadas; a página
  em português mostra as tags traduzidas, mas quem busca em inglês acha pelas tags em inglês.
- Receita: 5–7 termos em inglês que a pessoa digitaria + 1–2 em português ("passa fio").
  Sem sinônimos inventados, sem marca de terceiros.

## Categoria

Achar o modelo parecido mais baixado no MakerWorld e usar a mesma categoria.
Exemplo: passador de cabo → Casa (Household) > Escritório (Office).

## Licença

O formulário pergunta se outros podem **modificar/remixar** e se podem **usar
comercialmente**, e também oferece um menu com o nome explícito da licença. CC BY-NC e
CC BY-NC-SA foram conferidas no rascunho do suporte em 03/10/2026. Para as demais linhas,
conferir o nome efetivo no formulário; não supor a licença somente pelas respostas.

| Opção de remix | Licença resultante (com comercial "No") | Quando usar |
|---|---|---|
| **Yes** | **CC BY-NC 4.0** | **preferência informada em 03/10/2026**: reutilização/adaptação com crédito, sem comercial |
| Yes, as long as others share in the same way | CC BY-NC-SA 4.0 | acrescenta a obrigação de usar a mesma licença nas adaptações; escolher se solicitada |
| Exclusive to MakerWorld | licença exclusiva da plataforma | só se entrar em programa de exclusividade |
| Exclusive + SDFL-C | SDFL | remix proibido fora da plataforma |
| No | CC BY-NC-ND | ninguém modifica |

Comercial: "No" por padrão (vender a peça impressa exige permissão). Se o modelo é
inspirado em outro, a licença própria só vale se a geometria foi refeita do zero.

Referência: https://creativecommons.org/licenses/by-nc/4.0/ . CC BY-NC permite copiar,
redistribuir e adaptar para fins não comerciais, com crédito, link da licença e indicação
das mudanças. O sufixo SA é uma condição adicional, não um requisito para atribuir crédito.
