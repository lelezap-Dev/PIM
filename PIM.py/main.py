# ======= main.py =======
from services.usuarios import cadastrar_usuario, autenticar, redefinir_senha
from services.conteudos import criar_conteudo, deletar_conteudo
from services.sessoes import registrar_login, registrar_logout, exibir_sessoes_usuario, listar_conteudos, editar_conteudo, listar_usuarios, excluir_usuario, editar_usuario, ranking_geral
from services.chatbot import chatbot_ajuda
from services.leitura import registrar_leitura, ja_visualizou_conteudo
from services.quiz import responder_conteudo
from services.relatorios import exibir_relatorio_aluno
from services.professores import carregar_materias, carregar_turmas, salvar_turmas, listar_conteudos_materia
from services.usuarios import atualizar_perfis_antigos
atualizar_perfis_antigos()
import time


# Conversão automática de perfis antigos para "Secretaria"
import json, os
USUARIOS_FILE = 'data/usuarios.json'
if os.path.exists(USUARIOS_FILE):
    with open(USUARIOS_FILE, 'r', encoding='utf-8') as f:
        dados = json.load(f)
    alterado = False
    for u in dados:
        if u.get('perfil') == 'Administrador':
            u['perfil'] = 'Secretaria'
            alterado = True
    if alterado:
        with open(USUARIOS_FILE, 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)


def menu_aluno(usuario):
    while True:
        print("\n--- Menu do Aluno ---")
        print("1. Ver minhas turmas e matérias")
        print("2. Estudar conteúdo")
        print("3. Fazer atividades (após estudar)")
        print("4. Ver desempenho")
        print("5. Sair")
        opcao = input("Escolha: ")

        if opcao == '1':
            exibir_turmas_materias(usuario)
        elif opcao == '2':
            estudar_conteudo(usuario)
        elif opcao == '3':
            responder_conteudo(usuario)
        elif opcao == '4':
            exibir_relatorio_aluno(usuario)
        elif opcao == '5':
            from services.sessoes import registrar_logout
            registrar_logout(usuario['cpf'])
            print("Logout registrado. Voltando ao menu principal...")
            time.sleep(0.6)
            break
            
        else:
            print("Opção inválida.")
        
def exibir_turmas_materias(usuario):
    turmas = carregar_turmas()
    minhas_turmas = [t for t in turmas if usuario['cpf'] in t.get('alunos', [])]

    if not minhas_turmas:
        print("Você ainda não está matriculado em nenhuma turma.")
        input("Aperte Enter para voltar ao menu.")
        return

    print("\nSuas turmas e matérias:")
    for i, t in enumerate(minhas_turmas, 1):
        print(f"{i}. {t['codigo']} - {t['materia_nome']} | {t['horario']}")
    input("\nAperte Enter para voltar ao menu.")

def estudar_conteudo(usuario):
    turmas = carregar_turmas()
    minhas_turmas = [t for t in turmas if usuario['cpf'] in t.get('alunos', [])]

    if not minhas_turmas:
        print("Você não está matriculado em nenhuma turma.")
        input("Aperte Enter para voltar.")
        return

    print("\nSuas turmas:")
    for i, t in enumerate(minhas_turmas, 1):
        print(f"{i}. {t['codigo']} - {t['materia_nome']}")
    try:
        escolha = int(input("Escolha uma turma para estudar: ")) - 1
        if escolha < 0 or escolha >= len(minhas_turmas):
            print("Opção inválida.")
            return
    except ValueError:
        print("Entrada inválida.")
        return

    turma = minhas_turmas[escolha]
    conteudos = listar_conteudos_materia(turma['materia_id'])
    if not conteudos:
        print("Ainda não há conteúdos disponíveis nesta matéria.")
        input("Aperte Enter para voltar.")
        return

    print(f"\nConteúdos disponíveis em {turma['materia_nome']}:")
    for i, c in enumerate(conteudos, 1):
        status = "✅ Lido" if ja_visualizou_conteudo(usuario['cpf'], turma['materia_id'], c['titulo']) else "❌ Não lido"
        print(f"{i}. {c['titulo']} [{status}]")

    try:
        escolha = int(input("Escolha um conteúdo para ler: ")) - 1
        if escolha < 0 or escolha >= len(conteudos):
            print("Opção inválida.")
            return
    except ValueError:
        print("Entrada inválida.")
        return

    conteudo = conteudos[escolha]
    print(f"\n=== {conteudo['titulo']} ===")
    print(conteudo['texto'])
    registrar_leitura(usuario['cpf'], turma['materia_id'], conteudo['titulo'])
    input("\nLeitura concluída! Aperte Enter para voltar ao menu.")


