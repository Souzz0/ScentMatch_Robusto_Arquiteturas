"""Baixa catálogo público Scento e seleciona 1000 perfumes reais com notas."""
import csv
import io
import json
import urllib.request
from pathlib import Path

SOURCE = 'https://raw.githubusercontent.com/Scento-com/perfume-dataset/main/perfumes.csv'
DEST = Path(__file__).resolve().parent / 'data' / 'perfumes_1000_reais.csv'

def importar():
    req = urllib.request.Request(SOURCE, headers={'User-Agent':'ScentMatch-Academic/1.0'})
    with urllib.request.urlopen(req, timeout=45) as response:
        content=response.read().decode('utf-8-sig')
    reader=csv.DictReader(io.StringIO(content))
    required={'name','house','notes','url'}
    if not required.issubset(set(reader.fieldnames or [])):
        raise ValueError('O esquema da base pública mudou: '+str(reader.fieldnames))
    selected=[];seen=set()
    for row in reader:
        name=(row.get('name') or '').strip()
        house=(row.get('house') or '').strip()
        notes=[n.strip() for n in (row.get('notes') or '').split(';') if n.strip()]
        key=(house.casefold(),name.casefold())
        if not name or not house or not notes or key in seen:continue
        seen.add(key)
        selected.append({'id':len(selected)+1,'nome':name,'marca':house,
          'notas':';'.join(notes),'notas_saida':row.get('top_notes',''),
          'notas_coracao':row.get('heart_notes',''),'notas_fundo':row.get('base_notes',''),
          'familia':row.get('family',''),'url_fonte':row.get('url','')})
        if len(selected)==1000:break
    if len(selected)<1000:
        raise RuntimeError(f'Base contém somente {len(selected)} perfumes únicos com notas; nenhum arquivo foi substituído.')
    DEST.parent.mkdir(parents=True,exist_ok=True)
    with DEST.open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(selected[0]))
        writer.writeheader();writer.writerows(selected)
    print(f'SUCESSO: {len(selected)} perfumes reais com notas gravados em {DEST}')
    print('Fonte: Scento — https://www.scento.com/perfume-database (CC BY 4.0)')

if __name__=='__main__':
    try: importar()
    except Exception as e:
        print(f'ERRO AO IMPORTAR: {e}')
        raise SystemExit(1)
