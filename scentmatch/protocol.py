import json
import struct
MAX_MESSAGE = 20_000_000

def send_message(sock, obj):
    data = json.dumps(obj, ensure_ascii=False).encode('utf-8')
    if len(data) > MAX_MESSAGE:
        raise ValueError('Mensagem grande demais')
    sock.sendall(struct.pack('!I', len(data)) + data)

def recv_exact(sock, n):
    data = bytearray()
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            raise ConnectionError('Conexão encerrada')
        data.extend(chunk)
    return bytes(data)

def recv_message(sock):
    size = struct.unpack('!I', recv_exact(sock, 4))[0]
    if size > MAX_MESSAGE:
        raise ValueError('Mensagem grande demais')
    return json.loads(recv_exact(sock, size))
