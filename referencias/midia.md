# Mídia — receitas

Scripts-exemplo de mídia em `../scripts/` vieram do passador de cabo: as constantes do topo (nomes de
arquivo, coordenadas, textos) são daquele projeto e precisam ser trocadas. Copiar para
`<projeto>/midia/` antes de usar; não rodar dentro da pasta da skill.

## Roteiro de fotos para pedir ao dono (no início)

Antes de pedir, localizar e inspecionar as imagens já fornecidas. O roteiro abaixo veio do
passador de cabo: adaptar as vistas à função do produto. Para o formulário atual, reservar
ao menos três fotos reais distintas cobrindo três vistas e uma foto real do resultado do
perfil. Uma foto pode ser reaproveitada no perfil; não duplicar dentro do mesmo campo.

Celular, luz de janela, sem flash:
1. Peça instalada, tampa fechada (de cima, ~45°).
2. Peça instalada, tampa aberta, com cabos passando.
3. Peças soltas lado a lado, **sobre folha branca ou cartolina lisa** (vira Model Picture sem
   recorte difícil).
4. Detalhe do diferencial (ex. a porca por baixo).
Foto de peça preta sobre fundo preto não recorta bem por cor (GrabCut falhou); por isso a folha.

## Capa 4:3 e App cover 3:4

1. Render no Blender: `scripts/cena_marketing.py`, modo `"capa"` (Cycles, GPU se houver),
   rodado pelo contrato `executar(config)` de `executa_com_relatorio.py` via `roda_blender.py`
   (skill `modelagem-3d`, pasta `scripts/`), num Blender separado.
   - config: `base` (STLs de montagem), `modo`, `saida`, `res` ([1600,1200] ou [1200,1600]),
     `amostras`, `luz`, `luz_baixo`, `az`, `el`, `dist`, `dx`, `dy`, `dz` (enquadramento).
   - Deixar espaço vazio no canto de cima à esquerda para o texto.
2. Composição: `scripts/compoe_capa.py` (PIL): escurece o canto do texto, põe logo + "ByteLayer",
   título em 2 linhas (2ª em laranja), régua, subtítulo e 3 pílulas (tamanhos, versões,
   "Imprime sem suporte"). `python compoe_capa.py` → 4:3; `python compoe_capa.py 3x4` → retrato.
3. Olhar a capa reduzida a ~400 px: o título tem de ler.

Armadilhas de render resolvidas:
- Luz estourada: energias de área na casa de 0,5–3 W com a cena em metros.
- Vidro com retângulo de lâmpada: rugosidade 0,16 e `visible_glossy = False` no contraluz.
- Booleana deixa slot de material vazio → `materials.clear()` antes de aplicar o material.
- Lâmpada aparecendo no quadro → `visible_camera = False`.

## Vídeo (15–20 s, 1080p)

1. Animação de montagem no Blender: `cena_marketing.py` modo `"video"` (EEVEE, 480 quadros
   a 30 fps). Peças entram uma por vez; a câmera passa por baixo do tampo quando a peça de
   baixo trabalha (de cima o vidro reflete e esconde).
   - Preferência do dono: movimento real das peças, organização, encaixe e uso. Zoom sobre
     renders estáticos não atende a esse pedido.
   - Derivar a orientação de uso separadamente da impressão. Conferir apoio, sentido de
     inserção, ordem de montagem e retirada antes de renderizar o lote. No suporte de
     garrafinha, a garra desce sobre o parafuso fixo, com batente acima da cabeça; a montagem
     invertida deixou a garra escapar para baixo. Validar o mecanismo, além de colisões.
   - Flexão ilustrada não comprova resistência ou simula a deformação real do material.
2. Quadros → MP4:
   `ffmpeg -y -framerate 30 -i q_%04d.png -c:v libx264 -crf 17 -preset slow -pix_fmt yuv420p -movflags +faststart render3d.mp4`
3. Legendas e cartela final com HyperFrames (skills `hyperframes` / `general-video`):
   exemplo pronto em `scripts/video_hyperframes_exemplo.html` (render à direita,
   legendas numeradas à esquerda, cartela com logo). `npx hyperframes check` sem erro antes de
   `npx hyperframes render`.
   - Lições do lint: não animar `letterSpacing` (usar `scale`); não repetir a mesma imagem em
     dois `<img>` (copiar o arquivo); não usar `<br>`; proteger `fromTo` de alvo ausente;
     contraste do texto sobre o render (véu radial escuro atrás da legenda).
4. Conferir 5 quadros: `ffmpeg -ss <t> -i video.mp4 -frames:v 1 -vf scale=640:-1 t_<t>.png`.
5. GIF de reserva:
   `ffmpeg -i video.mp4 -vf "fps=12,scale=800:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=160:stats_mode=diff[p];[b][p]paletteuse=dither=sierra2_4a" -loop 0 video.gif`
   (passou de 30 MB → baixar fps para 10 ou largura para 720).

## Fotos reais tratadas (galeria)

`scripts/trata_fotos.py` (OpenCV): por foto, centro/raio da peça e caixa de corte 4:3.
Faz: poeira fora da peça (top-hat + inpaint, nunca dentro do círculo da peça), tom (CLAHE leve,
sombras abertas, tira azulado), foco (escurece o fundo fora da peça), nitidez leve, saída
1600×1200. **A peça não é retocada.**
Tratamento é opcional. No piloto do suporte, fotos originais de 1200×1600 instaladas foram
enviadas e persistiram sem recorte; preservavam informações úteis sobre grade e fixação.

## Model Pictures (fundo liso opcional)

Usar fotos reais adicionais. Não exigir recorte ou fotos novas se o fundo existente permitir
ver a peça e explicar seu uso; proporção 4:3 e fundo simples são recomendações. As receitas
abaixo servem quando limpar o fundo de fato melhora a apresentação.

1. Recorte:
   - fundo claro e liso na foto → GrabCut (`recorta()` em `scripts/fundo_limpo.py`);
   - peça redonda escura sobre fundo escuro → elipse ajustada por RANSAC na borda real
     (`scripts/ajusta_elipse.py` gera `elipses.json`; `mascara_elipse()` usa).
   - Se nada disso servir, `rembg` recorta qualquer coisa, mas exige baixar pacote PyPI e
     modelo de ~170 MB: **pedir permissão antes**.
2. Composição (`compoe()`): fundo cinza muito claro `(236,236,234)` com degradê de 7%, peça
   a ~70% da largura, sombra de contato suave, 1600×1200.
3. Conferir que a borda do recorte não comeu a peça nem deixou halo do fundo antigo.

## Tabela "qual arquivo escolher"

Imagem 1600×1200 com a mesma tabela da descrição (PIL, fontes Segoe/Montserrat, cores da
marca). Vai na galeria perto do fim.
