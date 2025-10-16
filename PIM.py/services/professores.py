# services/professores.py
import json
import os
import uuid
from datetime import datetime
from services.usuarios import carregar_usuarios
from services.leitura import registrar_leitura, ja_visualizou_conteudo

# -----------------------
# Helpers para JSON
# -----------------------
def _carregar(arquivo):
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def _salvar(arquivo, dados):
    os.makedirs('data', exist_ok=True)
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

# -----------------------
# Matérias (CRUD)
# -----------------------
MATERIAS_FILE = 'data/materias.json'
TURMAS_FILE = 'data/turmas.json'
ATIVIDADES_FILE = 'data/atividades.json'

def carregar_materias():
    return _carregar(MATERIAS_FILE)

def salvar_materias(materias):
    _salvar(MATERIAS_FILE, materias)

def criar_materia(professor_cpf):
    materias = carregar_materias()
    nome = input('Nome da matéria: ').strip()
    descricao = input('Descrição breve da matéria: ').strip()
    # id único
    mid = str(uuid.uuid4())[:8]
    materia = {
        "id": mid,
        "professor_cpf": professor_cpf,
        "nome": nome,
        "descricao": descricao,
        "conteudos": []  # lista de conteúdos {titulo,texto}
    }
    materias.append(materia)
    salvar_materias(materias)
    print(f"✅ Matéria '{nome}' criada com ID {mid}.")

def listar_materias_professor(professor_cpf):
    materias = [m for m in carregar_materias() if m['professor_cpf'] == professor_cpf]
    if not materias:
        print("Nenhuma matéria cadastrada por você.")
        return []
    for i, m in enumerate(materias, 1):
        print(f"{i}. {m['nome']} (ID: {m['id']}) - {m['descricao']}")
    return materias

def selecionar_materia_do_professor(professor_cpf):
    materias = listar_materias_professor(professor_cpf)
    if not materias:
        return None
    try:
        escolha = int(input("Escolha o número da matéria: ")) - 1
        if escolha < 0 or escolha >= len(materias):
            print("Opção inválida.")
            return None
        return materias[escolha]
    except ValueError:
        print("Entrada inválida.")
        return None

def editar_materia(professor_cpf):
    materias = carregar_materias()
    m = selecionar_materia_do_professor(professor_cpf)
    if not m:
        return
    print(f"Editando matéria: {m['nome']}")
    novo_nome = input("Novo nome (Enter para manter): ").strip() or m['nome']
    nova_desc = input("Nova descrição (Enter para manter): ").strip() or m['descricao']
    for mm in materias:
        if mm['id'] == m['id']:
            mm['nome'] = novo_nome
            mm['descricao'] = nova_desc
            break
    salvar_materias(materias)
    print("✅ Matéria atualizada.")

def excluir_materia(professor_cpf):
    materias = carregar_materias()
    m = selecionar_materia_do_professor(professor_cpf)
    if not m:
        return
    confirm = input(f"Tem certeza que deseja excluir a matéria '{m['nome']}' e todo seu conteúdo/atividades? (s/n): ").lower()
    if confirm != 's':
        print("Exclusão cancelada.")
        return
    materias = [mm for mm in materias if mm['id'] != m['id']]
    salvar_materias(materias)

    # também remover turmas e atividades vinculadas
    turmas = carregar_turmas()
    turmas = [t for t in turmas if t['materia_id'] != m['id']]
    salvar_turmas(turmas)

    atividades = carregar_atividades()
    atividades = [a for a in atividades if a['materia_id'] != m['id']]
    salvar_atividades(atividades)

    print("✅ Matéria e itens vinculados removidos.")

# -----------------------
# Conteúdos dentro de matéria
# -----------------------
def adicionar_conteudo_na_materia(professor_cpf):
    materias = carregar_materias()
    m = selecionar_materia_do_professor(professor_cpf)
    if not m:
        return
    titulo = input("Título do conteúdo: ").strip()
    texto = input("Texto/descrição do conteúdo (pode ser curto): ").strip()
    if not titulo or not texto:
        print("Título e texto obrigatórios.")
        return
    for mm in materias:
        if mm['id'] == m['id']:
            mm['conteudos'].append({"id": str(uuid.uuid4())[:8], "titulo": titulo, "texto": texto})
            break
    salvar_materias(materias)
    print(f"✅ Conteúdo '{titulo}' adicionado à matéria '{m['nome']}'.")

def listar_conteudos_materia(materia_id):
    materias = carregar_materias()
    m = next((x for x in materias if x['id'] == materia_id), None)
    if not m:
        return []
    return m.get('conteudos', [])