def menu_professor(usuario):
    from services.professores import (
        criar_materia, listar_materias_professor, editar_materia, excluir_materia,
        adicionar_conteudo_na_materia, editar_conteudo_da_materia, deletar_conteudo_da_materia,
        criar_turma, listar_turmas_professor, editar_turma, excluir_turma,
        criar_atividade, listar_atividades_professor, editar_atividade, excluir_atividade
    )
    from services.relatorios import gerar_relatorio_turma

    while True:
        print(f"\n--- Menu do Professor ({usuario['nome']}) ---")
        print("1. CRUD Matéria")
        print("2. CRUD Turma")
        print("3. CRUD Atividade")
        print("4. Gerar Relatório de Turma")
        print("5. Sair")

        opcao = input("Escolha: ").strip()

        # === CRUD MATÉRIA ===
        if opcao == '1':
            while True:
                print("\n📘 CRUD Matéria")
                print("1. Criar Matéria")
                print("2. Listar Minhas Matérias")
                print("3. Adicionar Conteúdo em Matéria")
                print("4. Editar Matéria")
                print("5. Editar Conteúdo de Matéria")
                print("6. Deletar Conteúdo de Matéria")
                print("7. Excluir Matéria")
                print("0. Voltar")
                sub = input("Escolha: ").strip()
                if sub == '1':
                    criar_materia(usuario['cpf'])
                elif sub == '2':
                    listar_materias_professor(usuario['cpf'])
                    input("\nPressione Enter para continuar.")
                elif sub == '3':
                    adicionar_conteudo_na_materia(usuario['cpf'])
                elif sub == '4':
                    editar_materia(usuario['cpf'])
                elif sub == '5':
                    editar_conteudo_da_materia(usuario['cpf'])
                elif sub == '6':
                    deletar_conteudo_da_materia(usuario['cpf'])
                elif sub == '7':
                    excluir_materia(usuario['cpf'])
                elif sub == '0':
                    break
                else:
                    print("Opção inválida.")
                time.sleep(1)

                # === CRUD TURMA ===
        elif opcao == '2':
            while True:
                print("\n🏫 CRUD Turma")
                print("1. Criar Turma")
                print("2. Listar Minhas Turmas")
                print("3. Editar Turma")
                print("4. Excluir Turma")
                print("0. Voltar")
                sub = input("Escolha: ").strip()
                if sub == '1':
                    criar_turma(usuario['cpf'])
                elif sub == '2':
                    listar_turmas_professor(usuario['cpf'])
                    input("\nPressione Enter para continuar.")
                elif sub == '3':
                    editar_turma(usuario['cpf'])
                elif sub == '4':
                    excluir_turma(usuario['cpf'])
                elif sub == '0':
                    break
                else:
                    print("Opção inválida.")
                time.sleep(1)

        # === CRUD ATIVIDADE ===
        elif opcao == '3':
            while True:
                print("\n🧾 CRUD Atividade")
                print("1. Criar Atividade")
                print("2. Listar Minhas Atividades")
                print("3. Editar Atividade")
                print("4. Excluir Atividade")
                print("0. Voltar")
                sub = input("Escolha: ").strip()
                if sub == '1':
                    criar_atividade(usuario['cpf'])
                elif sub == '2':
                    listar_atividades_professor(usuario['cpf'])
                    input("\nPressione Enter para continuar.")
                elif sub == '3':
                    editar_atividade(usuario['cpf'])
                elif sub == '4':
                    excluir_atividade(usuario['cpf'])
                elif sub == '0':
                    break
                else:
                    print("Opção inválida.")
                time.sleep(1)

        # === RELATÓRIO DE TURMA ===
        elif opcao == '4':
            gerar_relatorio_turma(usuario['cpf'])

        # === SAIR ===
        elif opcao == '5':
            from services.sessoes import registrar_logout
            registrar_logout(usuario['cpf'])
            print("Logout registrado. Saindo do menu do professor...")
            time.sleep(0.6)
            break

        else:
            print("Opção inválida.")

# ======= Submenus para secretarios (mantidos) =======
def crud_usuarios():
    while True:
        print("\n--- CRUD de Usuários ---")
        print("1. Listar usuários")
        print("2. Editar usuário")                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    
        print("3. Excluir usuário")
        print("4. Voltar")
        escolha = input("Escolha: ")

        if escolha == '1':
            listar_usuarios()
        elif escolha == '2':
            editar_usuario()
        elif escolha == '3':
            excluir_usuario()
        elif escolha == '4':
            break
        else:
            print("Opção inválida.")

def crud_conteudos():
    while True:
        print("\n--- Gerenciar Conteúdos ---")
        print("1. Criar conteúdo")
        print("2. Listar conteúdos")
        print("3. Editar conteúdo")
        print("4. Deletar conteúdo")
        print("5. Voltar")
        escolha = input("Escolha: ")

        if escolha == '1':
            criar_conteudo()
        elif escolha == '2':
            listar_conteudos()
        elif escolha == '3':
            editar_conteudo()
        elif escolha == '4':
            deletar_conteudo()
        elif escolha == '5':
            break
        else:
            print("Opção inválida.")

