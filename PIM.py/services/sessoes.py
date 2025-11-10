# ======= services/sessoes.py =======
import json
import os
from datetime import datetime

def carregar_sessoes():
    try:
        with open('data/sessoes.json', 'r') as file:
            return json.load(file)
    except:
        return []

def salvar_sessoes(sessoes):
    os.makedirs('data', exist_ok=True)
    with open('data/sessoes.json', 'w') as file:
        json.dump(sessoes, file, indent=4, ensure_ascii=False)

def registrar_login(cpf, nome):
    sessoes = carregar_sessoes()
    sessao = {
        'cpf': cpf,
        'nome': nome,
        'inicio': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'fim': None,
        'duracao_minutos': None
    }
    sessoes.append(sessao)
    salvar_sessoes(sessoes)


def registrar_logout(cpf):
    sessoes = carregar_sessoes()
    encontrado = False
    for sessao in reversed(sessoes):
        if sessao.get('cpf') == cpf and sessao.get('fim') is None:
            fim = datetime.now()
            inicio = datetime.strptime(sessao['inicio'], '%Y-%m-%d %H:%M:%S')
            sessao['fim'] = fim.strftime('%Y-%m-%d %H:%M:%S')
            sessao['duracao_minutos'] = round((fim - inicio).total_seconds() / 60, 2)
            encontrado = True
            break
    if not encontrado:
        print("Aviso: não foi encontrada sessão aberta para esse CPF. Nenhuma alteração feita.")
    salvar_sessoes(sessoes)


def exibir_sessoes_usuario(cpf):
    sessoes = carregar_sessoes()
    user_sessions = [s for s in sessoes if s['cpf'] == cpf]
    if not user_sessions:
        print('Nenhuma sessão encontrada para este usuário.')
        return

    print('\n📋 Histórico de Sessões:')
    for sessao in user_sessions:
        fim = sessao['fim'] if sessao['fim'] else '(sessão em andamento)'
        duracao = sessao['duracao_minutos'] if sessao['duracao_minutos'] else '-'
        print(f"Início: {sessao['inicio']} | Fim: {fim} | Duração: {duracao} minutos")
        
def visualizar_conteudos_por_tema(nome_usuario):
    from services.conteudos import carregar_conteudos
    from services.leitura import registrar_leitura

    conteudos = carregar_conteudos()
    if not conteudos:
        print("Nenhum conteúdo disponível.")
        return

    temas_disponiveis = list(set(c['tema'] for c in conteudos))

    print("\nTemas disponíveis:")
    for i, tema in enumerate(temas_disponiveis):
        print(f"{i+1}. {tema}")

    try:
        escolha = int(input("Escolha o tema para visualizar os conteúdos: ")) - 1
        if escolha < 0 or escolha >= len(temas_disponiveis):
            print("Opção inválida.")
            return
    except ValueError:
        print("Entrada inválida.")
        return

    tema_escolhido = temas_disponiveis[escolha]
    conteudos_filtrados = [c for c in conteudos if c['tema'] == tema_escolhido]

    print(f"\nConteúdos do tema '{tema_escolhido}':")
    for c in conteudos_filtrados:
        print(f"\nTítulo: {c['titulo']}\nDescrição: {c['descricao']}")
        registrar_leitura(nome_usuario, c['titulo'])
        
def listar_conteudos():
    from services.conteudos import carregar_conteudos
    conteudos = carregar_conteudos()
    if not conteudos:
        print("Nenhum conteúdo cadastrado.")
        return
    print("\n📚 Todos os Conteúdos:")
    for i, c in enumerate(conteudos):
        print(f"{i+1}. {c['titulo']} - {c['tema']}: {c['descricao']}")

