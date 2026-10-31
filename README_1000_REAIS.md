# ScentMatch — 1000 perfumes reais

## Instalação do catálogo

A base original contém 1320 perfumes e é publicada pela Scento sob licença CC BY 4.0. Como este pacote não inclui uma cópia baixada da internet, é necessário **baixar a base uma vez** no seu computador (conexão à internet necessária).

```powershell
py importar_1000_reais.py
```

O importador seleciona exatamente **1000 nomes e marcas únicos com notas disponíveis**, sem inventar notas, e cria `data/perfumes_1000_reais.csv`. Conserva campos de notas de saída, coração e fundo quando presentes na fonte. Nem todos os perfumes possuem pirâmide completa; campos vazios não são inventados.

## Recomendações

```powershell
py main.py --catalog real --mode sequential --notes "vanilla,lavender,amber" --effort 5000
py main.py --catalog real --mode multiprocessing --workers 4 --notes "vanilla,lavender,amber" --effort 5000
```

**Nota:** notas da fonte são em inglês. Use `vanilla,lavender,amber` (não `baunilha,lavanda,ambar`) para pontuar corretamente a base original.

## Benchmark comparável com 1000 perfumes reais

```powershell
py benchmark.py --catalog real --effort 10000 --repeat 3
```

Para benchmark distribuído, inicie os servidores 9001, 9002 e 9003 em terminais separados e execute:

```powershell
py benchmark.py --catalog real --effort 10000 --repeat 3 --distributed --timeout 60
```

A carga `effort` representa computação determinística efetiva por perfume, não pausas artificiais. A quantidade de registros é 1000, mas os tempos dependem da máquina. Multiprocessing pode ou não superar o sequencial. Os 3 servidores locais compartilham a mesma máquina, portanto não equivalem a 3 computadores físicos.

## Fonte e atribuição

Scento — https://www.scento.com/perfume-database
Dataset: https://github.com/Scento-com/perfume-dataset
Licença: Creative Commons Attribution 4.0 (CC BY 4.0): https://creativecommons.org/licenses/by/4.0/

Atribuição: Scento Perfume Database (2026-10-21). Dados de marcas, perfumes e notas pertencem à fonte; código do importador e transformação para formato ScentMatch são adaptações.
