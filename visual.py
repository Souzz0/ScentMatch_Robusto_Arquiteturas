"""Interface demonstrativa para terminal, sem bibliotecas externas.
Copie este arquivo para a pasta do ScentMatch e execute: py visual.py
"""
import argparse
import csv
import os
import statistics
import sys
import threading
import time
from pathlib import Path

from scentmatch.catalog import catalog
from scentmatch.core import matching_notes, normalize_note
from scentmatch.execution import execute
from scentmatch.distributed import execute_distributed

COLORS = sys.stdout.isatty()
if os.name == 'nt' and COLORS:
    os.system('')  # Habilita ANSI no terminal Windows moderno

def color(s, c):
    return f'\033[{c}m{s}\033[0m' if COLORS else s

def line(ch='─', width=72):
    print(ch * width)

def header(title):
    print('\n' + color('╔' + '═' * 70 + '╗', '36'))
    print(color('║', '36') + f' {title:<69}'[:70] + color('║', '36'))
    print(color('╚' + '═' * 70 + '╝', '36'))

def label(mode):
    return {'sequential':'SEQUENCIAL', 'threading':'THREADS',
            'multiprocessing':'PROCESSOS', 'distributed':'DISTRIBUÍDO'}.get(mode, mode)

def show_result(result, elapsed, count, mode, recovered, effort, prefs):
    print('\n' + color('✔ PROCESSAMENTO CONCLUÍDO', '32'))
    line()
    print(f' Arquitetura       : {label(mode)}')
    print(f' Perfumes avaliados: {count:,}'.replace(',', '.'))
    print(f' Carga por perfume : {effort:,} iterações'.replace(',', '.'))
    print(f' Tempo total       : {color(f"{elapsed:.3f} segundos", "33")}')
    print(f' Lotes recuperados : {color(str(len(recovered)), "31" if recovered else "32")}')
    if recovered:
        print(color(' ⚠ ATENÇÃO: um servidor falhou. O coordenador recuperou o lote localmente.', '33'))
        for item in recovered:
            print(f'   Lote {item["lote"]}: {item["erro"]}')
    else:
        print(color(' ✔ Execução sem falhas detectadas.', '32'))
    print('\n' + color('🏆 TOP RECOMENDAÇÕES', '36'))
    line()
    for i, p in enumerate(result, 1):
        score = max(0, min(100, float(p['pontuacao'])))
        filled = round(score / 5)
        bar = '█' * filled + '░' * (20 - filled)
        name = f'{p["marca"]} — {p["nome"]}'
        print(f'{i:>2}. {name[:66]}')
        print(f'    {color(bar, "32" if score >= 65 else "33")} {score:5.1f}%')
        print(f'    Notas correspondentes: {", ".join(matching_notes(p, prefs)) or "nenhuma"}')
        print(f'    Notas do perfume: {", ".join(p["notas"][:8])}')
    line()

def spinner(stop):
    frames = '|/-\\'
    start = time.perf_counter()
    i = 0
    while not stop.wait(0.12):
        print(f'\r {color(frames[i % 4], "36")} Analisando perfumes... {time.perf_counter()-start:5.1f}s', end='', flush=True)
        i += 1
    print('\r' + ' ' * 65 + '\r', end='', flush=True)

def run_mode(mode, prefs, size, effort, workers, servers, timeout, top):
    data = catalog('real', size)
    print(f'\n Preferências informadas: {", ".join(prefs)}')
    print(f' Iniciando {label(mode)} com {len(data)} perfumes...')
    print(' Notas interpretadas: ' + ', '.join(dict.fromkeys(normalize_note(n) for n in prefs)))
    if mode == 'distributed':
        for i, (host, port) in enumerate(servers, 1):
            print(f'   [SERVIDOR {i}] {host}:{port} — destino configurado')
    stop = threading.Event()
    th = threading.Thread(target=spinner, args=(stop,), daemon=True)
    th.start()
    try:
        if mode == 'distributed':
            result, elapsed, recovered = execute_distributed(data, prefs, servers, top, timeout, effort)
        else:
            result, elapsed = execute(data, prefs, mode, workers, top, effort)
            recovered = []
    finally:
        stop.set()
        th.join()
    show_result(result, elapsed, len(data), mode, recovered, effort, prefs)