# -----------------------
# Turmas (CRUD e matrícula)
# -----------------------
def carregar_turmas():
    return _carregar(TURMAS_FILE)

def salvar_turmas(turmas):
    _salvar(TURMAS_FILE, turmas)

def criar_turma(professor_cpf):
    materias = [m for m in carregar_materias() if m['professor_cpf'] == professor_cpf]
    if not materias:
        print("Você precisa criar uma matéria antes de criar turmas.")
        return
    print("Escolha a matéria para esta turma:")
    for i, m in enumerate(materias, 1):
        print(f"{i}. {m['nome']} (ID: {m['id']})")
    try:
        escolha = int(input("Escolha: ")) - 1
        if escolha < 0 or escolha >= len(materias):
            print("Opção inválida.")
            return
    except ValueError:
        print("Entrada inválida.")
        return
    materia = materias[escolha]
    codigo = input("Código da turma (ex: TURMA001): ").strip()
    horario = input("Horário (ex: Seg 10:00-12:00): ").strip()

    # checar conflito de horário para professor
    turmas = carregar_turmas()
    conflitos = [t for t in turmas if t['professor_cpf'] == professor_cpf and t['horario'] == horario]
    if conflitos:
        print("Você já tem uma turma nesse horário. Escolha outro horário.")
        return

    turma = {
        "codigo": codigo,
        "materia_id": materia['id'],
        "materia_nome": materia['nome'],
        "professor_cpf": professor_cpf,
        "horario": horario,
        "alunos": []  # lista de cpfs
    }
    turmas.append(turma)
    salvar_turmas(turmas)
    print(f"✅ Turma '{codigo}' criada para a matéria '{materia['nome']}' no horário {horario}.")

def listar_turmas_professor(professor_cpf):
    turmas = [t for t in carregar_turmas() if t['professor_cpf'] == professor_cpf]
    if not turmas:
        print("Nenhuma turma encontrada.")
        return []
    for i, t in enumerate(turmas, 1):
        print(f"{i}. {t['codigo']} - {t['materia_nome']} | {t['horario']} | Alunos: {len(t['alunos'])}")
    return turmas

def matricular_aluno_em_turma():
    turmas = carregar_turmas()
    if not turmas:
        print("Nenhuma turma disponível.")
        return
    from services.usuarios import carregar_usuarios
    usuarios = carregar_usuarios()
    cpf = input("CPF do aluno a matricular: ").strip()
    aluno = next((u for u in usuarios if u['cpf'] == cpf and u['perfil'] == 'Aluno'), None)
    if not aluno:
        print("Aluno não encontrado ou perfil não é Aluno.")
        return
    print("Turmas disponíveis:")
    for i, t in enumerate(turmas, 1):
        print(f"{i}. {t['codigo']} - {t['materia_nome']} | {t['horario']}")
    try:
        escolha = int(input("Escolha a turma: ")) - 1
        if escolha < 0 or escolha >= len(turmas):
            print("Opção inválida.")
            return
    except ValueError:
        print("Entrada inválida.")
        return
    turma = turmas[escolha]

    # verificar se aluno já tem turma em mesmo horário
    turmas_aluno = [t for t in turmas if cpf in t.get('alunos', [])]
    if any(t['horario'] == turma['horario'] for t in turmas_aluno):
        print("Aluno já está matriculado em outra turma no mesmo horário.")
        return

    if cpf not in turma['alunos']:
        turma['alunos'].append(cpf)
        salvar_turmas(turmas)
        print(f"✅ Aluno {cpf} matriculado na turma {turma['codigo']}.")
    else:
        print("Aluno já matriculado nessa turma.")

# -----------------------
# Atividades (questionários) vinculadas a matéria e/ou turma
# -----------------------
def carregar_atividades():
    return _carregar(ATIVIDADES_FILE)

def salvar_atividades(atividades):
    _salvar(ATIVIDADES_FILE, atividades)

