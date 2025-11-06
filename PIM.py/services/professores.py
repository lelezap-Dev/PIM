# services/professores.py
import json
import os
import uuid
import time

DATA_DIR = 'data'
MATERIAS_FILE = os.path.join(DATA_DIR, 'materias.json')
TURMAS_FILE = os.path.join(DATA_DIR, 'turmas.json')
ATIVIDADES_FILE = os.path.join(DATA_DIR, 'atividades.json')

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
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

# -----------------------
# Materias CRUD
# -----------------------
def carregar_materias():
    return _carregar(MATERIAS_FILE)

def salvar_materias(materias):
    _salvar(MATERIAS_FILE, materias)

def criar_materia(professor_cpf):
    materias = carregar_materias()
    nome = input('Nome da matéria: ').strip()
    if not nome:
        print("Nome inválido. Operação cancelada.")
        return
    # evitar duplicata do mesmo professor
    if any(m['nome'].lower() == nome.lower() and m.get('professor_cpf') == professor_cpf for m in materias):
        print("Você já possui uma matéria com esse nome.")
        return
    descricao = input('Descrição breve da matéria: ').strip()
    mid = str(uuid.uuid4())[:8]
    materia = {
        "id": mid,
        "professor_cpf": professor_cpf,
        "nome": nome,
        "descricao": descricao,
        "conteudos": []
    }
    materias.append(materia)
    salvar_materias(materias)
    print(f"✅ Matéria '{nome}' criada com sucesso (ID: {mid}).")
    time.sleep(0.8)

def listar_materias_professor(professor_cpf):
    materias = [m for m in carregar_materias() if m.get('professor_cpf') == professor_cpf]
    if not materias:
        print("Nenhuma matéria cadastrada por você.")
        return []
    print("\n📚 Suas matérias:")
    for i, m in enumerate(materias, 1):
        print(f"{i}. {m.get('nome')} (ID: {m.get('id')}) - {m.get('descricao','')}")
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
def editar_conteudo_da_materia(professor_cpf):
    materias = carregar_materias()
    m = selecionar_materia_do_professor(professor_cpf)
    if not m:
        return
    
    if not m.get("conteudos"):
        print("Essa matéria ainda não possui conteúdos.")
        return

    print(f"\nConteúdos disponíveis em '{m['nome']}':")
    for i, c in enumerate(m["conteudos"], 1):
        print(f"{i}. {c['titulo']}")

    try:
        escolha = int(input("Escolha o número do conteúdo que deseja editar: ")) - 1
        if escolha < 0 or escolha >= len(m["conteudos"]):
            print("Opção inválida.")
            return
    except ValueError:
        print("Entrada inválida.")
        return

    conteudo = m["conteudos"][escolha]
    print(f"\nEditando conteúdo: {conteudo['titulo']}")
    novo_titulo = input(f"Novo título (Enter para manter): ").strip() or conteudo["titulo"]
    novo_texto = input(f"Novo texto (Enter para manter): ").strip() or conteudo["texto"]

    # Atualiza o conteúdo na lista
    for mm in materias:
        if mm["id"] == m["id"]:
            for c in mm["conteudos"]:
                if c["id"] == conteudo["id"]:
                    c["titulo"] = novo_titulo
                    c["texto"] = novo_texto
                    break
            break

    salvar_materias(materias)
    print("✅ Conteúdo atualizado com sucesso.")

def deletar_conteudo_da_materia(professor_cpf):
    materias = carregar_materias()
    m = selecionar_materia_do_professor(professor_cpf)
    if not m:
        return
    
    if not m.get("conteudos"):
        print("Essa matéria ainda não possui conteúdos.")
        return

    print(f"\nConteúdos disponíveis em '{m['nome']}':")
    for i, c in enumerate(m["conteudos"], 1):
        print(f"{i}. {c['titulo']}")

    try:
        escolha = int(input("Escolha o número do conteúdo que deseja excluir: ")) - 1
        if escolha < 0 or escolha >= len(m["conteudos"]):
            print("Opção inválida.")
            return
    except ValueError:
        print("Entrada inválida.")
        return

    conteudo = m["conteudos"][escolha]
    confirmar = input(f"Tem certeza que deseja excluir o conteúdo '{conteudo['titulo']}'? (s/n): ").lower()
    if confirmar != 's':
        print("Exclusão cancelada.")
        return

    # Remove o conteúdo
    for mm in materias:
        if mm["id"] == m["id"]:
            mm["conteudos"] = [c for c in mm["conteudos"] if c["id"] != conteudo["id"]]
            break

    salvar_materias(materias)
    print("✅ Conteúdo excluído com sucesso.")

