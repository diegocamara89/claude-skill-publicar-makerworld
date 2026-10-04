---
name: publicar-makerworld
description: Prepara o pacote de publicação de um modelo 3D no MakerWorld — 3MF, textos PT+EN, tags, categoria, licença, capas, animação e fotos reais — e confere o envio quando autorizado. Use para publicar, postar ou preparar os campos e mídias de um modelo no MakerWorld.
---

# Publicar no MakerWorld

Objetivo: entregar uma pasta `PUBLICACAO_MakerWorld/` em que cada campo do formulário já tem
arquivo ou texto pronto, na ordem em que o formulário pede. O pacote pode ser usado no envio
manual ou em uma automação validada. Preparar o pacote não significa que ele foi publicado.

Marca do dono: **ByteLayer (@ByteLayer)**, logo em `referencias/logo_bytelayer.png`.
Paleta: carvão `#1e2024`, laranja `#ff8a3d`, pêssego `#ffc9a3`, creme `#f6eee6`.

## Ordem de trabalho

1. **Pré-voo (pendências bloqueiam a publicação, não a preparação independente).**
   - Se houve modelo de inspiração, ler a licença dele. SDFL e "No derivatives" proíbem remix:
     a geometria tem de ser refeita do zero, e o crédito vira "inspirado em", com link.
   - Juntar os números reais do projeto: tamanhos, faixa de espessura que cada versão cobre,
     tempo e gramas por placa (do fatiamento, nunca estimados) e as folgas calibradas.
   - Localizar e abrir as fotos já entregues, inclusive em `midia/fotos/`, antes de pedir
     imagens. Registrar o teste informado pelo dono e encerrar a pendência correspondente.
     Se faltarem fotos reais, pedir somente o necessário (roteiro em `referencias/midia.md`)
     e preparar os itens independentes enquanto aguarda.
2. **Arquivos 3MF** → `referencias/campos.md` § Arquivos.
3. **Textos** (título, resumo, descrição PT+EN, tags, Print Profile Description) →
   modelos e exemplo completo em `referencias/textos.md`.
4. **Mídia** (capa 4:3, App cover 3:4, vídeo, GIF, fotos tratadas, Model Pictures) →
   receitas em `referencias/midia.md`, scripts-exemplo em `scripts/`.
5. **Conferência final** (checklist abaixo) e entrega com um guia campo a campo.
6. **Envio automatizado, quando solicitado** → `referencias/automacao.md`. Criar uma entrada
   `POSTAGEM.json` com campos, anexos, HTML revisado e placas esperadas; validar localmente.
   Reutilizar `rascunho_makerworld.mjs` para lotes, retomada e modelo/perfil salvos e reabertos;
   `valida_postagem.py conferir` verifica a captura real. Mapear controles na primeira rodada
   e manter a conferência nas próximas. Não criar outro uploader ou duplicar rascunho na retomada.

Rodar trabalho pesado (fatiar, renderizar) **um de cada vez**, com retorno curto a cada passo.

## Campos do formulário: o que vai em cada um

| Campo | O que entregar | Regra que já causou retrabalho |
|---|---|---|
| Model Files | 1 3MF por kit + 1 com todas as placas, se houver vários kits | um kit não exige um arquivo TODOS duplicado; filamento de **sistema** (ex. Generic PETG @BBL A1), não o calibrado do dono |
| Title | frase com o benefício + materiais + tamanhos | chamativa mas verificável; nada de "o melhor do MakerWorld" |
| Summary | 1 linha | o que faz + onde serve + "sem suporte" se for verdade |
| Cover (4:3) | 1600×1200 | render bonito com logo e 3 selos; é a vitrine |
| App cover (3:4) | 1200×1600 | campo separado; recompor, não esticar a 4:3 |
| Fotos da vida real | ≥ 3 fotos reais cobrindo 3 vistas, até 16 | 1ª posição = foto real instalada; renders não completam esse requisito |
| Video | MP4 1080p, 15–30 s, sem som obrigatório | foco no modelo (regra da plataforma); GIF ≤ 30 MB de reserva |
| Description | PT + EN, estrutura fixa | ver `textos.md` |
| Tags | até 50 entradas, até 100 caracteres por entrada | maioria em **inglês** + 1–2 termos PT; limites do formulário em `campos.md` |
| Category | a mesma do modelo parecido mais popular | ex. passador: Casa (Household) > Escritório (Office) |
| License | ver tabela em `campos.md` | preferência atual: CC BY-NC 4.0 — permitir reutilização/adaptação com crédito, sem uso comercial |
| **Model Pictures** | **outras** fotos reais, até 16; 4:3 recomendado | campo separado; fundo simples é recomendação, preservar contexto útil de uso |
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
├─ POSTAGEM.json                             (entrada revisada para validação/automação)
├─ Galeria_imagens/   01_foto_real... 02_capa... NN_render... NN_qual_arquivo... NN_animacao.gif
├─ Model_Pictures/    fotos reais adicionais
├─ Print_Profile_Pictures/  foto real do resultado do perfil
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
- [ ] Tags: até 50 entradas de até 100 caracteres, sem repetir palavra à toa.
- [ ] Capa 4:3 e App cover 3:4 abertas e olhadas; texto legível em miniatura.
- [ ] Vídeo assistido em 3–5 quadros (início, meio, fim); legenda não cobre a peça.
- [ ] Model Pictures ≠ fotos da galeria; peça não retocada; fundo e enquadramento permitem
      conferir o produto. Tratamento e recorte só quando melhorarem a leitura.
- [ ] Mídias dentro dos limites do formulário; referência registrada: 30 MB por imagem/GIF.
- [ ] Crédito ao modelo de inspiração, se houver, com link.
- [ ] Entregar ao dono a lista "campo → arquivo/texto", na ordem do formulário.
- [ ] Se houver automação: não cortar texto/tags, escolher categoria pela posição, substituir
      3MF por STL ou completar fotos com renders/duplicatas. Conferir o conteúdo salvo.
- [ ] No perfil, conferir placas reconhecidas. Se aparecer zero, seguir a exportação completa
      em `campos.md`; arquivo aceito não comprova placa reconhecida.
- [ ] Após enviar, distinguir “Verificando” da página pública disponível, conforme
      `automacao.md`; registrar o estado observado.

## Exemplo real

Passador de cabo ByteLayer (27/09/2026): pasta
`Modelagem 3D\Passador de cabo 40mm\PUBLICACAO_MakerWorld\` tem todos os itens acima prontos.
Use como gabarito de nível de acabamento.
