# Bike Friendly Index · Portugal

**[https://soareslopes.github.io/bfi_explorer/](https://soareslopes.github.io/bfi_explorer/)**

Site do Bike Friendly Index, o índice que avalia a amigabilidade dos 278 municípios
de Portugal Continental para a utilização da bicicleta como modo de transporte
urbano. Edições de 2018 e 2025, em português e em inglês.

Publicado por GitHub Pages a partir da raiz do ramo `main`.

## O que está neste repositório

| Pasta | Conteúdo |
|---|---|
| raiz | O site, em português |
| `en/` | O mesmo site, em inglês |
| `municipio/`, `en/municipality/` | 278 fichas por língua |
| `assets/` | Folha de estilo e JavaScript |
| `dados/` | Ficheiros para download, em CSV, GeoJSON e JSON |
| `_build/` | Os geradores que produzem o site |
| `explorador-v1/` | A versão anterior do explorador, arquivada |

### Explorador anterior

A versão que estava publicada até agora continua acessível em
[`explorador-v1/`](explorador-v1/), tal como foi publicada, e está ligada a partir
do rodapé e da página do explorador. O ficheiro `concelhos_bfi_2018.geojson` que
acompanhava essa versão foi renomeado para `concelhos_bfi_2025_rascunho.geojson`:
apesar do nome antigo, não continha os resultados de 2018 mas sim um apuramento
intermédio de 2025, e já não era usado pelo `config.json`.

---

Site estático do Bike Friendly Index, gerado a partir dos dados em
`_novo_site/dados_site/`. Não precisa de servidor para funcionar: todos os dados
são carregados por `<script src>` e não por `fetch`, por isso abre directamente
do disco.

## Abrir

Duplo clique em `index.html`, ou:

```bash
open index.html
```

Para servir em HTTP (útil para testar como ficará publicado):

```bash
cd "$(dirname "$0")" && python3 -m http.server 8787
```

## Páginas

Site bilingue. Português na raiz, inglês em `/en/`. Cada página tem o alternador
de língua na barra de navegação e declara `hreflang` para a sua tradução.

| Português | English | Conteúdo |
|---|---|---|
| `index.html` | `en/index.html` | Apresentação, número nacional, mapa, seis indicadores de topo |
| `resultados-2025.html` | `en/results-2025.html` | Resultados de 2025, mapa por dimensão, topo e cauda, capitais, ranking completo |
| `resultados-2018.html` | `en/results-2018.html` | Arquivo de 2018, nas duas séries (publicada e recalculada) |
| `comparacao.html` | `en/comparison.html` | 2018 contra 2025, série comparável, mapa de variação, dispersão, maiores movimentos |
| `municipios.html` | `en/municipalities.html` | Grelha de 278 cartões, com procura, filtros e ordenações |
| `municipio/<slug>.html` | `en/municipality/<slug>.html` | 278 fichas: score, posição, perfil, 25 indicadores, vizinhança |
| `explorador.html` | `en/explorer.html` | Mapa interactivo por série e dimensão, com painel e extremos |
| `comparar.html` | `en/compare.html` | Até três municípios lado a lado |
| `metodologia.html` | `en/methodology.html` | Dimensões, pesos, normalização, os 25 indicadores, fontes, limitações |
| `dados.html` | `en/data.html` | Descarregar CSV, GeoJSON e JSON |
| `sobre.html` | `en/about.html` | Equipa, edições, citação, licença |

São 22 páginas mais 556 fichas, 278 por língua.

## Traduzir

O texto das páginas vive nas chamadas a `L(português, english)` dentro de
`_build/2_paginas.py`, ao lado do sítio onde é usado. Os nomes das dimensões e
dos 25 indicadores, e as strings que o JavaScript desenha (cabeçalhos de tabela,
rótulos de gráficos, legendas), estão em `_build/i18n.py`, que é a fonte única
de verdade e gera `assets/js/i18n.js`.

Para acrescentar uma língua: juntar a chave a `i18n.LANGS` e aos dicionários,
estender `L()` e `PAGES` em `_build/layout.py`, e correr a construção.

## Fundo de mapa do explorador

Por omissão usa os mosaicos padrão do OpenStreetMap, que não exigem chave.
A política de utilização desses mosaicos não é pensada para sítios de tráfego
elevado: **antes de publicar, convém contratar um fornecedor** (MapTiler com o
esquema OpenMapTiles, CARTO, Stadia) e definir `window.BFI_TILES` antes de
`map.js` ser carregado:

```html
<script>
window.BFI_TILES = {
  light: 'https://api.maptiler.com/maps/positron/{z}/{x}/{y}.png?key=SUA_CHAVE',
  dark:  'https://api.maptiler.com/maps/darkmatter/{z}/{x}/{y}.png?key=SUA_CHAVE'
};
</script>
```

Sem `dark`, os mosaicos claros são invertidos por filtro CSS em modo escuro.
A atribuição ao fornecedor é obrigatória e aparece no canto inferior esquerdo
do mapa.

## Publicar

```bash
./_build/publicar.sh
```

Gera o site, clona o repositório para uma pasta temporária, copia tudo por cima
e mostra o que mudaria, sem enviar nada. Para publicar mesmo:

```bash
./_build/publicar.sh --enviar "o que mudou"
```

A pasta `explorador-v1/` do repositório nunca é tocada: é o arquivo da versão
anterior e vive só lá, não neste projecto. A marca de versão dos assets depende
do conteúdo, por isso gerar duas vezes sem alterar nada produz exactamente o
mesmo site e o script diz que não há nada a publicar.

O GitHub Pages leva cerca de um minuto a reconstruir.

## Regenerar

Depois de mudar os dados em `_novo_site/dados_site/`:

```bash
python3 _build/1_dados.py && python3 _build/2_paginas.py
```

`1_dados.py` escreve `assets/js/data.js`, `assets/js/geo.js` e `assets/js/i18n.js`.
`2_paginas.py` escreve todas as páginas HTML nas duas línguas, fichas incluídas.
Os ficheiros de `dados/` são cópias dos de `_novo_site/dados_site/` para download, excepto `bfi_indicadores.csv`, que `1_dados.py` gera só com valores medidos e posição (sem normalização nem pesos).

## Estrutura

```
site/
  _build/          geradores (1_dados.py, 2_paginas.py, layout.py)
  assets/css/      folha de estilo única
  assets/js/       data.js e geo.js gerados; app, charts, map, table escritos à mão
  dados/           ficheiros para download
  municipio/       278 fichas em português
  en/              a árvore inglesa inteira, com en/municipality/
```

## Notas técnicas

- Sem dependências externas de JavaScript. Os mapas são SVG gerado a partir da
  geometria projectada em Mercator por `1_dados.py`, e os gráficos são SVG escrito
  à mão em `assets/js/charts.js`.
- O explorador tem um fundo de mosaicos por baixo do coroplético. Como a projecção
  do SVG é Web Mercator com a longitude em graus, o alinhamento com a grelha de
  mosaicos é uma transformação linear, calculada em `drawTiles()` dentro de
  `assets/js/map.js`. Não há biblioteca de mapas envolvida.
- As únicas chamadas à rede são os tipos de letra do Google Fonts. Sem internet,
  o site usa as alternativas do sistema e mantém-se legível.
- Paleta de dados validada: rampa sequencial azul para magnitude, par divergente
  azul e vermelho para variação, três cores categóricas para séries. A rampa
  sequencial tem passos próprios para fundo escuro.
- Modo claro e escuro, com memória da escolha no browser.
- Bilingue com URLs próprios por língua, `hreflang`, `lang` no `<html>` e
  formatação numérica por locale (vírgula decimal em português, ponto em inglês).
- As referências a CSS e JS levam uma marca de versão gerada na altura da
  construção, para que o browser não sirva ficheiros em cache depois de regenerar.
