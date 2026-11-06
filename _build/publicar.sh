#!/usr/bin/env bash
# Publica o site no GitHub Pages (soareslopes/bfi_explorer, ramo main, raiz).
#
#   ./_build/publicar.sh                       mostra o que mudaria, sem enviar
#   ./_build/publicar.sh --enviar              gera, faz commit e envia
#   ./_build/publicar.sh --enviar "mensagem"   idem, com mensagem de commit
#
# A pasta explorador-v1/ do repositorio nunca e tocada: e o arquivo da versao
# anterior e vive apenas la, nao neste projecto.
set -euo pipefail

REPO=https://github.com/soareslopes/bfi_explorer.git
BASE=https://soareslopes.github.io/bfi_explorer/
SITE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENVIAR=${1:-}
MSG=${2:-Actualiza o site}

echo "==> a gerar o site com BASE_URL=$BASE"
cd "$SITE"
python3 _build/1_dados.py
BFI_BASE_URL="$BASE" python3 _build/2_paginas.py

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
echo "==> a clonar o repositorio"
git clone --quiet --depth 1 "$REPO" "$TMP/repo"

echo "==> a copiar o site (explorador-v1/ fica intacto)"
rsync -a --delete \
      --exclude '.git/' --exclude 'explorador-v1/' \
      "$SITE"/ "$TMP/repo"/

cd "$TMP/repo"
if git diff --quiet && git diff --cached --quiet && [ -z "$(git status --porcelain)" ]; then
  echo "==> nada mudou, nada a publicar"; exit 0
fi

echo "==> alteracoes:"
git add -A
git diff --cached --stat | tail -15

if [ "$ENVIAR" != "--enviar" ]; then
  echo
  echo "==> simulacao. Para publicar mesmo: ./_build/publicar.sh --enviar"
  exit 0
fi

git commit --quiet -m "$MSG

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
git push origin main
echo "==> enviado. O Pages leva cerca de um minuto a reconstruir."
echo "    $BASE"
