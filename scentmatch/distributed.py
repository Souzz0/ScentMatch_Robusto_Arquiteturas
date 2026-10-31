import socket
from concurrent.futures import ThreadPoolExecutor,as_completed
from time import perf_counter
from .core import analyze_batch,fingerprint,partition,rank
from .protocol import send_message,recv_message

def remote_batch(host,port,batch,preferences,version,timeout=3,effort=0):
    with socket.create_connection((host,port),timeout=timeout) as sock:
        sock.settimeout(timeout)
        send_message(sock,{'action':'analyze','batch':batch,'preferences':preferences,
                           'version':version,'effort':effort})
        response=recv_message(sock)
        if not response.get('ok') or response.get('version')!=version:
            raise RuntimeError(response.get('error','Versão incompatível'))
        return response['results']

def execute_distributed(perfumes,preferences,servers,top=5,timeout=3,effort=0):
    if not servers: raise ValueError('Informe ao menos um servidor')
    start=perf_counter()
    version=fingerprint(perfumes)
    batches=partition(perfumes,len(servers))
    results=[];recovered=[]
    with ThreadPoolExecutor(max_workers=len(servers)) as pool:
        jobs={pool.submit(remote_batch,host,port,batch,preferences,version,timeout,effort):(i,batch)
              for i,((host,port),batch) in enumerate(zip(servers,batches))}
        for future in as_completed(jobs):
            i,batch=jobs[future]
            try: results.extend(future.result())
            except (OSError,ValueError,RuntimeError,ConnectionError) as exc:
                results.extend(analyze_batch(batch,preferences,effort))
                recovered.append({'lote':i,'erro':str(exc),'recuperacao':'processamento local'})
    return rank(results,top),perf_counter()-start,recovered
