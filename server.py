import argparse
import socketserver
import time
from scentmatch.core import analyze_batch
from scentmatch.protocol import recv_message,send_message

class Handler(socketserver.BaseRequestHandler):
    def handle(self):
        try:
            self.request.settimeout(60)
            request=recv_message(self.request)
            if request.get('action')!='analyze': raise ValueError('Ação inválida')
            batch=request['batch']; preferences=request['preferences']; version=request['version']
            effort=int(request.get('effort',0))
            if not isinstance(batch,list) or not isinstance(preferences,list) or not 0<=effort<=200000:
                raise ValueError('Dados inválidos')
            print(f'[{self.server.server_address[1]}] Recebido lote: {len(batch)} perfumes; esforço={effort}',flush=True)
            results=analyze_batch(batch,preferences,effort)
            if self.server.delay_response:
                print(f'[{self.server.server_address[1]}] SIMULAÇÃO: resposta atrasada {self.server.delay_response}s',flush=True)
                time.sleep(self.server.delay_response)
            send_message(self.request,{'ok':True,'version':version,'results':results})
            print(f'[{self.server.server_address[1]}] Lote respondido',flush=True)
        except (OSError,ValueError,KeyError,TypeError,ConnectionError) as exc:
            print(f'[{self.server.server_address[1]}] Erro: {exc}',flush=True)
            try:send_message(self.request,{'ok':False,'error':str(exc)})
            except OSError:pass
class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address=True
    daemon_threads=True

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--host',default='127.0.0.1');p.add_argument('--port',type=int,default=9001)
    p.add_argument('--delay-response',type=float,default=0,help='Simula servidor lento APENAS no teste de falha')
    a=p.parse_args()
    if a.delay_response<0:p.error('Atraso não pode ser negativo')
    with Server((a.host,a.port),Handler) as server:
        server.delay_response=a.delay_response
        print(f'Servidor ativo em {a.host}:{a.port}',flush=True)
        try:server.serve_forever()
        except KeyboardInterrupt:pass
