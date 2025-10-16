# services/relatorios.py
import json
import os
from statistics import mean

RESULTADOS_FILE = 'data/resultados.json'
USUARIOS_FILE = 'data/usuarios.json'
TURMAS_FILE = 'data/turmas.json'
MATERIAS_FILE = 'data/materias.json'

def carregar_json(caminho):
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def salvar_json(caminho, dados):
    os.makedirs('data', exist_ok=True)
    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

# ---------------------------------------------------------------------
# RELATÓRIO DO PROFESSOR
# ---------------------------------------------------------------------
def gerar_relatorio_turma(professor_cpf):
    from services.professores import carregar_turmas
    from services.quiz import carregar_resultados
    from services.usuarios import carregar_usuarios

    turmas = [t for t in carregar_turmas() if t['professor_cpf'] == professor_cpf]
    if not turmas:
        print("Você não possui turmas cadastradas.")
        input("\nAperte Enter para voltar.")
        return

    print("\n=== 📊 Relatórios de Turmas ===")
    for i, t in enumerate(turmas, 1):
        print(f"{i}. {t['codigo']} - {t['materia_nome']} ({t['horario']})")

    try:
        escolha = int(input("Escolha a turma: ")) - 1
        if escolha < 0 or escolha >= len(turmas):
            print("Opção inválida.")
            input("\nAperte Enter para voltar.")
            return
    except ValueError:
        print("Entrada inválida.")
        input("\nAperte Enter para voltar.")
        return

    turma = turmas[escolha]
    resultados = carregar_resultados()
    usuarios = carregar_usuarios()
    alunos_turma = set(turma.get('alunos', []))
    nome_por_cpf = {u['cpf']: u['nome'] for u in usuarios}

    resultados_filtrados = [
        r for r in resultados
        if r['cpf'] in alunos_turma and r.get('conteudo_materia_id') == turma['materia_id']
    ]

    if not resultados_filtrados:
        print("Nenhum resultado encontrado para esta turma.")
        input("\nAperte Enter para voltar.")
        return

    print(f"\n📘 Matéria: {turma['materia_nome']}")
    print(f"🏫 Turma: {turma['codigo']} - {turma['horario']}")
    print("-------------------------------------------")

    medias_alunos = []
    for cpf in alunos_turma:
        notas = [
            round((r['acertos'] / r['total']) * 10, 2)
            for r in resultados_filtrados if r['cpf'] == cpf and r['total'] > 0
        ]
        if notas:
            media = round(mean(notas), 2)
            medias_alunos.append(media)
            print(f"Aluno: {nome_por_cpf.get(cpf, cpf)} | Média: {media}")
        else:
            print(f"Aluno: {nome_por_cpf.get(cpf, cpf)} | Sem atividades registradas.")

    print("-------------------------------------------")
    if medias_alunos:
        print(f"Média geral da turma: {round(mean(medias_alunos), 2)}")
    input("\nAperte Enter para voltar.")

# ---------------------------------------------------------------------
# RELATÓRIO DO ADMINISTRADOR
# ---------------------------------------------------------------------
def relatorio_administrador():
    usuarios = carregar_json(USUARIOS_FILE)
    materias = carregar_json(MATERIAS_FILE)
    turmas = carregar_json(TURMAS_FILE)
    resultados = carregar_json(RESULTADOS_FILE)

    total_usuarios = len(usuarios)
    total_alunos = sum(1 for u in usuarios if u.get('perfil') == 'Aluno')
    total_professores = sum(1 for u in usuarios if u.get('perfil') == 'Professor')
    total_materias = len(materias)
    total_turmas = len(turmas)
    total_resultados = len(resultados)

    print("\n=== 📊 Relatório Administrativo ===")
    print(f"Usuários totais: {total_usuarios}")
    print(f"Alunos: {total_alunos}")
    print(f"Professores: {total_professores}")
    print(f"Matérias criadas: {total_materias}")
    print(f"Turmas registradas: {total_turmas}")
    print(f"Atividades realizadas: {total_resultados}")

    if total_resultados > 0:
        notas = [
            round((r['acertos'] / r['total']) * 10, 2)
            for r in resultados if r.get('total', 0) > 0
        ]
        print(f"Média geral de desempenho dos alunos: {round(mean(notas), 2)} / 10")
    else:
        print("Nenhuma atividade foi registrada ainda.")
    input("\nAperte Enter para voltar.")

# ---------------------------------------------------------------------
# RELATÓRIO DO ALUNO (já implementado antes)
# ---------------------------------------------------------------------
def exibir_relatorio_aluno(usuario):
    from services.quiz import carregar_resultados
    resultados = carregar_resultados()
    meus = [r for r in resultados if r['cpf'] == usuario['cpf']]
    if not meus:
        print("Nenhum desempenho encontrado ainda.")
        input("\nAperte Enter para voltar.")
        return

    print(f"\n📊 Desempenho de {usuario['nome']}:")
    materias = {}
    for r in meus:
        mat = r.get('conteudo_materia_nome', 'Desconhecida')
        nota = round((r['acertos'] / r['total']) * 10, 2) if r.get('total') else 0
        materias.setdefault(mat, []).append(nota)

    for mat, notas in materias.items():
        print(f"- {mat}: Média {round(mean(notas), 2)} / 10")

    input("\nAperte Enter para voltar ao menu.")
