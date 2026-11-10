# Textos — modelos e exemplo real

Tom: chamativo, mas **justo**. Cada frase tem de ser verificável no modelo ou no teste.
Proibido: "o melhor do MakerWorld", "indestrutível", número que não saiu do fatiamento.
Permitido: dor concreta que o modelo resolve, comparação com o problema comum, "testado em
N rodadas de impressão" quando for verdade.

## Título

Modelo: `<O que é> com <diferencial> — <versões>, <tamanhos>`
Exemplo:
- Passador de Cabo com Rosca que Prende de Verdade — Vidro e Madeira, 35 a 60 mm

## Resumo (1 linha)

Modelo: `<ação principal> e <resultado>. Serve em <onde>, tem <recurso> e imprime sem suporte.`
Exemplo: Rosqueia por baixo da mesa e não sai mais. Serve em vidro e madeira, tem tampa
giratória e imprime sem suporte.

## Descrição (estrutura fixa, só em português)

Decisão do dono (06/10/2026): textos **só em português**. O MakerWorld traduz título,
resumo e descrição automaticamente; versão EN duplicada é retrabalho e polui a página.
Tags continuam com termos de busca em inglês (são busca, não texto).

```markdown
**<Pergunta com as 2–3 dores que o modelo resolve>?** <Frase: como ele resolve>. <Frase: recurso visível>.

**Por que ele é diferente**
- **<Benefício 1>:** <mecanismo que garante>.
- **<Benefício 2>:** <faixa/compatibilidade com números>.
- **<Benefício 3>:** <detalhe de projeto>.
- **Testado de verdade:** <o que foi ajustado em impressão real>.

**O que vem**
- <tamanhos e versões>
- Cada placa é um kit completo: <peças>. Imprime **sem suporte**.
- <detalhes úteis: sem ferramenta, fita opcional etc.>

**Qual arquivo baixar**
| <medida> | <versão A (faixa)> | <versão B (faixa)> | <capacidade> |
|---|---|---|---|
| ... |
<como medir; exceções>

**Impressão**
- <material>, camada <x>, bico <y>.
- <chapa>, <brim>, sem suporte.
- Cada placa leva <faixa real de tempo>.

**Montagem**
1. ...

**Dicas**
- <o que fazer se ficar justo/folgado>
- <em que material/impressora as folgas foram testadas>

**Créditos:** inspirado em "<nome>", de <autor> (<link>). Esta versão foi redesenhada do zero, <o que mudou>.

Design: ByteLayer (@ByteLayer)
```

Não escrever versão EN (nem da descrição, nem do perfil).

### Exemplo completo (PT)

**Cansado de passador de cabo que solta do furo, gira junto com os cabos ou só serve numa
espessura de mesa?** Este rosqueia por baixo do tampo com uma porca apertada à mão e fica
firme, em **vidro** ou em **madeira**. Por cima, a **tampa giratória** abre e fecha a passagem
em volta dos cabos.

**Por que ele é diferente**
- **Não sai do furo:** rosca e porca no lugar de encaixe por pressão.
- **Uma peça para várias mesas:** a mesma bucha serve de 4 a 12 mm (vidro) ou de 4 a 30 mm (madeira).
- **Não balança:** o disco interno assenta num anel inteiro e é travado por 3 nervuras.
- **Testado de verdade:** folgas ajustadas em várias rodadas de impressão real, até ficar firme sem prender.

**Qual arquivo baixar**

| Furo no tampo | Tampo de vidro (4 a 12 mm) | Tampo de madeira (4 a 30 mm) | Cabo mais grosso que passa com a tampa |
|---|---|---|---|
| 35 mm | 35mm_vidro | 35mm_madeira | ~6,5 mm |
| 40 mm | 40mm_vidro | 40mm_madeira | ~9 mm |
| 50 mm | 50mm_vidro | 50mm_madeira | ~14 mm |
| 60 mm | 60mm_vidro | 60mm_madeira | ~19 mm |

(Texto integral em `Passador de cabo 40mm\PUBLICACAO_MakerWorld\DESCRICAO_MakerWorld.md`.)

## Tags (até 50 entradas de até 100 caracteres)

Receita: termos em inglês que a pessoa digitaria na busca + 1–2 em português. Contar com
`len(tag)` por entrada e a quantidade de entradas antes de entregar; não limitar o conjunto
todo a 100 caracteres. Conferir os limites atuais em `campos.md`.

Exemplo (99 caracteres):
`cable grommet,desk grommet,cable management,cable hole cover,glass desk,wood desk,passa fio,grommet`

Alternativa só PT (se ele preferir):
`passa fio,passa cabo,organizador de cabos,mesa de vidro,mesa de madeira,cable grommet`

## Print Profile Description

```markdown
**Perfil testado:** Bambu Lab A1, bico 0,4 mm, <filamento genérico de sistema>, camada 0,20 mm.

**Configuração**
- Paredes: <n> (gerador arachne) · Preenchimento: <x>% · Chapa: <tipo>
- Brim: <auto/sim> · Suporte: não precisa · Orientação: já vem correta, não gire as peças.

**Tempo e material por placa** (Bambu Studio, <filamento>)
| Placa | Tempo | Filamento |
|---|---|---|
| ... | ... min | ... g |

**Dicas**
- <folga/lixa/ordem de montagem>
- <material alternativo e o que muda>
```

Exemplo real (Generic PETG @BBL A1): 35 vidro 56 min 16,8 g · 35 madeira 76 min 21,7 g ·
40 vidro 60 min 19,6 g · 40 madeira 81 min 25,3 g · 50 vidro 71 min 25,1 g ·
50 madeira 93 min 32,4 g · 60 vidro 88 min 31,1 g · 60 madeira 116 min 40,1 g.

## Guia campo a campo (entregar ao dono no fim)

Lista na ordem do formulário: `Campo → arquivo ou texto`. Ex.:
- Model Files → os 9 `.3mf` da pasta
- Cover → `midia/capa_4x3_1600x1200.png` · App cover → `midia/capa_app_3x4_1200x1600.png`
- Gallery → `Galeria_imagens/` na ordem numérica · Video → `midia/video_...mp4`
- Model Pictures → `Model_Pictures/` · Print Profile Pictures → foto real instalada primeiro
- Description, Tags, Category, License, Print Profile Description → seções do `DESCRICAO_MakerWorld.md`
