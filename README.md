# publicar-makerworld

Skill para Claude Code que prepara o pacote de publicação de um modelo 3D no [MakerWorld](https://makerworld.com): arquivos 3MF, textos em português e inglês, tags, categoria, licença, capas, animação e fotos reais tratadas.

O resultado é uma pasta `PUBLICACAO_MakerWorld/` em que cada campo do formulário já tem o arquivo ou o texto pronto, na ordem em que o formulário pede. Preparar o pacote não é publicar: o envio só acontece quando o dono autoriza.

## O que ela faz

- **Pré-voo:** confere a licença do modelo de inspiração (SDFL e "No derivatives" proíbem remix) e junta os números reais do projeto, como tempo e gramas por placa tirados do fatiamento, nunca estimados.
- **Textos:** título, resumo, descrição, tags e descrição do perfil de impressão, com modelos em `referencias/textos.md`.
- **Mídia:** capa 4:3, capa do app 3:4, vídeo, GIF e fotos tratadas, com scripts em `scripts/`.
- **Conferência:** checklist final e guia campo a campo.
- **Envio automatizado (opcional):** monta um `POSTAGEM.json`, valida localmente e confere a captura real depois do envio.

## Instalação

Copie a pasta do repositório para a pasta de skills do Claude Code (`~/.claude/skills/publicar-makerworld`). A skill é ativada quando você pede para publicar ou preparar um modelo no MakerWorld.

## Estrutura

```
SKILL.md          instruções da skill
referencias/      campos do formulário, textos, mídia e automação
scripts/          tratamento de fotos, capas, validação e rascunho automatizado (com testes)
```

## Testes

```bash
python scripts/test_valida_postagem.py
node scripts/test_rascunho_makerworld.mjs
```