def adicionar_conteudo_na_materia(professor_cpf):
    materias = carregar_materias()
    m = selecionar_materia_do_professor(professor_cpf)
    if not m:
        return
    titulo = input("Título do conteúdo: ").strip()
    texto = input("Texto/descrição do conteúdo: ").strip()
    if not titulo or not texto:
        print("Título e texto são obrigatórios.")
        return
    # gera id de conteúdo
    cid = str(uuid.uuid4())[:8]
    for mm in materias:
        if mm['id'] == m['id']:
            mm.setdefault('conteudos', []).append({"id": cid, "titulo": titulo, "texto": texto})
            break
    salvar_materias(materias)
    print(f"✅ Conteúdo '{titulo}' adicionado à matéria '{m['nome']}'.")
    time.sleep(0.6)

def listar_conteudos_materia(materia_id):
    materias = carregar_materias()
    m = next((x for x in materias if x.get('id') == materia_id), None)
    if not m:
        return []
    return m.get('conteudos', [])

def editar_materia(professor_cpf):
    materias = carregar_materias()
    m = selecionar_materia_do_professor(professor_cpf)
    if not m:
        return
    print(f"Editando matéria: {m['nome']}")
    novo_nome = input("Novo nome (Enter para manter): ").strip() or m['nome']
    nova_desc = input("Nova descrição (Enter para manter): ").strip() or m.get('descricao', '')
    for mm in materias:
        if mm['id'] == m['id']:
            mm['nome'] = novo_nome
            mm['descricao'] = nova_desc
            break
    salvar_materias(materias)
    print("✅ Matéria atualizada.")
    time.sleep(0.6)

def excluir_materia(professor_cpf):
    materias = carregar_materias()
    m = selecionar_materia_do_professor(professor_cpf)
    if not m:
        return
    # checar se existe turma vinculada a essa materia
    turmas = carregar_turmas()
    vinculadas = [t for t in turmas if t.get('materia_id') == m['id']]
    if vinculadas:
        print("Não é possível excluir a matéria: existem turmas vinculadas a ela. Remova ou migre as turmas primeiro.")
        return
    confirm = input(f"Tem certeza que deseja excluir a matéria '{m['nome']}'? (s/n): ").lower()
    if confirm != 's':
        print("Exclusão cancelada.")
        return
    materias = [mm for mm in materias if mm['id'] != m['id']]
    salvar_materias(materias)
    print("✅ Matéria excluída com sucesso.")
    time.sleep(0.6)

# -----------------------
# Turmas CRUD
# -----------------------
def carregar_turmas():
    return _carregar(TURMAS_FILE)

def salvar_turmas(turmas):
    _salvar(TURMAS_FILE, turmas)

def criar_turma(professor_cpf):
    materias = [m for m in carregar_materias() if m.get('professor_cpf') == professor_cpf]
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
    if not codigo:
        print("Código inválido.")
        return
    horario = input("Horário (ex: Seg 10:00-12:00): ").strip()
    if not horario:
        print("Horário inválido.")
        return

    # checar conflito de horário para professor
    turmas = carregar_turmas()
    conflitos = [t for t in turmas if t.get('professor_cpf') == professor_cpf and t.get('horario') == horario]
    if conflitos:
        print("Você já possui uma turma nesse horário. Escolha outro horário.")
        return

    turma = {
        "codigo": codigo,
        "materia_id": materia['id'],
        "materia_nome": materia['nome'],
        "professor_cpf": professor_cpf,
        "horario": horario,
        "alunos": []
    }
    turmas.append(turma)
    salvar_turmas(turmas)
    print(f"✅ Turma '{codigo}' criada para a matéria '{materia['nome']}' no horário {horario}.")
    time.sleep(0.6)

def listar_turmas_professor(professor_cpf):
    turmas = [t for t in carregar_turmas() if t.get('professor_cpf') == professor_cpf]
    if not turmas:
        print("Nenhuma turma encontrada.")
        return []
    print("\n🏫 Suas turmas:")
    for i, t in enumerate(turmas, 1):
        materia_nome = t.get('materia_nome') or 'N/A'
        horario = t.get('horario', 'Horário não definido')
        alunos = len(t.get('alunos', []))
        print(f"{i}. {t.get('codigo', 'Sem código')} - {materia_nome} | {horario} | Alunos: {alunos}")
    return turmas

def selecionar_turma_do_professor(professor_cpf):
    turmas = listar_turmas_professor(professor_cpf)
    if not turmas:
        return None
    try:
        escolha = int(input("Escolha o número da turma: ")) - 1
        if escolha < 0 or escolha >= len(turmas):
            print("Opção inválida.")
            return None
        return turmas[escolha]
    except ValueError:
        print("Entrada inválida.")
        return None

