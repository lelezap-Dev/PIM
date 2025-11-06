# ======= services/graficos.py =======
import json
import os
import matplotlib.pyplot as plt

DATA_DIR = "data"
ATIVIDADES_FILE = os.path.join(DATA_DIR, "atividades.json")
RESULTADOS_FILE = os.path.join(DATA_DIR, "resultados.json")
USUARIOS_FILE = os.path.join(DATA_DIR, "usuarios.json")
MATERIAS_FILE = os.path.join(DATA_DIR, "materias.json")

# -----------------------
# Funções auxiliares
# -----------------------
def carregar_json(caminho):
    """Lê um arquivo JSON e retorna uma lista vazia em caso de erro."""
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


# -----------------------
# 1️⃣ Gráfico de Médias por Matéria (Secretaria)
# -----------------------
def exibir_grafico_medias_materias():
    """
    Mostra um gráfico com a média de desempenho dos alunos por matéria.
    """
    atividades = carregar_json(ATIVIDADES_FILE)
    resultados = carregar_json(RESULTADOS_FILE)

    if not atividades or not resultados:
        print("⚠️ Não há dados suficientes para gerar o gráfico.")
        input("\nPressione Enter para voltar.")
        return

    medias = {}
    for resultado in resultados:
        materia_id = resultado.get("materia_id")
        acertos = resultado.get("acertos", 0)
        total = resultado.get("total_perguntas") or resultado.get("total", 1)
        perc = acertos / total * 100 if total > 0 else 0

        materia = next((a for a in atividades if a.get("materia_id") == materia_id), None)
        if not materia:
            continue
        nome_materia = materia.get("materia_nome", "Desconhecida")

        medias.setdefault(nome_materia, []).append(perc)

    if not medias:
        print("Nenhuma média encontrada.")
        input("\nPressione Enter para voltar.")
        return

    nomes = list(medias.keys())
    valores = [sum(lista) / len(lista) for lista in medias.values()]

    plt.figure(figsize=(8, 5))
    plt.bar(nomes, valores, color="royalblue")
    plt.title("📊 Média de Desempenho por Matéria")
    plt.ylabel("Média de Acertos (%)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()


# -----------------------
# 2️⃣ Gráfico de Desempenho Individual (Aluno)
# -----------------------
def exibir_grafico_desempenho_aluno(cpf_aluno):
    """
    Mostra o desempenho de um aluno (porcentagem de acertos por matéria).
    """
    resultados = carregar_json(RESULTADOS_FILE)
    atividades = carregar_json(ATIVIDADES_FILE)

    aluno_resultados = [r for r in resultados if r.get("cpf") == cpf_aluno]
    if not aluno_resultados:
        print("Nenhum resultado encontrado para este aluno.")
        input("\nPressione Enter para voltar.")
        return

    materias = {}
    for r in aluno_resultados:
        materia_id = r.get("materia_id")
        acertos = r.get("acertos", 0)
        total = r.get("total_perguntas") or r.get("total", 1)
        perc = acertos / total * 100 if total > 0 else 0

        materia = next((a for a in atividades if a.get("materia_id") == materia_id), None)
        nome_materia = materia.get("materia_nome", "Desconhecida") if materia else "Desconhecida"

        materias.setdefault(nome_materia, []).append(perc)

    nomes = list(materias.keys())
    valores = [sum(lista) / len(lista) for lista in materias.values()]

    plt.figure(figsize=(8, 5))
    plt.bar(nomes, valores, color='skyblue')
    plt.title("📈 Desempenho Individual por Matéria")
    plt.ylabel("Acertos (%)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()


# -----------------------
# 3️⃣ Gráfico de Ranking (Geral)
# -----------------------
def exibir_grafico_ranking():
    """
    Mostra o ranking dos alunos com base nas médias gerais de desempenho.
    """
    resultados = carregar_json(RESULTADOS_FILE)
    usuarios = carregar_json(USUARIOS_FILE)

    if not resultados:
        print("Nenhum resultado disponível.")
        input("\nPressione Enter para voltar.")
        return

    medias_alunos = {}
    for r in resultados:
        cpf = r.get("cpf")
        acertos = r.get("acertos", 0)
        total = r.get("total_perguntas") or r.get("total", 1)
        perc = acertos / total * 100 if total > 0 else 0
        medias_alunos.setdefault(cpf, []).append(perc)

    if not medias_alunos:
        print("Nenhum dado encontrado.")
        input("\nPressione Enter para voltar.")
        return

    nomes, valores = [], []
    for cpf, lista in medias_alunos.items():
        usuario = next((u for u in usuarios if u.get("cpf") == cpf), None)
        nome = usuario.get("nome") if usuario else cpf
        nomes.append(nome)
        valores.append(sum(lista) / len(lista))

    # Ordenar ranking e limitar ao top 10
    dados = sorted(zip(nomes, valores), key=lambda x: x[1], reverse=True)[:10]
    nomes, valores = zip(*dados)

    plt.figure(figsize=(9, 5))
    plt.barh(nomes, valores, color='gold')
    plt.title("🏆 Ranking de Alunos - Top 10")
    plt.xlabel("Média Geral (%)")
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.show()