def criar_atividade(professor_cpf):
    materias = [m for m in carregar_materias() if m['professor_cpf'] == professor_cpf]
    if not materias:
        print("Você precisa criar uma matéria antes de criar atividades.")
        return
    print("Escolha a matéria para a atividade:")
    for i, m in enumerate(materias, 1):
        print(f"{i}. {m['nome']} (ID: {m['id']})")
    try:
        escolha = int(input("Escolha: ")) - 1
        if escolha < 0 or escolha >= len(materias):
            print("Opção inválida.")
            return
    except ValueError:
        print("Entrada inválida.")
        return
    materia = materias[escolha]

    # opcional: vincular a turma específica (ou deixar aberta para todas as turmas dessa matéria)
    turmas_prof = [t for t in carregar_turmas() if t['professor_cpf'] == professor_cpf and t['materia_id'] == materia['id']]
    turma_codigo = None
    if turmas_prof:
        print("Deseja vincular a atividade a uma turma específica?")
        print("0. Não (disponível para todas as turmas desta matéria)")
        for i, tr in enumerate(turmas_prof, 1):
            print(f"{i}. {tr['codigo']} - {tr['horario']}")
        try:
            escolha_t = int(input("Escolha: "))
            if escolha_t == 0:
                turma_codigo = None
            else:
                turma_codigo = turmas_prof[escolha_t - 1]['codigo']
        except ValueError:
            turma_codigo = None

    titulo = input("Título da atividade: ").strip()
    perguntas = []
    while True:
        p = input("Digite a pergunta (ou Enter para finalizar): ").strip()
        if not p:
            break
        cor = input("Resposta correta: ").strip()
        alternativas = [cor]
        for i in range(3):
            alt = input(f"Alternativa {i+1}: ").strip()
            alternativas.append(alt)
        perguntas.append({
            "pergunta": p,
            "resposta_correta": cor,
            "alternativas": alternativas
        })

    atividade = {
        "id": str(uuid.uuid4())[:8],
        "materia_id": materia['id'],
        "materia_nome": materia['nome'],
        "turma_codigo": turma_codigo,  # None => disponível para todas as turmas da matéria
        "titulo": titulo,
        "perguntas": perguntas,
        "criada_por": professor_cpf,
        "criada_em": datetime.now().isoformat()
    }

    atividades = carregar_atividades()
    atividades.append(atividade)
    salvar_atividades(atividades)
    print(f"✅ Atividade '{titulo}' criada para a matéria '{materia['nome']}' (turma: {turma_codigo or 'todas'}).")

def listar_atividades_professor(professor_cpf):
    atividades = [a for a in carregar_atividades() if a['criada_por'] == professor_cpf]
    if not atividades:
        print("Nenhuma atividade encontrada.")
        return []
    for i, a in enumerate(atividades, 1):
        print(f"{i}. {a['titulo']} | Matéria: {a['materia_nome']} | Turma: {a['turma_codigo'] or 'Todas'}")
    return atividades

# -----------------------
# Relatório de Turma (APENAS para as matérias/turmas do professor)
# -----------------------
def gerar_relatorio_turma(professor_cpf):
    
    from services.quiz import carregar_resultados
    
    turmas = [t for t in carregar_turmas() if t['professor_cpf'] == professor_cpf]
    if not turmas:
        print("Você não possui turmas cadastradas.")
        return

    print("Suas turmas:")
    for i, t in enumerate(turmas, 1):
        print(f"{i}. {t['codigo']} - {t['materia_nome']} | {t['horario']}")

    try:
        escolha = int(input("Escolha a turma para gerar relatório: ")) - 1
        if escolha < 0 or escolha >= len(turmas):
            print("Opção inválida.")
            return
    except ValueError:
        print("Entrada inválida.")
        return
    turma = turmas[escolha]

    # Carregar resultados e filtrar por alunos desta turma e pela matéria da turma
    resultados = carregar_resultados()
    alunos_turma = set(turma.get('alunos', []))
    resultados_filtrados = [r for r in resultados if r['cpf'] in alunos_turma and r.get('conteudo_materia_id') == turma['materia_id']]

    # Se as atividades foram salvas com 'conteudo_materia_id', usamos isso; senão tentamos usar título->materia_nome
    # Agrupar por aluno
    from services.usuarios import carregar_usuarios
    usuarios = carregar_usuarios()
    cpf_to_nome = {u['cpf']: u['nome'] for u in usuarios}

    if not resultados_filtrados:
        print("Nenhum resultado encontrado para esta turma/atividade.")
        return

    print(f"\n📋 Relatório da Turma {turma['codigo']} - Matéria: {turma['materia_nome']}")
    por_aluno = {}
    for r in resultados_filtrados:
        nome = cpf_to_nome.get(r['cpf'], r['cpf'])
        if nome not in por_aluno:
            por_aluno[nome] = {'acertos': 0, 'total': 0, 'atividades': 0}
        por_aluno[nome]['acertos'] += r['acertos']
        por_aluno[nome]['total'] += r['total']
        por_aluno[nome]['atividades'] += 1

    for nome, stats in por_aluno.items():
        media = round((stats['acertos'] / stats['total']) * 10, 2) if stats['total'] > 0 else 0
        print(f"- {nome}: Atividades: {stats['atividades']} | Média (0-10): {media}")