def editar_turma(professor_cpf):
    """
    Permite ao professor editar apenas suas próprias turmas,
    sem poder alterar o professor responsável.
    """
    turmas = carregar_turmas()
    minhas_turmas = [t for t in turmas if t.get('professor_cpf') == professor_cpf]

    if not minhas_turmas:
        print("Você ainda não possui turmas cadastradas.")
        input("\nAperte Enter para voltar.")
        return

    print("\n--- Editar Turma ---")
    for i, t in enumerate(minhas_turmas, 1):
        print(f"{i}. {t['codigo']} - {t['materia_nome']} | {t['horario']}")
    
    try:
        escolha = int(input("Escolha a turma que deseja editar: ")) - 1
        if escolha < 0 or escolha >= len(minhas_turmas):
            print("Opção inválida.")
            return
    except ValueError:
        print("Entrada inválida.")
        return

    turma = minhas_turmas[escolha]
    print(f"\nEditando turma: {turma['codigo']} - {turma['materia_nome']}")

    # Só pode editar código e horário
    novo_codigo = input(f"Novo código ({turma['codigo']}): ").strip() or turma['codigo']
    novo_horario = input(f"Novo horário ({turma['horario']}): ").strip() or turma['horario']

    # Atualiza a turma
    turma['codigo'] = novo_codigo
    turma['horario'] = novo_horario

    # Salva alterações
    salvar_turmas(turmas)
    print("✅ Turma atualizada com sucesso!")
    input("\nAperte Enter para voltar.")


def matricular_aluno_em_turma(professor_cpf=None):
    """
    Se professor_cpf fornecido, só permite matricular em turmas do professor (workflow normal).
    Se None, permite matricular em qualquer turma (útil para admin).
    """
    turmas = carregar_turmas()
    if not turmas:
        print("Nenhuma turma disponível.")
        return
    from services.usuarios import carregar_usuarios
    usuarios = carregar_usuarios()
    cpf = input("CPF do aluno a matricular: ").strip()
    aluno = next((u for u in usuarios if u.get('cpf') == cpf and u.get('perfil') == 'Aluno'), None)
    if not aluno:
        print("Aluno não encontrado ou perfil diferente de Aluno.")
        return

    # listar turmas possíveis
    possiveis = turmas
    if professor_cpf:
        possiveis = [t for t in turmas if t.get('professor_cpf') == professor_cpf]
    if not possiveis:
        print("Nenhuma turma disponível para matrícula (para este professor).")
        return

    print("Turmas disponíveis:")
    for i, t in enumerate(possiveis, 1):
        print(f"{i}. {t.get('codigo')} - {t.get('materia_nome')} | {t.get('horario')}")
    try:
        escolha = int(input("Escolha a turma: ")) - 1
        if escolha < 0 or escolha >= len(possiveis):
            print("Opção inválida.")
            return
    except ValueError:
        print("Entrada inválida.")
        return

    turma = possiveis[escolha]
    # verificar conflito de horário do aluno
    turmas_aluno = [t for t in turmas if cpf in t.get('alunos', [])]
    if any(t.get('horario') == turma.get('horario') for t in turmas_aluno):
        print("Aluno já está matriculado em outra turma no mesmo horário.")
        return

    # adicionar se não existente
    for tt in turmas:
        if tt.get('codigo') == turma.get('codigo'):
            if cpf not in tt.get('alunos', []):
                tt.setdefault('alunos', []).append(cpf)
                salvar_turmas(turmas)
                print(f"✅ Aluno {cpf} matriculado na turma {tt.get('codigo')}.")
                time.sleep(0.6)
                return
            else:
                print("Aluno já matriculado nesta turma.")
                return

def excluir_turma(professor_cpf):
    turmas = carregar_turmas()
    t = selecionar_turma_do_professor(professor_cpf)
    if not t:
        return
    confirm = input(f"Tem certeza que deseja excluir a turma '{t.get('codigo')}'? (s/n): ").lower()
    if confirm != 's':
        print("Exclusão cancelada.")
        return
    # remover
    turmas = [tt for tt in turmas if not (tt.get('codigo') == t.get('codigo') and tt.get('professor_cpf') == professor_cpf)]
    salvar_turmas(turmas)
    print("✅ Turma excluída com sucesso.")
    time.sleep(0.6)

# -----------------------
# Atividades CRUD
# -----------------------
def carregar_atividades():
    return _carregar(ATIVIDADES_FILE)

def salvar_atividades(atividades):
    _salvar(ATIVIDADES_FILE, atividades)

