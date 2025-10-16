# ======= main.py =======
from services.usuarios import cadastrar_usuario, autenticar, redefinir_senha
from services.conteudos import criar_conteudo, deletar_conteudo
from services.quiz import responder_conteudo, relatorio_usuario, relatorio_pessoal
from services.graficos import (
    gerar_grafico_media_usuarios,
    gerar_grafico_distribuicao,
    gerar_grafico_por_conteudo
)
from services.sessoes import registrar_login, registrar_logout, exibir_sessoes_usuario, visualizar_conteudos_por_tema, listar_conteudos, editar_conteudo, listar_usuarios, excluir_usuario, editar_usuario, ranking_geral
from services.certificados import gerar_certificado
from services.professores import criar_materia, criar_turma, criar_atividade, listar_turmas_professor, matricular_aluno_em_turma, gerar_relatorio_turma
from services.chatbot import chatbot_ajuda
from services.professores import (
    criar_materia, listar_materias_professor, editar_materia, excluir_materia,
    adicionar_conteudo_na_materia,
    criar_turma, listar_turmas_professor, matricular_aluno_em_turma,
    criar_atividade, listar_atividades_professor, gerar_relatorio_turma
)


from services.professores import carregar_turmas, carregar_materias, listar_conteudos_materia
from services.leitura import registrar_leitura, ja_visualizou_conteudo
from services.quiz import responder_conteudo
from services.relatorios import exibir_relatorio_aluno

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
        status = "✅ Lido" if ja_visualizou_conteudo(usuario['nome'], c['titulo']) else "❌ Não lido"
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
    registrar_leitura(usuario['nome'], conteudo['titulo'])
    input("\nLeitura concluída! Aperte Enter para voltar ao menu.")


def menu_professor(usuario):
    while True:
        print("\n--- Menu do Professor ---")
        print("1. Criar matéria")
        print("2. Listar/Editar/Deletar matérias")
        print("3. Adicionar conteúdo em matéria")
        print("4. Criar turma")
        print("5. Listar turmas")
        print("6. Matricular aluno em turma")
        print("7. Criar atividade (questionário)")
        print("8. Listar minhas atividades")
        print("9. Gerar relatório de turma")
        print("10. Sair")
        op = input("Escolha: ")
        if op == '1':
            criar_materia(usuario['cpf'])
        elif op == '2':
            print("Suas matérias:")
            listar_materias_professor(usuario['cpf'])
            sub = input("Deseja (e)ditar, (d)eletar ou (v)oltar? ").lower()
            if sub == 'e':
                editar_materia(usuario['cpf'])
            elif sub == 'd':
                excluir_materia(usuario['cpf'])
        elif op == '3':
            adicionar_conteudo_na_materia(usuario['cpf'])
        elif op == '4':
            criar_turma(usuario['cpf'])
        elif op == '5':
            listar_turmas_professor(usuario['cpf'])
        elif op == '6':
            matricular_aluno_em_turma()
        elif op == '7':
            criar_atividade(usuario['cpf'])
        elif op == '8':
            listar_atividades_professor(usuario['cpf'])
        elif op == '9':
            from services.relatorios import gerar_relatorio_turma
            gerar_relatorio_turma(usuario['cpf'])
        elif op == '10':
            break
        else:
            print("Opção inválida.")


# ======= Submenus para administrador (mantidos) =======
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

def menu_administrador(usuario):
    while True:
        print('\n--- Menu do Administrador ---')
        print('1. Gerenciar conteúdos')
        print('2. Gerenciar usuários')
        print('3. Relatório do Sistema')
        print('4. Gráficos de desempenho')
        print('5. Exportar relatórios')
        print('6. Ver sessões de um usuário')
        print('7. Sair')

        op = input('Escolha: ')

        if op == '1':
            crud_conteudos()
        elif op == '2':
            crud_usuarios()
        elif op == '3':
            from services.relatorios import relatorio_administrador
            relatorio_administrador()
        elif op == '4':
            gerar_grafico_media_usuarios()
            gerar_grafico_distribuicao()
            gerar_grafico_por_conteudo()
        elif op == '5':
            cpf = input('Digite o CPF do usuário para exportar: ')
            exportar_relatorio_txt(cpf)
            exportar_relatorio_json(cpf)
        elif op == '6':
            cpf = input('Digite o CPF do usuário: ')
            exibir_sessoes_usuario(cpf)
        elif op == '7':
            registrar_logout(usuario['cpf'])
            break
        else:
            print('Opção inválida.')

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
                registrar_login(usuario['cpf'])
                if usuario['perfil'] == 'Aluno':
                    menu_aluno(usuario)
                elif usuario['perfil'] == 'Administrador':
                    menu_administrador(usuario)
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
