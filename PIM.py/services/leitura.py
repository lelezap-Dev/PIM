import json
import os

LEITURA_FILE = 'data/leitura_conteudos.json'

# -----------------------
# Funções auxiliares
# -----------------------
def carregar_leituras():
    try:
        with open(LEITURA_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    except:
        return []

def salvar_leituras(leituras):
    os.makedirs('data', exist_ok=True)
    with open(LEITURA_FILE, 'w', encoding='utf-8') as file:
        json.dump(leituras, file, indent=4, ensure_ascii=False)

# -----------------------
# Registrar leitura
# -----------------------
def registrar_leitura(cpf, materia_id, conteudo):
    leituras = carregar_leituras()

    # Verifica se já existe um registro desse aluno/matéria
    registro = next((r for r in leituras if r['cpf'] == cpf and r['materia_id'] == materia_id), None)

    if not registro:
        leituras.append({
            "cpf": cpf,
            "materia_id": materia_id,
            "conteudos_vistos": [conteudo]
        })
    else:
        if conteudo not in registro['conteudos_vistos']:
            registro['conteudos_vistos'].append(conteudo)

    salvar_leituras(leituras)

# -----------------------
# Verificar leitura
# -----------------------
def ja_visualizou_conteudo(cpf, materia_id, titulo):
    leituras = carregar_leituras()
    return any(
        l['cpf'] == cpf and l['materia_id'] == materia_id and titulo in l['conteudos_vistos']
        for l in leituras
    )