def criar_atividade(professor_cpf):
    materias = [m for m in carregar_materias() if m.get('professor_cpf') == professor_cpf]
    if not materias:
        print("Crie uma matéria antes de criar atividades.")
        return
    print("Escolha a matéria para a atividade:")
    for i, m in enumerate(materias, 1):
        print(f"{i}. {m.get('nome')} (ID: {m.get('id')})")
    try:
        escolha = int(input("Escolha: ")) - 1
        if escolha < 0 or escolha >= len(materias):
            print("Opção inválida.")
            return
    except ValueError:
        print("Entrada inválida.")
        return
    materia = materias[escolha]

    # opcional: vincular a uma turma específica
    turmas_prof = [t for t in carregar_turmas() if t.get('professor_cpf') == professor_cpf and t.get('materia_id') == materia.get('id')]
    turma_codigo = None
    if turmas_prof:
        print("Deseja vincular a atividade a uma turma específica?")
        print("0. Não (disponível para todas as turmas desta matéria)")
        for i, tr in enumerate(turmas_prof, 1):
            print(f"{i}. {tr.get('codigo')} - {tr.get('horario')}")
        try:
            escolha_t = int(input("Escolha: "))
            if escolha_t == 0:
                turma_codigo = None
            else:
                turma_codigo = turmas_prof[escolha_t - 1].get('codigo')
        except ValueError:
            turma_codigo = None

    titulo = input("Título da atividade: ").strip()
    if not titulo:
        print("Título inválido.")
        return
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
        "materia_id": materia.get('id'),
        "materia_nome": materia.get('nome'),
        "turma_codigo": turma_codigo,
        "titulo": titulo,
        "perguntas": perguntas,
        "criada_por": professor_cpf,
        "criada_em": time.strftime("%Y-%m-%d %H:%M:%S")

    }

    atividades = carregar_atividades()
    atividades.append(atividade)
    salvar_atividades(atividades)
    print(f"✅ Atividade '{titulo}' criada.")

def listar_atividades_professor(professor_cpf):
    atividades = [a for a in carregar_atividades() if a.get('criada_por') == professor_cpf]
    if not atividades:
        print("Nenhuma atividade encontrada.")
        return []
    print("\n🧾 Suas atividades:")
    for i, a in enumerate(atividades, 1):
        print(f"{i}. {a.get('titulo')} | Matéria: {a.get('materia_nome')} | Turma: {a.get('turma_codigo') or 'Todas'}")
    return atividades

def selecionar_atividade_do_professor(professor_cpf):
    atividades = listar_atividades_professor(professor_cpf)
    if not atividades:
        return None
    try:
        escolha = int(input("Escolha o número da atividade: ")) - 1
        if escolha < 0 or escolha >= len(atividades):
            print("Opção inválida.")
            return None
        return atividades[escolha]
    except ValueError:
        print("Entrada inválida.")
        return None

def editar_atividade(professor_cpf):
    atividades = carregar_atividades()
    a = selecionar_atividade_do_professor(professor_cpf)
    if not a:
        return
    print(f"Editando atividade: {a.get('titulo')}")
    novo_titulo = input("Novo título (Enter para manter): ").strip() or a.get('titulo')
    # editar perguntas: para simplicidade, vamos permitir re-criar o conjunto
    print("Você pode recriar as perguntas da atividade. Deixe em branco para manter as existentes.")
    novas_perguntas = []
    while True:
        p = input("Digite a pergunta (ou Enter para finalizar): ").strip()
        if not p:
            break
        cor = input("Resposta correta: ").strip()
        alternativas = [cor]
        for i in range(3):
            alt = input(f"Alternativa {i+1}: ").strip()
            alternativas.append(alt)
        novas_perguntas.append({
            "pergunta": p,
            "resposta_correta": cor,
            "alternativas": alternativas
        })
    atividades_all = carregar_atividades()
    for idx, at in enumerate(atividades_all):
        if at.get('id') == a.get('id'):
            at['titulo'] = novo_titulo
            if novas_perguntas:
                at['perguntas'] = novas_perguntas
            break
    salvar_atividades(atividades_all)
    print("✅ Atividade atualizada.")

def excluir_atividade(professor_cpf):
    atividades = carregar_atividades()
    a = selecionar_atividade_do_professor(professor_cpf)
    if not a:
        return
    confirm = input(f"Tem certeza que deseja excluir a atividade '{a.get('titulo')}'? (s/n): ").lower()
    if confirm != 's':
        print("Exclusão cancelada.")
        return
    atividades = [at for at in atividades if at.get('id') != a.get('id')]
    salvar_atividades(atividades)
    print("✅ Atividade excluída.")
