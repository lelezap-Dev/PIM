# services/chatbot.py
import time

def chatbot_ajuda():
    while True:
        print("\n=== 🤖 Chatbot de Ajuda ===")
        print("1. Como faço login ou cadastro?")
        print("2. Como estudar os conteúdos?")
        print("3. Por que não consigo fazer a atividade?")
        print("4. O que é a função de professor?")
        print("5. Como é garantida a segurança dos meus dados?")
        print("0. Voltar ao menu principal")

        opcao = input("Escolha uma pergunta: ")

        respostas = {
            '1': (
                "\n🔹 Para fazer login, use seu email e senha cadastrados.\n"
                "🔹 Se ainda não tem uma conta, escolha 'Fazer Cadastro' no menu principal.\n"
                "🔹 Use uma senha com letras, números e símbolos para maior segurança."
            ),
            '2': (
                "\n📘 Para estudar os conteúdos:\n"
                "1. Acesse o menu do aluno.\n"
                "2. Vá até 'Estudar conteúdo'.\n"
                "3. Escolha a turma e o conteúdo desejado.\n"
                "💡 Após a leitura, o sistema registra automaticamente sua visualização!"
            ),
            '3': (
                "\n⚠️ Você só pode fazer atividades se:\n"
                "- Estiver matriculado em uma turma;\n"
                "- E já tiver estudado o conteúdo da matéria.\n"
                "Se ainda não leu o conteúdo, vá até 'Estudar conteúdo' antes de tentar novamente."
            ),
            '4': (
                "\n👨‍🏫 O perfil de professor é responsável por:\n"
                "- Criar matérias e conteúdos;\n"
                "- Cadastrar turmas e alunos;\n"
                "- Criar atividades (questionários);\n"
                "- Gerar relatórios de desempenho dos alunos.\n"
                "Cada professor leciona apenas suas próprias matérias e turmas."
            ),
            '5': (
                "\n🔒 A plataforma segue boas práticas de segurança:\n"
                "- As senhas são armazenadas de forma protegida;\n"
                "- Dados pessoais não são compartilhados;\n"
                "- Incentiva-se o uso de senhas fortes e o cuidado com links suspeitos.\n"
                "Esses conceitos fazem parte da LGPD (Lei Geral de Proteção de Dados)."
            )
        }

        if opcao == '0':
            print("\nVoltando ao menu principal...")
            time.sleep(1)
            break
        elif opcao in respostas:
            print(respostas[opcao])
            input("\nPressione Enter para voltar ao Chatbot.")
        else:
            print("Opção inválida. Tente novamente.")
