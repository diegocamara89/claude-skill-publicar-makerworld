# Campos do MakerWorld — especificações

Levantado em 27/09/2026 no formulário de upload e nas regras da plataforma. Se o formulário
mostrar outro limite, o formulário vence: anotar a mudança aqui.

## Arquivos

- **Um 3MF por kit** (o que a pessoa realmente imprime) e **um 3MF com todas as placas**
  (quem quer tudo baixa uma vez). Nome: `<Marca>_<modelo>_<tamanho>_<versao>.3mf`.
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

## Título e resumo

- Título: benefício concreto + materiais/versões + tamanhos. ~60–90 caracteres.
- Resumo: 1 frase. A plataforma traduz título, resumo, descrição e comentários
  automaticamente; escrever em português é aceitável, com versão EN na descrição.

## Capa e App cover

| Campo | Proporção | Tamanho usado | Observação |
|---|---|---|---|
| Cover | 4:3 | 1600×1200 | aparece na lista e na página |
| App cover | 3:4 | 1200×1600 | campo à parte, para o app; recompor o render em retrato |

Renders são permitidos se forem fiéis ao modelo; foto real é recomendada como capa quando
estiver bonita. Na prática: capa = render com marca; foto real em 1º lugar na galeria.

## Galeria e vídeo

- Imagens png/jpg/webp/gif, até 30 MB cada, 4:3 recomendado.
- Vídeo aceito na página do modelo (recurso lançado em jul/2026): MP4 H.264, 1080p,
  `yuv420p`, `+faststart`. Conteúdo focado no modelo, sem propaganda alheia.
- GIF de reserva (≤ 30 MB): 800 px de largura, 12 fps, paleta de 160 cores.

## Model Pictures (campo separado!)

- Texto do campo: "Photos of the printed model, png/jpg/webp/gif, ≤ 30MB/piece, 4:3 ratio
  recommended", até 16 imagens.
- A plataforma recomenda **fundo simples de uma cor**. São fotos **diferentes** das da galeria:
  a peça real recortada e posta sobre fundo liso claro, com sombra suave.
- A peça não é retocada; só o fundo é trocado. Receita em `midia.md` § Model Pictures.

## Print Profile Pictures

- Até 37 imagens. **Pelo menos uma foto real** da peça impressa, senão o perfil pode ser
  derrubado. A 1ª imagem vira a miniatura do perfil.
- Ordem: foto real instalada → foto real das peças soltas → renders.

## Print Profile Description

Modelo em `textos.md`. Leva: impressora/bico, filamento, camada, paredes, preenchimento,
chapa, brim, suporte, orientação, tabela tempo/gramas por placa e dicas de montagem.

## Tags

- Até 100 caracteres no total (vírgulas contam). A busca casa as palavras digitadas; a página
  em português mostra as tags traduzidas, mas quem busca em inglês acha pelas tags em inglês.
- Receita: 5–7 termos em inglês que a pessoa digitaria + 1–2 em português ("passa fio").
  Sem sinônimos inventados, sem marca de terceiros.

## Categoria

Achar o modelo parecido mais baixado no MakerWorld e usar a mesma categoria.
Exemplo: passador de cabo → Casa (Household) > Escritório (Office).

## Licença

O formulário pergunta se outros podem **modificar/remixar** e se podem **usar
comercialmente**. Só a linha em negrito foi conferida na publicação do passador; as outras
são o mapeamento esperado — confira o nome da licença que o formulário mostra ao escolher.

| Opção de remix | Licença resultante (com comercial "No") | Quando usar |
|---|---|---|
| Yes | CC BY-NC | quer máxima difusão |
| **Yes, as long as others share in the same way** | **CC BY-NC-SA** | **padrão do dono**: remix volta aberto |
| Exclusive to MakerWorld | licença exclusiva da plataforma | só se entrar em programa de exclusividade |
| Exclusive + SDFL-C | SDFL | remix proibido fora da plataforma |
| No | CC BY-NC-ND | ninguém modifica |

Comercial: "No" por padrão (vender a peça impressa exige permissão). Se o modelo é
inspirado em outro, a licença própria só vale se a geometria foi refeita do zero.