def editar_conteudo():
    from services.conteudos import carregar_conteudos, salvar_conteudos
    conteudos = carregar_conteudos()
    if not conteudos:
        print("Nenhum conteúdo para editar.")
        return

    listar_conteudos()
    try:
        escolha = int(input("Digite o número do conteúdo que deseja editar: ")) - 1
        if escolha < 0 or escolha >= len(conteudos):
            print("Opção inválida.")
            return
    except ValueError:
        print("Entrada inválida.")
        return

    conteudo = conteudos[escolha]
    print(f"Editando: {conteudo['titulo']} ({conteudo['tema']})")
    conteudo['titulo'] = input("Novo título (ou Enter para manter): ") or conteudo['titulo']
    conteudo['descricao'] = input("Nova descrição (ou Enter para manter): ") or conteudo['descricao']
    salvar_conteudos(conteudos)
    print("✅ Conteúdo atualizado com sucesso!")

def listar_usuarios():
    from services.usuarios import carregar_usuarios
    usuarios = carregar_usuarios()
    if not usuarios:
        print("Nenhum usuário cadastrado.")
        return

    print("\n👥 Lista de Usuários:")
    for u in usuarios:
        print(f"CPF: {u['cpf']} | Nome: {u['nome']} | E-mail: {u['email']} | Perfil: {u['perfil']}")

def editar_usuario():
    from services.usuarios import carregar_usuarios, salvar_usuarios
    usuarios = carregar_usuarios()
    cpf = input("Digite o CPF do usuário que deseja editar: ")
    usuario = next((u for u in usuarios if u['cpf'] == cpf), None)
    if not usuario:
        print("Usuário não encontrado.")
        return

    print(f"Editando usuário: {usuario['nome']}")
    usuario['nome'] = input("Novo nome (ou Enter para manter): ") or usuario['nome']
    usuario['email'] = input("Novo e-mail (ou Enter para manter): ") or usuario['email']
    novo_perfil = input("Novo perfil (Aluno, Administrador) ou Enter para manter: ").capitalize()
    if novo_perfil in ['Aluno', 'Administrador']:
        usuario['perfil'] = novo_perfil

    nova_chave = input("Nova palavra-chave secreta (ou Enter para manter): ")
    if nova_chave:
        usuario['palavra_chave'] = nova_chave

    salvar_usuarios(usuarios)
    print("✅ Usuário atualizado com sucesso!")


def excluir_usuario():
    from services.usuarios import carregar_usuarios, salvar_usuarios
    usuarios = carregar_usuarios()
    cpf = input("Digite o CPF do usuário que deseja excluir: ")
    usuario = next((u for u in usuarios if u['cpf'] == cpf), None)
    if not usuario:
        print("Usuário não encontrado.")
        return

    confirm = input(f"Tem certeza que deseja excluir {usuario['nome']}? (s/n): ").lower()
    if confirm == 's':
        usuarios = [u for u in usuarios if u['cpf'] != cpf]
        salvar_usuarios(usuarios)
        print("✅ Usuário excluído com sucesso.")
    else:
        print("Operação cancelada.")
    
    # ======= Ranking de desempenho dos alunos =======
def ranking_geral():
    from services.quiz import carregar_resultados
    from services.usuarios import carregar_usuarios

    resultados = carregar_resultados()
    usuarios = carregar_usuarios()

    desempenho = {}
    for r in resultados:
        nome = next((u['nome'] for u in usuarios if u['cpf'] == r['cpf']), None)
        if not nome:
            continue
        if nome not in desempenho:
            desempenho[nome] = {'acertos': 0, 'total': 0}
        desempenho[nome]['acertos'] += r['acertos']
        desempenho[nome]['total'] += r['total']

    ranking = []
    for nome, d in desempenho.items():
        media = round((d['acertos'] / d['total']) * 10, 2) if d['total'] > 0 else 0
        ranking.append((nome, media))

    ranking.sort(key=lambda x: x[1], reverse=True)

    print("\n🏆 Ranking dos Alunos por Desempenho:")
    for i, (nome, media) in enumerate(ranking, 1):
        destaque = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "⭐"
        print(f"{i}. {nome} - Média: {media}/10 {destaque}")

