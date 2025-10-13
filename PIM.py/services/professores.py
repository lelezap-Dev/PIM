# ======= services/professores.py =======
import json, os
from services.usuarios import carregar_usuarios, salvar_usuarios
from services.quiz import carregar_resultados
from services.conteudos import carregar_conteudos
from services.leitura import carregar_leituras

# Helpers para persistência
def carregar_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def salvar_json(path, dados):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

# Materias (disciplinas)
def carregar_materias():
    return carregar_json('data/materias.json')

def salvar_materias(materias):
    salvar_json('data/materias.json', materias)

def criar_materia(professor_cpf=None):
    materias = carregar_materias()
    nome = input('Nome da matéria: ').strip()
    if not nome:
        print('Nome inválido.')
        return
    if any(m['nome'].lower() == nome.lower() for m in materias):
        print('Matéria já existe.')
        return
    materias.append({'nome': nome, 'professor_cpf': professor_cpf})
    salvar_materias(materias)
    print('Matéria criada com sucesso!')

# Turmas
def carregar_turmas():
    return carregar_json('data/turmas.json')

def salvar_turmas(turmas):
    salvar_json('data/turmas.json', turmas)

def criar_turma(professor_cpf):
    turmas = carregar_turmas()
    materias = carregar_materias()
    if not materias:
        print('Não há matérias cadastradas. Professor deve criar uma matéria primeiro.')
        return
    print('Matérias disponíveis:')
    for i, m in enumerate(materias, 1):
        print(f"{i}. {m['nome']}")
    try:
        escolha = int(input('Escolha a matéria por número: ')) - 1
    except:
        print('Entrada inválida.')
        return
    if escolha < 0 or escolha >= len(materias):
        print('Opção inválida.')
        return
    materia = materias[escolha]['nome']
    codigo = input('Código da turma (ex: TURMA001): ').strip()
    horario = input('Horário da turma (ex: Segunda 10:00-12:00): ').strip()
    # Verificar conflito de horário para o professor
    for t in turmas:
        if t['professor_cpf'] == professor_cpf and t['horario'] == horario:
            print('Conflito: você já tem uma turma nesse horário.')
            return
    turmas.append({
        'codigo': codigo,
        'materia': materia,
        'professor_cpf': professor_cpf,
        'horario': horario,
        'alunos': []
    })
    salvar_turmas(turmas)
    print('Turma criada com sucesso!')

def listar_turmas_professor(professor_cpf):
    turmas = carregar_turmas()
    minhas = [t for t in turmas if t['professor_cpf'] == professor_cpf]
    if not minhas:
        print('Você não tem turmas cadastradas.')
        return
    for i, t in enumerate(minhas, 1):
        print(f"{i}. {t['codigo']} | {t['materia']} | {t['horario']} | Alunos: {len(t['alunos'])}")

# Matrícula de aluno em turma (respeitando conflitos de horário)
def matricular_aluno_em_turma():
    turmas = carregar_turmas()
    usuarios = carregar_usuarios()
    cpf_aluno = input('CPF do aluno a matricular: ')
    aluno = next((u for u in usuarios if u['cpf'] == cpf_aluno and u['perfil'] == 'Aluno'), None)
    if not aluno:
        print('Aluno não encontrado ou não é perfil Aluno.')
        return
    if not turmas:
        print('Nenhuma turma disponível.')
        return
    print('Turmas disponíveis:')
    for i, t in enumerate(turmas, 1):
        print(f"{i}. {t['codigo']} | {t['materia']} | {t['horario']}")
    try:
        escolha = int(input('Escolha a turma por número: ')) - 1
    except:
        print('Entrada inválida.')
        return
    if escolha < 0 or escolha >= len(turmas):
        print('Opção inválida.')
        return
    turma = turmas[escolha]
    # Verificar se aluno já tem turma no mesmo horário
    for t in turmas:
        if cpf_aluno in t.get('alunos', []) and t['horario'] == turma['horario']:
            print('Conflito: aluno já matriculado em outra turma nesse horário.')
            return
    if cpf_aluno in turma['alunos']:
        print('Aluno já matriculado nessa turma.')
        return
    turma['alunos'].append(cpf_aluno)
    salvar_turmas(turmas)
    print('Aluno matriculado com sucesso!')

# Atividades / Questionários
def carregar_atividades():
    return carregar_json('data/atividades.json')

def salvar_atividades(atividades):
    salvar_json('data/atividades.json', atividades)

def criar_atividade(professor_cpf):
    materias = carregar_materias()
    if not materias:
        print('Nenhuma matéria disponível.')
        return
    # Filtra matérias do professor (se desejar restringir)
    minhas = [m for m in materias if m.get('professor_cpf') in (None, professor_cpf, '') or m.get('professor_cpf') == professor_cpf]
    if not minhas:
        print('Você não tem matérias associadas para criar atividade.')
        return
    print('Matérias disponíveis:')
    for i, m in enumerate(minhas, 1):
        print(f"{i}. {m['nome']}")
    try:
        escolha = int(input('Escolha a matéria por número: ')) - 1
    except:
        print('Entrada inválida.')
        return
    if escolha < 0 or escolha >= len(minhas):
        print('Opção inválida.')
        return
    materia = minhas[escolha]['nome']
    titulo = input('Título da atividade: ').strip()
    perguntas = []
    while True:
        pergunta = input('Digite uma pergunta (ou Enter para finalizar): ').strip()
        if not pergunta:
            break
        resposta = input('Resposta correta: ').strip()
        alternativas = [resposta]
        for i in range(3):
            alt = input(f'Digite outra alternativa ({i+1}/3): ').strip()
            alternativas.append(alt)
        perguntas.append({'pergunta': pergunta, 'resposta_correta': resposta, 'alternativas': alternativas})
    if not perguntas:
        print('Atividade precisa ter pelo menos uma pergunta.')
        return
    atividades = carregar_atividades()
    atividades.append({'materia': materia, 'titulo': titulo, 'perguntas': perguntas, 'professor_cpf': professor_cpf})
    salvar_atividades(atividades)
    print('Atividade criada com sucesso!')

# Relatório de turma
def gerar_relatorio_turma(professor_cpf):
    turmas = carregar_turmas()
    resultados = carregar_resultados()
    usuarios = carregar_usuarios()
    minhas = [t for t in turmas if t['professor_cpf'] == professor_cpf]
    if not minhas:
        print('Nenhuma turma encontrada.')
        return
    for i, t in enumerate(minhas, 1):
        print(f"{i}. {t['codigo']} | {t['materia']} | {t['horario']}")
    try:
        escolha = int(input('Escolha a turma por número para gerar relatório: ')) - 1
    except:
        print('Entrada inválida.')
        return
    if escolha < 0 or escolha >= len(minhas):
        print('Opção inválida.')
        return
    turma = minhas[escolha]
    print(f"\n📋 Relatório da Turma {turma['codigo']} - {turma['materia']}")
    if not turma.get('alunos'):
        print('Nenhum aluno matriculado.')
        return
    for cpf in turma['alunos']:
        nome = next((u['nome'] for u in usuarios if u['cpf'] == cpf), cpf)
        res = [r for r in resultados if r['cpf'] == cpf]
        if not res:
            print(f"- {nome} ({cpf}): Sem registros de atividades")
            continue
        acertos = [r['acertos'] for r in res]
        print(f"- {nome} ({cpf}): Atividades: {len(res)} | Média de acertos: {round(sum(acertos)/len(acertos),2)}")