# ======= Menu da Secretaria =======
def menu_secretaria(usuario):
    from services.usuarios import carregar_usuarios
    from services.professores import (
        matricular_aluno_em_turma,
        carregar_turmas,
        carregar_materias,
    )
    from services.relatorios import relatorio_secretaria
    from services.graficos import (
        exibir_grafico_medias_materias,
        exibir_grafico_ranking,
    )

    while True:
        print("\n--- Menu da Secretaria ---")
        print("1. CRUD Usuários")
        print("2. Matricular aluno em matéria/turma")
        print("3. Visualizar relatórios")
        print("4. Visualizar gráficos de desempenho")
        print("5. Histórico de sessões de usuários")
        print("6. Voltar ao menu principal")


        opcao = input("Escolha: ").strip()

        # ======= 1. CRUD Usuários =======
        if opcao == "1":
            print("\n--- CRUD Usuários ---")
            print("1. Listar usuários")
            print("2. Editar usuário")
            print("3. Excluir usuário")
            print("4. Voltar")

            sub = input("Escolha: ").strip()
            usuarios = carregar_usuarios()

            if sub == "1":
                print("\nUsuários cadastrados:")
                for i, u in enumerate(usuarios, 1):
                    print(f"{i}. {u['nome']} ({u['perfil']}) - CPF: {u['cpf']}")
                input("\nPressione Enter para voltar.")
            
            elif sub == "2":
                cpf = input("CPF do usuário que deseja editar: ").strip()
                for u in usuarios:
                    if u["cpf"] == cpf:
                        novo_nome = input(f"Novo nome ({u['nome']}): ").strip() or u["nome"]
                        novo_email = input(f"Novo e-mail ({u['email']}): ").strip() or u["email"]
                        u["nome"] = novo_nome
                        u["email"] = novo_email
                        from services.usuarios import salvar_usuarios
                        salvar_usuarios(usuarios)
                        print("✅ Usuário atualizado com sucesso.")
                        break
                else:
                    print("Usuário não encontrado.")
                input("\nPressione Enter para voltar.")
            
            elif sub == "3":
                cpf = input("CPF do usuário que deseja excluir: ").strip()
                usuarios = [u for u in usuarios if u["cpf"] != cpf]
                from services.usuarios import salvar_usuarios
                salvar_usuarios(usuarios)
                print("✅ Usuário excluído com sucesso.")
                input("\nPressione Enter para voltar.")
            
            elif sub == "4":
                continue
            else:
                print("Opção inválida.")
                continue

        # ======= 2. Matricular aluno =======
        elif opcao == "2":
            matricular_aluno_em_turma(None)  # Secretaria pode matricular em qualquer turma
            input("\nPressione Enter para voltar.")

        # ======= 3. Relatórios =======
        elif opcao == "3":
            print("\n--- Relatórios ---")
            print("1. Relatório geral de turmas e matérias")
            print("2. Relatório detalhado (por aluno)")
            print("3. Voltar")

            sub = input("Escolha: ").strip()
            if sub == "1":
                relatorio_secretaria()
            elif sub == "2":
                cpf = input("Digite o CPF do aluno: ").strip()
                relatorio_secretaria(cpf)
            elif sub == "3":
                continue
            else:
                print("Opção inválida.")
            input("\nPressione Enter para voltar.")

        # ======= 4. Gráficos =======
        elif opcao == "4":
            print("\n--- Gráficos Disponíveis ---")
            print("1. Médias por matéria")
            print("2. Ranking de alunos (Top 10)")
            print("3. Voltar")

            sub = input("Escolha: ").strip()
            if sub == "1":
                exibir_grafico_medias_materias()
            elif sub == "2":
                exibir_grafico_ranking()
            elif sub == "3":
                continue
            else:
                print("Opção inválida.")
                
        elif opcao == "5":
            from services.sessoes import exibir_todas_sessoes
            exibir_todas_sessoes()
            input("\nPressione Enter para voltar.")

        elif opcao == "6":
            print("Voltando ao menu principal...")
            break

        else:
            print("Opção inválida.")

if __name__ == '__main__':
    while True:
        print('\n--- Sistema Educacional ---')
        print('1. Cadastrar usuário')
        print('2. Entrar')
        print('3. Esqueci minha senha')
        print('4. Chatbot de Ajuda')
        print('5. Sair')
        escolha = input('Escolha: ')

        if escolha == '1':
            cadastrar_usuario()
        elif escolha == '2':
            usuario = autenticar()
            if usuario:
                registrar_login(usuario['cpf'], usuario.get('nome',''))
                if usuario['perfil'] == 'Aluno':
                    menu_aluno(usuario)
                elif usuario['perfil'] == 'Secretaria':
                    menu_secretaria(usuario)
                elif usuario['perfil'] == 'Professor':
                    menu_professor(usuario)
        elif escolha == '3':
            redefinir_senha()
        elif escolha == '4':
            chatbot_ajuda()
        elif escolha == '5':
            try:
                registrar_logout(usuario['cpf'])
            except:
                pass
            break
        else:
            print('Opção inválida.')
