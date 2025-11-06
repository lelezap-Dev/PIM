# ======= services/usuarios.py =======
import json, os, bcrypt, sys
from utils.validacoes import validar_email, validar_senha, validar_cpf
from services.professores import carregar_materias, carregar_turmas, salvar_turmas
import time

# Função para leitura de senha mascarada (mostra '#' para cada caractere)
def input_senha_mascarada(prompt='Senha: '):
    print(prompt, end='', flush=True)
    senha = ''
    try:
        if sys.platform.startswith('win'):
            import msvcrt
            while True:
                ch = msvcrt.getch()
                if ch in {b'\r', b'\n'}:
                    print()
                    break
                if ch == b'\x03':  # ctrl-c
                    raise KeyboardInterrupt
                if ch == b'\x08':  # backspace
                    if len(senha) > 0:
                        senha = senha[:-1]
                        # apagar o último '#'
                        print('\b \b', end='', flush=True)
                else:
                    try:
                        char = ch.decode('utf-8')
                    except:
                        continue
                    senha += char
                    print('#', end='', flush=True)
        else:
            import tty, termios
            fd = sys.stdin.fileno()
            old = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                while True:
                    ch = sys.stdin.read(1)
                    if ch in ('\r', '\n'):
                        print()
                        break
                    if ch == '\x03':
                        raise KeyboardInterrupt
                    if ch in ('\x7f', '\b'):
                        if len(senha) > 0:
                            senha = senha[:-1]
                            print('\b \b', end='', flush=True)
                    else:
                        senha += ch
                        print('#', end='', flush=True)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old)
    except KeyboardInterrupt:
        print('\nOperação cancelada pelo usuário.')
        return ''
    return senha

