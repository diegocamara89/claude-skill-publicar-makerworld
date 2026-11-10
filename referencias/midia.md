# Mídia — receitas

Scripts-exemplo de mídia em `../scripts/` vieram do passador de cabo, exceto `desfoca_fundo_nome.py`: as constantes do topo (nomes de
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

## Fotos leves para o envio

`scripts/fotos_leves.py <saida> <fotos...>`: gira pelo EXIF, reduz o maior lado a 2000 px (JPEG 88) e
grava sem metadados. Foto de celular de 8 MB vira ~0,4 MB, e a extensão do Chrome (10 MB por chamada)
manda o lote de uma vez. As fotos do celular do dono trazem **GPS** no EXIF; o MakerWorld tira ao
reprocessar (conferido em 11/10/2026), mas o arquivo leve já sai limpo.

## Vídeo de remix: só o que mudou, em laranja

Para remix, o vídeo mostra as peças lado a lado e pinta de laranja as faces novas (cortes, chanfros,
rampas, base reta). Testado no suporte Arzopa (11/10/2026, 19 s, 1080p, aprovado pelo dono).
1. `scripts/destaca_mudancas.py original.stl novo.stl saida/A --girar x:90 --mover 7,0,57.5 --final y:90`
   → `A_base.stl` e `A_novo.stl`. A mediana de distância das faces antigas tem de dar ~0 mm; se não,
   o alinhamento (girar/mover) está errado.
2. `scripts/video_remix_blender.py` pelo `trabalho_blender.py` (skill `modelagem-3d`), com `cena.json`
   (peças, deslocamento, quadros-chave de câmera). Testar 6 quadros em 960×540 antes do lote.
   Cada plano olha a face onde está a mudança (janela por baixo, recorte na lateral, chanfro na boca).
3. `scripts/legendas_video.py legendas.json quadros quadros_leg logo.png --mp4 v.mp4 --gif v.gif`:
   legendas por plano (canto configurável) e cartela com logo e créditos dos autores originais.
4. Conferir 5 quadros do MP4: legenda não cobre a peça. Apagar os quadros (≈2 GB) depois do aval.

## Fotos reais tratadas (galeria)

`scripts/trata_fotos.py` (OpenCV): por foto, centro/raio da peça e caixa de corte 4:3.
Faz: poeira fora da peça (top-hat + inpaint, nunca dentro do círculo da peça), tom (CLAHE leve,
sombras abertas, tira azulado), foco (escurece o fundo fora da peça), nitidez leve, saída
1600×1200. **A peça não é retocada.**
Para pedido de borrar fundo e identidade, usar a receita abaixo, em vez do círculo aproximado.
Tratamento é opcional. No piloto do suporte, fotos originais de 1200×1600 instaladas foram
enviadas e persistiram sem recorte; preservavam informações úteis sobre grade e fixação.

## Fundo borrado e nome ocultado — tratamento local aprovado

Receita aprovada visualmente pelo dono em 12/10/2026 na amostra Desk V3 (1280×960).
A aprovação cobre aquela amostra; cada foto nova exige contorno e inspeção próprios.
Processar localmente com OpenCV/NumPy já disponíveis. Fotos privadas com nomes ou identidade
institucional ficam no computador; não encaminhar a geradores de IA ou serviços externos.

1. Abrir o original e trabalhar em cópia. Fixar orientação e resolução **antes** de medir
   coordenadas. Fazer um recorte ampliado da identificação, ou uma grade de coordenadas
   privada, para localizar o nome exatamente; não reaproveitar a posição de outra foto.
2. Desenhar polígonos que preservem a silhueta da montagem, inclusive celular e acessórios
   úteis. Desfocar todo o restante com GaussianBlur, sigma 18 px; suavizar a máscara com
   sigma 4 px. Compor `original × máscara + fundo_desfocado × (1 − máscara)`.
   Preservar também os vazios entre peças: fundo visível através de um vão não é produto.
3. Para ocultar **somente a identificação autorizada**, delimitar um polígono estreito em
   perspectiva sobre o nome. Aplicar `cv2.inpaint`, `INPAINT_TELEA`, raio 2 px, e misturar
   a reconstrução local usando a máscara suavizada com sigma 2 px. Essa exceção de privacidade
   modifica a inscrição; não corrigir defeitos de impressão, bordas, furos ou geometria.
4. Salvar JPEG 95 sem EXIF/GPS. Abrir a foto inteira e ampliar a região do nome: confirmar
   que não há letras legíveis, manchas, halos, pedaços do produto borrados ou fundo nítido
   esquecido. A máscara suavizada não garante anonimização: se restar letra, ajustar o
   polígono e inspecionar novamente.
5. Mostrar uma amostra ao dono quando ele pedir revisão prévia. Após aprovação, aplicar
   o estilo às demais fotos com coordenadas próprias e conferir o conjunto antes do envio.

Os valores em pixels são ponto de partida para 1280×960; adaptar à resolução e ao resultado.
O procedimento preserva o contexto da mesa e a nitidez do produto. Não usar desfoque global,
retângulos grandes atravessando a peça ou mistura fraca que deixe o fundo legível. Não substituir
fotos reais por imagens geradas.

### Execução reutilizável

Copiar `scripts/desfoca_fundo_nome.py` para a pasta privada de mídia do projeto. Criar um JSON
por foto com `origem`, `saida` (cópia), `tamanho: [largura, altura]`, `preservar` (lista de
polígonos) e `ocultar_nome` (lista de polígonos; vazia se não houver nome). Cada polígono é
uma lista de pares `[x, y]`, medidos a partir do canto superior esquerdo da foto orientada.
Os caminhos relativos são resolvidos a partir do JSON. Parâmetros opcionais:
`sigma_fundo: 18`, `sigma_borda: 4`, `raio_nome: 2`, `sigma_nome: 2`.

```powershell
python "<projeto>/FOTOS_PRIVADAS/desfoca_fundo_nome.py" "<projeto>/FOTOS_PRIVADAS/foto_01.json"
```

Guardar o JSON junto da cópia tratada para repetir o resultado. Coordenadas, recortes ampliados
e originais ficam privados; somente as imagens finais aprovadas entram no pacote público.

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
