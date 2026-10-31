"""Catálogo sintético reproduzível, SEM atribuir combinações inventadas a marcas reais."""
import random
from .core import load_perfumes

FAMILIAS = {
    'citrico': ['bergamota','limão','mandarina','toranja','laranja','neroli','petitgrain'],
    'floral': ['rosa','jasmim','lavanda','iris','tuberosa','violeta','flor de laranjeira'],
    'amadeirado': ['cedro','sândalo','vetiver','patchouli','guaiaco','cipreste'],
    'oriental': ['baunilha','ambar','almíscar','fava tonka','canela','cardamomo','incenso'],
    'fresco': ['menta','alecrim','notas marinhas','chá verde','manjericão','ozonico'],
    'gourmand': ['cafe','cacau','praline','caramelo','mel','amendoa','coco'],
    'frutado': ['pera','maçã','pêssego','groselha','framboesa','abacaxi'],
}

def generate_catalog(size=1200, seed=42):
    """Cria perfumes simulados, com 6-12 notas e famílias variadas."""
    if size < 1: raise ValueError('size deve ser positivo')
    rng = random.Random(seed)
    familias=list(FAMILIAS)
    catalog=[]
    for i in range(size):
        fam=rng.choice(familias)
        base=rng.sample(FAMILIAS[fam], k=min(4,len(FAMILIAS[fam])))
        extras=rng.sample([n for f,notes in FAMILIAS.items() for n in notes if n not in base],rng.randint(2,8))
        catalog.append({'id':i+100000,'nome':f'Formula experimental {i+1:06d}',
                        'marca':'CATALOGO SINTETICO', 'familia':fam,'notas':base+extras})
    return catalog

def catalog(kind='real', size=1200):
    if kind=='real':
        from pathlib import Path
        data=Path(__file__).resolve().parents[1]/'data'/'perfumes_1000_reais.csv'
        if not data.exists():
            raise FileNotFoundError('Base de 1000 perfumes ainda não instalada. Execute: py importar_1000_reais.py')
        perfumes=load_perfumes(data)
        if len(perfumes)!=1000: raise ValueError('Esperados exatamente 1000 perfumes reais')
        return perfumes
    if kind=='synthetic': return generate_catalog(size)
    raise ValueError('Catálogo desconhecido')
