from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from time import perf_counter
from .core import analyze_batch,partition,rank

def execute(perfumes,preferences,mode='sequential',workers=4,top=5,effort=0):
    start=perf_counter()
    if mode=='sequential': results=analyze_batch(perfumes,preferences,effort)
    elif mode in ('threading','multiprocessing'):
        cls=ThreadPoolExecutor if mode=='threading' else ProcessPoolExecutor
        batches=[b for b in partition(perfumes,workers) if b]
        with cls(max_workers=workers) as pool:
            parts=list(pool.map(analyze_batch,batches,[preferences]*len(batches),[effort]*len(batches)))
        results=[r for part in parts for r in part]
    else: raise ValueError('Modo inválido')
    return rank(results,top),perf_counter()-start
