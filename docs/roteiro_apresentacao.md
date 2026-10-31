# Roteiro de apresentação — ScentMatch

1. **Problema:** encontrar perfumes a partir de notas favoritas.
2. **Algoritmo:** proporção de notas selecionadas encontradas; ranking Top 5.
3. **Arquitetura sequencial:** um executor percorre toda a base.
4. **Arquitetura paralela:** tarefas independentes em lotes; threads e processos; resultados locais e agregação.
5. **Sincronização:** futuros aguardados antes de montar o ranking; sem contador global compartilhado.
6. **Arquitetura distribuída:** coordenador, servidores TCP, mensagens JSON, partição de dados e versão da base.
7. **Falha:** desligar um servidor, mostrar timeout/conexão recusada e reprocessamento local do lote.
8. **Consistência:** os mesmos registros são enviados com a requisição e todos os lotes usam o mesmo snapshot; comparar ranking com sequencial.
9. **Experimentos:** executar `benchmark.py` com a mesma base e preferências; comparar 1, 2, 4 e 8 executores e 1, 2 e 3 servidores. Registrar tempos reais em CSV.
10. **Conclusão:** calcular speedup = tempo sequencial / tempo paralelo; explicar overhead de threads, processos e rede. Não presumir aceleração.

**Demonstração sugerida:** primeiro rodar testes unitários; depois mostrar modos sequencial, threading, multiprocessing, distribuído e simulação de falha. Inserir capturas dos resultados reais do seu computador nos slides.