def show_benchmark(path):
    if not path.exists():
        print(f'\nArquivo de resultados não encontrado: {path}')
        print('Execute antes: py benchmark.py --catalog real --effort 10000 --repeat 3 --distributed --timeout 60')
        return
    with path.open('r', encoding='utf-8-sig', newline='') as f:
        rows = list(csv.DictReader(f))
    groups = {}
    for r in rows:
        mode = r.get('modo') or r.get('mode')
        n = int(r.get('executores') or r.get('workers') or 1)
        seconds = float(r.get('segundos') or r.get('seconds'))
        groups.setdefault((mode, n), []).append(seconds)
    if not groups:
        print('Nenhum resultado encontrado no CSV.'); return
    averages = {key: statistics.mean(vals) for key, vals in groups.items()}
    baseline = averages.get(('sequential', 1))
    scale = max(averages.values())
    header('COMPARAÇÃO DE DESEMPENHO — MENOR TEMPO É MELHOR')
    print(' Barras representam o tempo de execução (menor = mais rápido).\n')
    for (mode, n), avg in averages.items():
        width = max(1, round(avg / scale * 28))
        speedup = f'{baseline / avg:.2f}x' if baseline else '—'
        bar = color('█' * width, '32' if avg == min(averages.values()) else '36')
        print(f' {label(mode):<13} {n:>2}  {bar:<28} {avg:>6.3f}s  {speedup}')
    best = min(averages, key=averages.get)
    print('\n' + color(f' ★ MELHOR RESULTADO: {label(best[0])} ({best[1]} executores) — {averages[best]:.3f}s', '32'))
    if baseline:
        print(f'   Aceleração em relação ao sequencial: {baseline / averages[best]:.2f} vezes')
    print('   Fonte: medições registradas no arquivo CSV (não simuladas).')
    line()

def main():
    p = argparse.ArgumentParser(description='ScentMatch — interface visual de terminal')
    p.add_argument('--mode', choices=['sequential','threading','multiprocessing','distributed'])
    p.add_argument('--notes', default=None, help='Notas iniciais; sem esta opção, solicita notas no terminal')
    p.add_argument('--workers', type=int, default=4)
    p.add_argument('--size', type=int, default=1000)
    p.add_argument('--effort', type=int, default=10000)
    p.add_argument('--timeout', type=float, default=60)
    p.add_argument('--top', type=int, default=5)
    p.add_argument('--servers', default='127.0.0.1:9001,127.0.0.1:9002,127.0.0.1:9003')
    p.add_argument('--benchmark', default='resultados_benchmark_robusto.csv')
    a = p.parse_args()
    if not 0 <= a.effort <= 200000 or a.workers < 1 or a.size < 1 or a.top < 1 or a.timeout <= 0:
        p.error('Parâmetros numéricos inválidos')
    try:
        servers = [(host, int(port)) for host, port in (s.strip().rsplit(':', 1) for s in a.servers.split(','))]
    except ValueError:
        p.error('Use --servers host:porta,host:porta')
    def pedir_notas():
        while True:
            entrada = input('\n Digite suas notas favoritas (separadas por vírgula): ').strip()
            notas = list(dict.fromkeys(n.strip().casefold() for n in entrada.split(',') if n.strip()))
            if notas:
                print(' Notas escolhidas: ' + ', '.join(notas))
                return notas
            print(color(' Informe pelo menos uma nota. Exemplo: baunilha, lavanda, menta', '33'))

    prefs_iniciais = [n.strip().casefold() for n in a.notes.split(',') if n.strip()] if a.notes is not None else None
    if a.notes is not None and not prefs_iniciais:
        p.error('Informe ao menos uma nota em --notes')
    header('SCENTMATCH | DEMONSTRAÇÃO VISUAL')
    print(' 1 — Recomendação sequencial')
    print(' 2 — Paralelismo com threads')
    print(' 3 — Paralelismo com processos')
    print(' 4 — Distribuído (servidores TCP)')
    print(' 5 — Gráfico de benchmark')
    print(' 0 — Sair')
    mapping = {'1':'sequential','2':'threading','3':'multiprocessing','4':'distributed'}
    if a.mode:
        prefs = prefs_iniciais if prefs_iniciais is not None else pedir_notas()
        run_mode(a.mode, prefs, a.size, a.effort, a.workers, servers, a.timeout, a.top)
        return
    while True:
        choice = input('\n Escolha uma opção [0-5]: ').strip()
        if choice == '0':
            print('Até a próxima!'); return
        if choice == '5':
            show_benchmark(Path(a.benchmark)); continue
        if choice in mapping:
            try:
                prefs = pedir_notas()
                run_mode(mapping[choice], prefs, a.size, a.effort, a.workers, servers, a.timeout, a.top)
            except (OSError, ValueError, RuntimeError, FileNotFoundError) as exc:
                print(color(f' ERRO: {exc}', '31'))
        else:
            print('Escolha 0, 1, 2, 3, 4 ou 5.')

if __name__ == '__main__':
    main()
