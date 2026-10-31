import argparse
from scentmatch.catalog import catalog
from scentmatch.execution import execute
from scentmatch.distributed import execute_distributed

def main():
    p=argparse.ArgumentParser(description='ScentMatch - recomendador e laboratório de arquitetura')
    p.add_argument('--mode',choices=['sequential','threading','multiprocessing','distributed'],default='sequential')
    p.add_argument('--workers',type=int,default=4)
    p.add_argument('--notes',default=None)
    p.add_argument('--catalog',choices=['real','synthetic'],default='real')
    p.add_argument('--size',type=int,default=1200)
    p.add_argument('--effort',type=int,default=0,help='Iterações de CPU por perfume; 0 = rápido')
    p.add_argument('--servers',default='127.0.0.1:9001,127.0.0.1:9002,127.0.0.1:9003')
    p.add_argument('--timeout',type=float,default=3)
    p.add_argument('--top',type=int,default=5)
    a=p.parse_args()
    if min(a.workers,a.size,a.top)<=0 or a.effort<0 or a.timeout<=0:p.error('Parâmetros inválidos')
    if a.effort>200000:p.error('effort máximo: 200000')
    notes=a.notes if a.notes is not None else input('Digite as notas favoritas (separadas por vírgula): ')
    prefs=[n.strip().lower() for n in notes.split(',') if n.strip()]
    if not prefs:p.error('Informe ao menos uma nota')
    perfumes=catalog(a.catalog,a.size)
    if a.mode=='distributed':
        try:servers=[(h,int(port)) for h,port in (e.rsplit(':',1) for e in a.servers.split(','))]
        except ValueError:p.error('Use --servers host:porta,host:porta')
        result,elapsed,recovered=execute_distributed(perfumes,prefs,servers,a.top,a.timeout,a.effort)
    else:
        result,elapsed=execute(perfumes,prefs,a.mode,a.workers,a.top,a.effort)
        recovered=[]
    print(f'\nModo: {a.mode} | Tempo: {elapsed:.4f}s | Perfumes: {len(perfumes)} | CPU/registro: {a.effort}')
    for i,r in enumerate(result,1):
        print(f"{i}. {r['marca']} - {r['nome']} | {r['pontuacao']:.2f}% | {', '.join(r['notas'])}")
    for rec in recovered:print(f"AVISO: lote {rec['lote']} recuperado localmente: {rec['erro']}")
    if recovered:print(f'RECUPERAÇÃO: {len(recovered)} lote(s) processados localmente.')
if __name__=='__main__':main()


