# ======= services/chatbot.py =======
def chatbot_ajuda():
    print("\n=== Chatbot de Ajuda (FAQ) ===")
    perguntas = {
        "1": ("Como faço para me cadastrar?", "Vá até o menu principal e escolha 'Cadastrar usuário'. Preencha CPF, nome, e-mail, senha e perfil."),
        "2": ("Esqueci minha senha, e agora?", "Escolha 'Esqueci minha senha' no menu principal e informe o CPF e a palavra-chave secreta cadastrada."),
        "3": ("Como o professor cria uma turma?", "O professor acessa seu menu e escolhe 'Criar turma', informando a matéria e o horário. O sistema impede conflito de horário."),
        "4": ("Posso estar em duas turmas ao mesmo tempo?", "Não. O sistema não permite matrícula de um aluno em duas turmas com o mesmo horário."),
        "5": ("Quem cria as atividades/provas?", "Os professores criam atividades vinculadas às matérias que lecionam.")
    }

    for k, v in perguntas.items():
        print(f"{k}. {v[0]}")

    escolha = input("\nDigite o número da dúvida para ver a resposta (ou 0 para voltar): ").strip()
    if escolha == '0' or escolha == '':
        return
    if escolha in perguntas:
        print(f"\n💬 {perguntas[escolha][1]}")
    else:
        print("Opção inválida.")
    input("\nAperte Enter para voltar ao menu principal.")
