---
name: publicar-makerworld
description: Prepara o pacote de publicação de um modelo 3D no MakerWorld — 3MF, textos só em português, tags, categoria, licença, capas, animação e fotos reais — e confere o envio quando autorizado. Use para publicar, postar ou preparar os campos e mídias de um modelo no MakerWorld.
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
   - **Licença herdada:** remix de modelo **BY-NC-SA** (ou de um remix dele) tem de sair
     **CC BY-NC-SA 4.0**: o "SA" obriga a mesma licença. O formulário só habilita a opção SA ao
     ligar a origem. Ler a licença na página de cada elo da cadeia de remixes, não só no 3MF.
   - Juntar os números reais do projeto: tamanhos, faixa de espessura que cada versão cobre,
     tempo e gramas por placa (do fatiamento, nunca estimados) e as folgas calibradas.
   - Localizar e abrir as fotos já entregues, inclusive em `midia/fotos/`, antes de pedir
     imagens. Registrar o teste informado pelo dono e encerrar a pendência correspondente.
     Se faltarem fotos reais, pedir somente o necessário (roteiro em `referencias/midia.md`)
     e preparar os itens independentes enquanto aguarda.
2. **Arquivos 3MF** → `referencias/campos.md` § Arquivos. Montar com `scripts/monta_3mf.py`
   (qualquer conjunto de peças, perfil 0,20/0,28, exporta o 3MF completo e lê tempo, gramas e suporte).
3. **Textos** (título, resumo, descrição, tags, Print Profile Description), **só em português** →
   modelos e exemplo completo em `referencias/textos.md`.
4. **Mídia** (capa 4:3, App cover 3:4, vídeo, GIF, fotos tratadas, Model Pictures) →
   receitas em `referencias/midia.md`, scripts em `scripts/`. Para borrar fundo e ocultar nome,
   seguir a seção “Fundo borrado e nome ocultado” e usar `scripts/desfoca_fundo_nome.py` localmente.
   Fotos de celular passam por
   `fotos_leves.py` (≤ 1 MB, sem GPS). Remix: vídeo com as mudanças em laranja
   (`destaca_mudancas.py` → `video_remix_blender.py` → `legendas_video.py`).
5. **Conferência final** (checklist abaixo) e entrega com um guia campo a campo.
6. **Envio, quando solicitado** → `referencias/automacao.md`. Criar uma entrada
   `POSTAGEM.json` com campos, anexos, HTML revisado e placas esperadas; validar localmente.
   **O Claude posta ele mesmo pelo Claude in Chrome** (§ "Rota principal: Claude in Chrome").
   **Não delegar a postagem ao Codex:** o Codex fica sem navegador conectado (`cua_repl` com
   `browsers: []`) e todas as tentativas do dono falharam (a última em 11/10/2026). Conferir
   o rascunho salvo e reaberto antes de publicar: `captura_rascunho.js` na página +
   `monta_captura.py` + `valida_postagem.py conferir`, que precisa dar `conferencia_ok: true`.
   Tags pelo `tags_lote.js` (tira acento, blocos de 10). Não duplicar rascunho na retomada.

Rodar trabalho pesado (fatiar, renderizar) **um de cada vez**, com retorno curto a cada passo.

## Campos do formulário: o que vai em cada um

| Campo | O que entregar | Regra que já causou retrabalho |
|---|---|---|
| Model Files | 1 3MF por kit + 1 com todas as placas, se houver vários kits; perfil extra (ex. 0,28 rápido) = 3MF próprio | um kit não exige um arquivo TODOS duplicado; filamento de **sistema** (ex. Generic PETG @BBL A1), não o calibrado do dono |
| Title | frase com o benefício + materiais + tamanhos | chamativa mas verificável; nada de "o melhor do MakerWorld" |
| Summary | 1 linha | o que faz + onde serve + "sem suporte" se for verdade |
| Cover (4:3) | 1600×1200 | render bonito com logo e 3 selos; é a vitrine |
| App cover (3:4) | 1200×1600 | campo separado; recompor, não esticar a 4:3 |
| Fotos da vida real | ≥ 3 fotos reais cobrindo 3 vistas, até 16 | 1ª posição = foto real instalada; **só foto real** (o campo é "photos of the printed model"): imagem explicativa (qual perfil, medidas, render) vai em Print Profile Pictures, depois da foto real (12/10/2026) |
| Video | MP4 1080p, 15–30 s, sem som obrigatório | foco no modelo (regra da plataforma); GIF ≤ 30 MB de reserva |
| Description | **só PT**, estrutura fixa (decisão do dono em 06/10/2026: o MakerWorld traduz sozinho; não escrever versão EN) | ver `textos.md` |
| Tags | até 50 entradas, até 100 caracteres por entrada | maioria em **inglês** + termos PT **sem acento** (o site corta letras acentuadas: "portátil" vira "porttil"); marca do produto compatível entra (pedido do dono, 11/10/2026) |
| Category | a mesma do modelo parecido mais popular | ex. passador: Casa (Household) > Escritório (Office) |
| License | ver tabela em `campos.md` | preferência atual: CC BY-NC 4.0; **remix de BY-NC-SA sai BY-NC-SA** |
| **Model Pictures** | **outras** fotos reais, até 16; 4:3 recomendado | campo separado; fundo simples é recomendação, preservar contexto útil de uso |
| Print Profile Pictures | ≥ 1 foto real; a 1ª vira miniatura do perfil | sem foto real o perfil pode ser removido |
| Print Profile Description | perfil usado + tabela tempo/gramas por placa + dicas | números do fatiamento |

Especificações completas (tamanhos, limites, quantidades) em `referencias/campos.md`.

## Pasta de entrega

```
PUBLICACAO_MakerWorld/
├─ <Marca>_<modelo>_<tamanho>_<versao>.3mf     (um por kit)
├─ <Marca>_<modelo>_TODOS_<tamanhos>.3mf       (todas as placas)
├─ DESCRICAO_MakerWorld.md                     (título, resumo, descrição PT, tags, categoria,
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
- [ ] Tags: até 50 entradas de até 100 caracteres, sem repetir palavra à toa, sem acento.
- [ ] Licença compatível com a de cada elo da cadeia de remixes (BY-NC-SA → BY-NC-SA).
- [ ] Fotos de envio ≤ 10 MB cada (limite por chamada da extensão) e sem metadados de GPS.
- [ ] Capa 4:3 e App cover 3:4 abertas e olhadas; texto legível em miniatura.
- [ ] Vídeo assistido em 3–5 quadros (início, meio, fim); legenda não cobre a peça.
- [ ] Model Pictures ≠ fotos da galeria; peça não retocada (exceto identificação ocultada a pedido); fundo e enquadramento permitem
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