def exibir_todas_sessoes():
    SESSOES_FILE = 'data/sessoes.json'
    USUARIOS_FILE = 'data/usuarios.json'

    if not os.path.exists(SESSOES_FILE):
        print("Nenhuma sessão registrada ainda.")
        return

    with open(SESSOES_FILE, 'r', encoding='utf-8') as f:
        try:
            sessoes = json.load(f)
        except:
            print("Erro ao ler arquivo de sessões.")
            return

    if not sessoes:
        print("Nenhuma sessão registrada ainda.")
        return

    # Carregar usuários para mapear cpf -> nome
    usuarios = []
    if os.path.exists(USUARIOS_FILE):
        try:
            with open(USUARIOS_FILE, 'r', encoding='utf-8') as f:
                usuarios = json.load(f)
        except:
            usuarios = []

    mapa_nome = {u['cpf']: u.get('nome', '') for u in usuarios if u.get('cpf')}

    # Filtrar apenas alunos
    cpfs_alunos = {u['cpf'] for u in usuarios if u.get('perfil') == 'Aluno'}
    sessoes_filtradas = [s for s in sessoes if s.get('cpf') in cpfs_alunos]

    if not sessoes_filtradas:
        print("Nenhum histórico de alunos encontrado.")
        return

    # ordenar por inicio (mais recentes primeiro) quando possível
    def parse_inicio(item):
        try:
            return datetime.strptime(item.get('inicio',''), "%Y-%m-%d %H:%M:%S")
        except:
            return datetime.min

    sessoes_filtradas.sort(key=parse_inicio, reverse=True)

    print("\n=== Histórico de Sessões dos Alunos ===")
    for s in sessoes_filtradas:
        cpf = s.get('cpf')
        nome_reg = s.get('nome')  # se já existir no registro
        nome = nome_reg or mapa_nome.get(cpf, '') or 'Desconhecido'

        inicio = s.get('inicio', 'Indefinido')
        fim = s.get('fim')

        try:
            t_inicio = datetime.strptime(inicio, "%Y-%m-%d %H:%M:%S")
            t_fim = datetime.strptime(fim, "%Y-%m-%d %H:%M:%S") if fim else None
            if t_fim:
                duracao = round((t_fim - t_inicio).total_seconds() / 60, 1)
                tempo = f"{duracao} min"
            else:
                tempo = "Sessão ainda ativa"
        except:
            tempo = "Tempo não calculado"

        print(f"👤 {nome}")
        print(f"🕒 Login: {inicio}")
        print(f"🚪 Logout: {fim if fim else 'Ainda não saiu'}")
        print(f"⏱️ Duração: {tempo}")
        print("-" * 50)
        
def corrigir_sessoes_faltando_nome():
    """
    Atualiza o arquivo sessoes.json inserindo o nome do usuário
    quando ele estiver ausente (baseado no CPF).
    """
    SESSOES_FILE = 'data/sessoes.json'
    USUARIOS_FILE = 'data/usuarios.json'

    if not os.path.exists(SESSOES_FILE) or not os.path.exists(USUARIOS_FILE):
        print("Arquivos necessários não encontrados.")
        return

    with open(USUARIOS_FILE, 'r', encoding='utf-8') as f:
        usuarios = json.load(f)
    mapa = {u['cpf']: u.get('nome', '') for u in usuarios if u.get('cpf')}

    with open(SESSOES_FILE, 'r', encoding='utf-8') as f:
        sessoes = json.load(f)

    alterado = False
    for s in sessoes:
        cpf = s.get('cpf')
        if cpf and not s.get('nome') and mapa.get(cpf):
            s['nome'] = mapa[cpf]
            alterado = True

    if alterado:
        with open(SESSOES_FILE, 'w', encoding='utf-8') as f:
            json.dump(sessoes, f, indent=4, ensure_ascii=False)
        print("✅ Sessões atualizadas com nomes ausentes preenchidos.")
    else:
        print("Nenhuma sessão precisava de atualização.")