def carregar_usuarios():
    try:
        with open('data/usuarios.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except:
        return []

def salvar_usuarios(usuarios):
    os.makedirs('data', exist_ok=True)
    with open('data/usuarios.json', 'w', encoding='utf-8') as file:
        json.dump(usuarios, file, indent=4, ensure_ascii=False)

def hash_senha(senha):
    return bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()

def verificar_senha(senha, senha_hash):
    try:
        return bcrypt.checkpw(senha.encode(), senha_hash.encode())
    except:
        return False

def cadastrar_usuario():
    usuarios = carregar_usuarios()

    while True:
        cpf = input('Digite seu CPF (apenas números, ex: 12345678900): ')
        if not validar_cpf(cpf):
            print('CPF inválido. Tente novamente.')
        elif any(u['cpf'] == cpf for u in usuarios):
            print('CPF já cadastrado.')
            return
        else:
            break

    nome = input('Nome completo: ')

    while True:
        email = input('E-mail (ex: nome@email.com): ')
        if validar_email(email):
            break
        print('E-mail inválido. Tente novamente.')

    while True:
        senha = input_senha_mascarada('Senha (mínimo 8 caracteres, com maiúscula, minúscula, número e símbolo): ')
        if not senha:
            print('Senha vazia. Tente novamente.')
            continue
        if validar_senha(senha):
            break
        print('Senha fraca. Tente novamente.')

    palavra_chave = input("Informe uma palavra-chave secreta para recuperação de senha: ")

    while True:
        perfil = input('Perfil (Aluno, Professor ou Administrador): ').capitalize()
        if perfil in ['Aluno', 'Administrador', 'Professor']:
            break
        print('Perfil inválido. Tente novamente.')

    senha_hash = hash_senha(senha)
    usuarios.append({ 'cpf': cpf, 'nome': nome, 'email': email, 'senha': senha_hash, 'perfil': perfil, 'palavra_chave': palavra_chave })
    salvar_usuarios(usuarios)
    print('Usuário cadastrado com sucesso!')
    print('\n🔒 Seus dados estão protegidos conforme a Lei Geral de Proteção de Dados (LGPD).')

def autenticar():
    usuarios = carregar_usuarios()
    cpf = input('CPF: ')
    senha = input_senha_mascarada('Senha: ')
    usuario = next((u for u in usuarios if u['cpf'] == cpf), None)

    if usuario and verificar_senha(senha, usuario['senha']):
        print(f"Bem-vindo, {usuario['nome']} ({usuario['perfil']})")
        return usuario
    else:
        print('CPF ou senha inválidos.')
        return None

def redefinir_senha():
    usuarios = carregar_usuarios()
    cpf = input('Digite seu CPF para redefinir a senha: ')
    usuario = next((u for u in usuarios if u['cpf'] == cpf), None)

    if not usuario:
        print('Usuário não encontrado.')
        return

    chave = input("Digite sua palavra-chave secreta: ")
    if chave != usuario.get('palavra_chave'):
        print("Palavra-chave incorreta.")
        return

    print(f"Usuário encontrado: {usuario['nome']}")
    print("Vamos definir uma nova senha.")

    while True:
        nova_senha = input_senha_mascarada('Nova senha (oculta): ')
        if not nova_senha:
            print('Senha vazia. Tente novamente.')
            continue
        if validar_senha(nova_senha):
            break
        print('Senha fraca. Use letras maiúsculas, minúsculas, números e símbolos.')

    usuario['senha'] = hash_senha(nova_senha)
    salvar_usuarios(usuarios)
    print('Senha atualizada com sucesso!')
    
# ==========================
# Conversão automática de perfil "Administrador" → "Secretaria"
# ==========================
def atualizar_perfis_antigos():
    usuarios = carregar_usuarios()
    alterado = False
    for u in usuarios:
        if u.get('perfil') == 'Administrador':
            u['perfil'] = 'Secretaria'
            alterado = True
    if alterado:
        salvar_usuarios(usuarios)
        print("Perfis antigos atualizados: 'Administrador' → 'Secretaria'.")
        time.sleep(0.5)

# ==========================
# CRUD Usuários (para Secretaria)
# ==========================
def listar_usuarios():
    usuarios = carregar_usuarios()
    if not usuarios:
        print("\nNenhum usuário cadastrado.")
        return
    print("\n=== Lista de Usuários ===")
    for i, u in enumerate(usuarios, 1):
        print(f"{i}. {u['nome']} | {u['email']} | CPF: {u['cpf']} | Perfil: {u['perfil']}")

def editar_usuario():
    usuarios = carregar_usuarios()
    if not usuarios:
        print("\nNenhum usuário cadastrado.")
        return

    listar_usuarios()
    try:
        indice = int(input("\nDigite o número do usuário que deseja editar: ")) - 1
        if indice < 0 or indice >= len(usuarios):
            print("Usuário inválido.")
            return
    except ValueError:
        print("Entrada inválida.")
        return

    usuario = usuarios[indice]
    print(f"\nEditando: {usuario['nome']} ({usuario['perfil']})")

    novo_nome = input(f"Novo nome (Enter para manter '{usuario['nome']}'): ").strip() or usuario['nome']
    novo_email = input(f"Novo email (Enter para manter '{usuario['email']}'): ").strip() or usuario['email']
    novo_perfil = input(f"Novo perfil (Aluno / Professor / Secretaria) [atual: {usuario['perfil']}]: ").capitalize()
    nova_senha = input_senha_mascarada("Nova senha (Enter para manter a atual): ")

    usuario['nome'] = novo_nome
    usuario['email'] = novo_email
    if novo_perfil in ['Aluno', 'Professor', 'Secretaria']:
        usuario['perfil'] = novo_perfil
    if nova_senha:
        usuario['senha'] = hash_senha(nova_senha)

    usuarios[indice] = usuario
    salvar_usuarios(usuarios)
    print("\n✅ Usuário atualizado com sucesso!")

def excluir_usuario():
    usuarios = carregar_usuarios()
    if not usuarios:
        print("\nNenhum usuário cadastrado.")
        return

    listar_usuarios()
    try:
        indice = int(input("\nDigite o número do usuário que deseja excluir: ")) - 1
        if indice < 0 or indice >= len(usuarios):
            print("Usuário inválido.")
            return
    except ValueError:
        print("Entrada inválida.")
        return

    confirm = input(f"Tem certeza que deseja excluir {usuarios[indice]['nome']}? (s/n): ").lower()
    if confirm == 's':
        usuarios.pop(indice)
        salvar_usuarios(usuarios)
        print("\n✅ Usuário excluído com sucesso!")
    else:
        print("Ação cancelada.")

# ==========================
# Listar matérias e professores
# ==========================
def listar_materias_e_professores():
    MATERIAS_FILE = 'data/materias.json'
    if not os.path.exists(MATERIAS_FILE):
        print("Nenhuma matéria encontrada.")
        return
    with open(MATERIAS_FILE, 'r', encoding='utf-8') as f:
        materias = json.load(f)
    if not materias:
        print("Nenhuma matéria cadastrada.")
        return
    print("\n=== Matérias e Professores Responsáveis ===")
    for i, m in enumerate(materias, 1):
        print(f"{i}. {m.get('nome')} — Professor CPF: {m.get('professor_cpf')}")

# ==========================
# Secretaria vincula aluno a matéria/turma
# ==========================
def vincular_aluno_materia_secretaria():
    usuarios = carregar_usuarios()
    alunos = [u for u in usuarios if u.get('perfil') == 'Aluno']
    if not alunos:
        print("\nNenhum aluno cadastrado.")
        return

    print("\n=== Alunos disponíveis ===")
    for i, a in enumerate(alunos, 1):
        print(f"{i}. {a['nome']} | CPF: {a['cpf']}")
    try:
        escolha_aluno = int(input("\nEscolha o número do aluno: ")) - 1
        if escolha_aluno < 0 or escolha_aluno >= len(alunos):
            print("Opção inválida.")
            return
    except ValueError:
        print("Entrada inválida.")
        return

    aluno = alunos[escolha_aluno]
    materias = carregar_materias()
    if not materias:
        print("Nenhuma matéria cadastrada.")
        return

    print("\n=== Matérias disponíveis ===")
    for i, m in enumerate(materias, 1):
        print(f"{i}. {m['nome']} | Professor CPF: {m['professor_cpf']}")
    try:
        escolha_materia = int(input("\nEscolha a matéria: ")) - 1
        if escolha_materia < 0 or escolha_materia >= len(materias):
            print("Opção inválida.")
            return
    except ValueError:
        print("Entrada inválida.")
        return

    materia = materias[escolha_materia]
    turmas = carregar_turmas()
    turmas_materia = [t for t in turmas if t.get('materia_id') == materia.get('id')]

    if not turmas_materia:
        print("Não há turmas cadastradas para esta matéria.")
        return

    print("\n=== Turmas da matéria selecionada ===")
    for i, t in enumerate(turmas_materia, 1):
        print(f"{i}. {t['codigo']} | {t['horario']} | Alunos: {len(t['alunos'])}")
    try:
        escolha_turma = int(input("\nEscolha a turma: ")) - 1
        if escolha_turma < 0 or escolha_turma >= len(turmas_materia):
            print("Opção inválida.")
            return
    except ValueError:
        print("Entrada inválida.")
        return

    turma = turmas_materia[escolha_turma]
    # verificar conflito de horário
    turmas_aluno = [t for t in turmas if aluno['cpf'] in t.get('alunos', [])]
    if any(t.get('horario') == turma.get('horario') for t in turmas_aluno):
        print("⚠️  O aluno já está matriculado em outra turma neste mesmo horário.")
        return

    # matricular aluno
    for tt in turmas:
        if tt['codigo'] == turma['codigo']:
            if aluno['cpf'] not in tt.get('alunos', []):
                tt.setdefault('alunos', []).append(aluno['cpf'])
                salvar_turmas(turmas)
                print(f"✅ Aluno {aluno['nome']} vinculado à turma {tt['codigo']} da matéria '{materia['nome']}'.")
                time.sleep(1)
                return
            else:
                print("Aluno já matriculado nesta turma.")
                return

