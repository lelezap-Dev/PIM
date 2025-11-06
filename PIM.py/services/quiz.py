# ======= services/quiz.py =======
import json
from services.conteudos import carregar_conteudos
import random
from services.leitura import ja_visualizou_conteudo
from services.professores import carregar_atividades, carregar_turmas, listar_conteudos_materia

def carregar_resultados():
    try:
        with open('data/resultados.json', 'r') as file:
            return json.load(file)
    except:
        return []

def salvar_resultados(resultados):
    with open('data/resultados.json', 'w') as file:
        json.dump(resultados, file, indent=4)

def responder_conteudo(usuario):
    # agora as "atividades" são as avaliações criadas pelos professores
    atividades = carregar_atividades()
    if not atividades:
        print('Nenhuma atividade disponível.')
        return

    # listar atividades disponíveis para o aluno (filtrar por matrícula)
    turmas = carregar_turmas()
    # turmas em que o aluno está matriculado
    turmas_do_aluno = [t for t in turmas if usuario['cpf'] in t.get('alunos', [])]
    turma_codigos_aluno = {t['codigo'] for t in turmas_do_aluno}
    materias_ids_aluno = {t['materia_id'] for t in turmas_do_aluno}

    atividades_disponiveis = []
    for a in atividades:
        if a['turma_codigo']:
            # atividade vinculada a turma específica: só alunos daquela turma podem ver
            if a['turma_codigo'] in turma_codigos_aluno:
                atividades_disponiveis.append(a)
        else:
            # atividade aberta para todas turmas da matéria: verifica se aluno tem turma dessa matéria
            if a['materia_id'] in materias_ids_aluno:
                atividades_disponiveis.append(a)

    if not atividades_disponiveis:
        print("Nenhuma atividade disponível para suas turmas ou matérias.")
        return

    print("\nAtividades disponíveis:")
    for i, a in enumerate(atividades_disponiveis, 1):
        print(f"{i}. {a['titulo']} | Matéria: {a['materia_nome']} | Turma: {a['turma_codigo'] or 'Todas'}")

    try:
        escolha = int(input("Escolha a atividade: ")) - 1
        if escolha < 0 or escolha >= len(atividades_disponiveis):
            print("Opção inválida.")
            return
    except ValueError:
        print("Entrada inválida.")
        return

    atividade = atividades_disponiveis[escolha]

    # --- Verificar se aluno leu conteúdo da matéria ---
    conteudos_da_materia = listar_conteudos_materia(atividade['materia_id'])
    # se não houver conteúdo cadastrado, bloquear (professor precisa criar conteúdo)
    if not conteudos_da_materia:
        print("Esta matéria ainda não possui conteúdo para estudo. Peça ao professor para adicionar conteúdos antes da atividade.")
        return

    # verificar se aluno já visualizou pelo menos um título de conteúdo desta matéria
    ja_leu_algum = False
    for c in conteudos_da_materia:
        if ja_visualizou_conteudo(usuario['cpf'], atividade['materia_id'], c['titulo']):
            ja_leu_algum = True
            break

    if not ja_leu_algum:
        print("\n⚠️ Você precisa estudar o conteúdo da matéria antes de fazer a atividade.")
        input("Aperte Enter para voltar.")
        return

    # realizar a atividade
    pontuacao = 0
    total = len(atividade['perguntas'])

    for p in atividade['perguntas']:
        print(f"\n{p['pergunta']}")
        alternativas_embaralhadas = p['alternativas'][:]
        random.shuffle(alternativas_embaralhadas)
        for i, alt in enumerate(alternativas_embaralhadas):
            print(f"{i+1}. {alt}")
        try:
            resp = int(input('Sua resposta: ')) - 1
            if alternativas_embaralhadas[resp] == p['resposta_correta']:
                pontuacao += 1
        except (ValueError, IndexError):
            print('Resposta inválida.')

    print(f"\nVocê acertou {pontuacao}/{total}!")
    # salvar resultado (com referência à matéria para relatórios)
    resultados = carregar_resultados()
    resultados.append({
        'cpf': usuario['cpf'],
        'atividade_id': atividade['id'],
        'conteudo_materia_id': atividade['materia_id'],
        'conteudo_materia_nome': atividade['materia_nome'],
        'acertos': pontuacao,
        'total': total
    })
    salvar_resultados(resultados)

def relatorio_pessoal(cpf):
    resultados = carregar_resultados()
    user_results = [r for r in resultados if r['cpf'] == cpf]

    if not user_results:
        print('Nenhum resultado encontrado.')
        return

    acertos = [r['acertos'] for r in user_results]

    print('\n📋 Relatório de Desempenho:')
    print(f"- Total de Atividades Realizadas: {len(user_results)}")
    print(f"- Média de Acertos: {round(sum(acertos) / len(acertos), 2)}")
    print(f"- Maior Nota: {max(acertos)}")
    print(f"- Menor Nota: {min(acertos)}")
    print("\nContinue estudando para melhorar ainda mais! 🚀")

def relatorio_usuario(cpf):
    resultados = carregar_resultados()
    user_results = [r for r in resultados if r['cpf'] == cpf]
    if not user_results:
        print('Nenhum resultado encontrado.')
        return

    acertos = [r['acertos'] for r in user_results]
    relatorio = {
        'cpf': cpf,
        'total_atividades': len(user_results),
        'media_acertos': round(sum(acertos)/len(acertos), 2),
        'maior_nota': max(acertos),
        'menor_nota': min(acertos)
    }
    print(json.dumps(relatorio, indent=4))