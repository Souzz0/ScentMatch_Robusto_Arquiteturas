# ScentMatch Robusto — Python, Threads, Processos e TCP

Compatível com Windows (comando `py`).

## O que mudou
- **Carga real de CPU** (`--effort`): cálculo determinístico por registro; NÃO usa `sleep` para fingir desempenho. Não representa IA treinada.
- **Threads e processos**: comparação de custos reais de execução.
- **Distribuído**: lotes TCP para 1 a 3 servidores, timeout e reprocessamento local se um falhar.
- **Falha lenta demonstrável**: `--delay-response` no servidor é uma **simulação explicitamente identificada**, exclusiva do teste de timeout; nunca usada nos benchmarks normais.

## Execução no VS Code
```powershell
py main.py --notes "baunilha,lavanda,ambar"
py main.py --catalog synthetic --size 1200 --effort 2500 --mode sequential --notes "baunilha,lavanda,ambar"
py main.py --catalog synthetic --size 1200 --effort 2500 --mode threading --workers 4 --notes "baunilha,lavanda,ambar"
py main.py --catalog synthetic --size 1200 --effort 2500 --mode multiprocessing --workers 4 --notes "baunilha,lavanda,ambar"
```

## Benchmark comparável
```powershell
py benchmark.py --size 1200 --effort 2500 --repeat 3
```
Aumente para `--size 3000 --effort 4000` caso sua máquina termine rápido demais. Isso aumenta **trabalho computacional real**, não atrasos artificiais. Pode demorar alguns minutos. Para demonstrar ganho com processos, use vários núcleos de CPU livres; **não há garantia de speedup**, sobretudo no Windows (inicialização de processos) ou com poucos núcleos.

## Distribuído
### Biblioteca e protocolo utilizados
O modo distribuído é implementado **somente com a biblioteca padrão do
Python** — não é necessária nenhuma dependência externa ou instalação via
`pip`.

- `socket`: o coordenador abre conexões TCP com cada worker usando
  `socket.create_connection` e aplica o timeout configurado.
- `socketserver`: cada worker executa um `ThreadingTCPServer`, permitindo que
  mais de uma requisição seja atendida simultaneamente.
- `json` e `struct`: mensagens UTF-8 são serializadas em JSON e recebem um
  cabeçalho de 4 bytes com o tamanho da mensagem. Isso permite delimitar cada
  mensagem corretamente no fluxo TCP.

O coordenador divide o catálogo em lotes, envia um lote a cada servidor e
reúne o ranking ao final. Cada mensagem inclui a versão (hash) do catálogo;
respostas com versão diferente são rejeitadas. Se houver timeout, conexão
recusada ou erro de protocolo, o lote correspondente é reprocessado
localmente. Consulte a documentação oficial de [`socket`](https://docs.python.org/3/library/socket.html)
e [`socketserver`](https://docs.python.org/3/library/socketserver.html) para
mais detalhes sobre essas APIs.

> Segurança: os servidores locais usam TCP sem autenticação ou criptografia.
> Mantenha o host padrão `127.0.0.1` e não exponha essas portas à internet.

Em três terminais separados:
```powershell
py server.py --port 9001
py server.py --port 9002
py server.py --port 9003
```
Em um quarto terminal:
```powershell
py benchmark.py --size 1200 --effort 2500 --repeat 3 --distributed --timeout 30
```
Para uma consulta pontual:
```powershell
py main.py --catalog synthetic --size 1200 --effort 2500 --mode distributed --timeout 30 --notes "baunilha,lavanda,ambar"
```

## Falha de servidor: demonstração 1 (conexão recusada)
Desligue o servidor da porta 9002 com Ctrl+C, mantendo os outros ligados. Execute a consulta distribuída. Observe `AVISO: lote 1 recuperado localmente`. O tempo depende do trabalho de CPU e da conexão; falha imediata não implica espera longa.

## Falha de servidor: demonstração 2 (timeout visível)
Reinicie o servidor 9002 com `py server.py --port 9002 --delay-response 4`. No coordenador, execute:
```powershell
py main.py --catalog synthetic --size 300 --effort 500 --mode distributed --timeout 1 --notes "baunilha,lavanda,ambar"
```
O servidor 9002 atrasa a resposta intencionalmente por **4 s (simulação de lentidão de rede/servidor)**. O coordenador aguarda até **1 s**, registra timeout e recupera o lote localmente. O atraso visível **não é ganho/perda de desempenho real** e NÃO deve ser misturado aos benchmarks normais.

## Interpretação honesta
- A carga aritmética é uma simulação de análise intensiva, não IA treinada nem recomendação olfativa cientificamente validada.
- `threading` no CPython tradicional pode não acelerar cálculos CPU-bound devido ao GIL.
- `multiprocessing` usa múltiplos processos e pode acelerar com carga suficiente, mas a criação e serialização custam tempo.
- Três servidores locais compartilham a mesma CPU; não equivalem a três máquinas físicas.
- A mesma pontuação e a mesma assinatura de cálculo são verificadas pelo benchmark em todos os modos.
- Para ter speedup verdadeiro, meça e compare os tempos; nunca atribua um valor antes da execução.
- O protocolo TCP é local e sem autenticação: não exponha os servidores à internet.

## Testes
```powershell
py -m unittest discover -s tests -v
```

## Estrutura
`main.py`: recomendador; `benchmark.py`: testes; `server.py`: worker TCP; `scentmatch/catalog.py`: gerador robusto; `scentmatch/core.py`: pontuação e CPU; `scentmatch/execution.py`: threads/processos; `scentmatch/distributed.py`: TCP/fallback.
