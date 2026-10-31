import csv
import hashlib
import json
import unicodedata
from pathlib import Path
DATA=Path(__file__).resolve().parents[1]/'data'/'perfumes.csv'

def load_perfumes(path=DATA):
    with open(path,encoding='utf-8-sig',newline='') as f:
        return [{'id':int(r['id']),'nome':r['nome'],'marca':r['marca'],
                 'notas':[x.strip().lower() for x in r['notas'].split(';') if x.strip()]}
                for r in csv.DictReader(f)]

# Nomes equivalentes em portugues/ingles. Normalizacao preserva notas originais para exibicao.
ALIASES = {
    'lavanda':'lavender', 'bergamota':'bergamot', 'sandalo':'sandalwood',
    'baunilha':'vanilla', 'menta':'mint', 'hortela':'mint', 'jasmim':'jasmine',
    'rosa':'rose', 'cedro':'cedar', 'almiscar':'musk', 'ambar':'amber',
    'limao':'lemon', 'laranja':'orange', 'flor de laranjeira':'orange blossom',
    'patchuli':'patchouli', 'vetiver':'vetiver', 'iris':'iris',
    'cardamomo':'cardamom', 'canela':'cinnamon', 'couro':'leather',
    'tabaco':'tobacco', 'cafe':'coffee', 'coco':'coconut',
    'pera':'pear', 'maca':'apple', 'pessego':'peach', 'abacaxi':'pineapple',
    'mandarina':'mandarin orange', 'fava tonka':'tonka bean',
    'madeira de agar':'oud', 'oud wood':'oud', 'agarwood':'oud',
    'lavandin':'lavender', 'sandal':'sandalwood',
}

def normalize_note(value):
    value = unicodedata.normalize('NFKD', str(value).casefold().strip())
    value = ''.join(c for c in value if not unicodedata.combining(c))
    value = ' '.join(value.replace('_', ' ').replace('-', ' ').split())
    return ALIASES.get(value, value)

def matching_notes(perfume, preferences):
    wanted = {normalize_note(n) for n in preferences if str(n).strip()}
    found = {normalize_note(n) for n in perfume['notas']}
    return sorted(wanted & found)

def score(perfume, preferences):
    wanted = {normalize_note(n) for n in preferences if str(n).strip()}
    return round(100 * len(matching_notes(perfume, preferences)) / len(wanted), 2) if wanted else 0.0

def cpu_work(perfume, effort):
    """Carga aritmética REAL de CPU, determinística, sem sleep nem espera artificial.
    Simula análise intensiva de descritores. Não altera o ranking por notas.
    """
    value=(perfume['id']*2654435761)&0xffffffff
    notes=perfume['notas']
    for i in range(effort):
        note=notes[i%len(notes)]
        value=((value ^ (ord(note[i%len(note)]) + i))*1664525+1013904223)&0xffffffff
        value^=(value>>13)
    return value

def analyze_batch(batch, preferences, effort=0):
    result=[]
    for p in batch:
        digest=cpu_work(p,effort) if effort else 0
        result.append({'id':p['id'],'nome':p['nome'],'marca':p['marca'],
                       'notas':p['notas'],'pontuacao':score(p,preferences),'assinatura':digest})
    return result

def rank(results,limit=5):
    return sorted(results,key=lambda r:(-r['pontuacao'],r['id']))[:limit]

def partition(data,n):
    return [data[i::n] for i in range(max(1,n))]

def fingerprint(data):
    return hashlib.sha256(json.dumps(data,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
