---
name: publicar-makerworld
description: Prepara TUDO para publicar um modelo 3D no MakerWorld (Bambu Lab) de uma vez, sem o dono ter que pedir item por item — arquivos 3MF por kit e um com todas as placas, título, resumo, descrição PT+EN, tags até 100 caracteres, categoria, licença, capa 4:3 e App cover 3:4, vídeo e GIF, fotos reais tratadas, Model Pictures (fundo liso), Print Profile Pictures e Print Profile Description. Use sempre que ele falar em publicar, postar, subir ou lançar um modelo no MakerWorld (ou Printables), pedir capa, fotos do modelo, tags, licença, categoria, descrição de modelo ou perfil de impressão, ou quando um projeto de modelagem for "fechado" e o próximo passo natural for publicar.
---

# Publicar no MakerWorld

Objetivo: entregar uma pasta `PUBLICACAO_MakerWorld/` em que cada campo do formulário já tem
arquivo ou texto pronto, na ordem em que o formulário pede. O dono só copia e cola.

Marca do dono: **ByteLayer (@ByteLayer)**, logo em `referencias/logo_bytelayer.png`.
Paleta: carvão `#1e2024`, laranja `#ff8a3d`, pêssego `#ffc9a3`, creme `#f6eee6`.

## Ordem de trabalho

1. **Pré-voo (bloqueia o resto).**
   - Se houve modelo de inspiração, ler a licença dele. SDFL e "No derivatives" proíbem remix:
     a geometria tem de ser refeita do zero, e o crédito vira "inspirado em", com link.
   - Juntar os números reais do projeto: tamanhos, faixa de espessura que cada versão cobre,
     tempo e gramas por placa (do fatiamento, nunca estimados) e as folgas calibradas.
   - Conferir se há fotos reais da peça impressa. Sem foto real, o Print Profile pode ser
     derrubado: pedir as fotos ao dono logo no início (roteiro em `referencias/midia.md`).
2. **Arquivos 3MF** → `referencias/campos.md` § Arquivos.
3. **Textos** (título, resumo, descrição PT+EN, tags, Print Profile Description) →
   modelos e exemplo completo em `referencias/textos.md`.
4. **Mídia** (capa 4:3, App cover 3:4, vídeo, GIF, fotos tratadas, Model Pictures) →
   receitas em `referencias/midia.md`, scripts-exemplo em `scripts/`.
5. **Conferência final** (checklist abaixo) e entrega com um guia campo a campo.

Rodar trabalho pesado (fatiar, renderizar) **um de cada vez**, com retorno curto a cada passo.

## Campos do formulário: o que vai em cada um

| Campo | O que entregar | Regra que já causou retrabalho |
|---|---|---|
| Model Files | 1 3MF por kit + 1 3MF com todas as placas | filamento de **sistema** (ex. Generic PETG @BBL A1), não o calibrado do dono |
| Title | frase com o benefício + materiais + tamanhos | chamativa mas verificável; nada de "o melhor do MakerWorld" |
| Summary | 1 linha | o que faz + onde serve + "sem suporte" se for verdade |
| Cover (4:3) | 1600×1200 | render bonito com logo e 3 selos; é a vitrine |
| App cover (3:4) | 1200×1600 | campo separado; recompor, não esticar a 4:3 |
| Gallery (imagens do modelo) | fotos reais tratadas + renders + tabela "qual arquivo" + GIF | 1ª posição = foto real instalada |
| Video | MP4 1080p, 15–30 s, sem som obrigatório | foco no modelo (regra da plataforma); GIF ≤ 30 MB de reserva |
| Description | PT + EN, estrutura fixa | ver `textos.md` |
| Tags | ≤ 100 caracteres, separadas por vírgula | maioria em **inglês** + 1–2 termos PT; ver `textos.md` |
| Category | a mesma do modelo parecido mais popular | ex. passador: Casa (Household) > Escritório (Office) |
| License | ver tabela em `campos.md` | padrão dele: "Yes, share alike" + comercial "No" |
| **Model Pictures** | **outras** fotos: peça real recortada sobre fundo liso de uma cor, 4:3 | **campo separado da galeria — não repetir as mesmas fotos** |
| Print Profile Pictures | ≥ 1 foto real; a 1ª vira miniatura do perfil | sem foto real o perfil pode ser removido |
| Print Profile Description | perfil usado + tabela tempo/gramas por placa + dicas | números do fatiamento |

Especificações completas (tamanhos, limites, quantidades) em `referencias/campos.md`.

## Pasta de entrega

```
PUBLICACAO_MakerWorld/
├─ <Marca>_<modelo>_<tamanho>_<versao>.3mf     (um por kit)
├─ <Marca>_<modelo>_TODOS_<tamanhos>.3mf       (todas as placas)
├─ DESCRICAO_MakerWorld.md                     (título, resumo, PT, EN, tags, categoria,
│                                               licença, Print Profile Description)
├─ Galeria_imagens/   01_foto_real... 02_capa... NN_render... NN_qual_arquivo... NN_animacao.gif
├─ Model_Pictures/    1_... 4_...  (recortes em fundo liso, 1600×1200)
└─ midia/             capa_4x3_1600x1200.png  capa_app_3x4_1200x1600.png
                      video_<marca>_<modelo>.mp4  .gif  fotos/
```

Numerar as imagens na ordem em que devem subir. Emitir só dentro da pasta do projeto que o
dono abriu.

## Checklist final (conferir por inspeção, não de memória)

- [ ] Cada 3MF fatiado **um por vez** no `bambu-studio.exe` CLI: nº de objetos por placa,
      sem suporte, furos abertos no G-code (skill `bambu-a1`, `references/operacao.md`).
- [ ] Tempos e gramas da descrição e do perfil batem com o `result.json`/G-code.
- [ ] Toda afirmação da descrição é verdadeira e testada ("testado de verdade" só se foi).
- [ ] Tags contadas: ≤ 100 caracteres, sem repetir palavra à toa.
- [ ] Capa 4:3 e App cover 3:4 abertas e olhadas; texto legível em miniatura.
- [ ] Vídeo assistido em 3–5 quadros (início, meio, fim); legenda não cobre a peça.
- [ ] Model Pictures ≠ fotos da galeria; fundo liso; peça não retocada (só o fundo trocado).
- [ ] Nenhum arquivo acima de 30 MB.
- [ ] Crédito ao modelo de inspiração, se houver, com link.
- [ ] Entregar ao dono a lista "campo → arquivo/texto", na ordem do formulário.

## Exemplo real

Passador de cabo ByteLayer (27/09/2026): pasta
`Modelagem 3D\Passador de cabo 40mm\PUBLICACAO_MakerWorld\` tem todos os itens acima prontos.
Use como gabarito de nível de acabamento.
