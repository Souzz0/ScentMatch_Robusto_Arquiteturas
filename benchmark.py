import argparse,csv,statistics
from pathlib import Path
from scentmatch.catalog import catalog
from scentmatch.execution import execute
from scentmatch.distributed import execute_distributed

def main():
    p=argparse.ArgumentParser(description='Benchmark real: mesmos dados, mesma carga e conferência de ranking')
    p.add_argument('--size',type=int,default=1200)
    p.add_argument('--catalog',choices=['real','synthetic'],default='real')
    p.add_argument('--effort',type=int,default=2500)
    p.add_argument('--repeat',type=int,default=3)
    p.add_argument('--distributed',action='store_true')
    p.add_argument('--timeout',type=float,default=30)
    p.add_argument('--servers',default='127.0.0.1:9001,127.0.0.1:9002,127.0.0.1:9003')
    a=p.parse_args()
    if a.size<1 or a.repeat<1 or not 0<=a.effort<=200000:p.error('Parâmetros inválidos')
    data=catalog(a.catalog,a.size);prefs=['baunilha','lavanda','ambar']
    baseline,_=execute(data,prefs,'sequential',effort=a.effort)
    records=[]
    for mode,workers in [('sequential',1)]+[(m,w) for m in ('threading','multiprocessing') for w in (2,4,8)]:
        for rep in range(1,a.repeat+1):
            got,seconds=execute(data,prefs,mode,workers,effort=a.effort)
            if got!=baseline:raise AssertionError(f'Ranking divergente: {mode}')
            records.append({'modo':mode,'executores':workers,'repeticao':rep,'segundos':seconds,'correto':True,'recuperacoes':0})
            print(mode,workers,rep,f'{seconds:.4f}s',flush=True)
    if a.distributed:
        servers=[(h,int(port)) for h,port in (e.rsplit(':',1) for e in a.servers.split(','))]
        for count in (1,2,3):
            for rep in range(1,a.repeat+1):
                got,seconds,recovered=execute_distributed(data,prefs,servers[:count],timeout=a.timeout,effort=a.effort)
                if got!=baseline:raise AssertionError('Ranking distribuído divergente')
                records.append({'modo':'distributed','executores':count,'repeticao':rep,'segundos':seconds,'correto':True,'recuperacoes':len(recovered)})
                print('distributed',count,rep,f'{seconds:.4f}s','recuperações',len(recovered),flush=True)
    path=Path('resultados_benchmark_robusto.csv')
    with path.open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
    print('\nMÉDIAS (segundos):')
    for mode,workers in dict.fromkeys((r['modo'],r['executores']) for r in records):
        vals=[r['segundos'] for r in records if (r['modo'],r['executores'])==(mode,workers)]
        print(f'{mode:16s} {workers} = {statistics.mean(vals):.4f}s')
    print('Resultados salvos em',path.resolve())
if __name__=='__main__':main()
