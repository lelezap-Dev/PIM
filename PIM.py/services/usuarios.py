# ======= services/usuarios.py =======
import json, os, bcrypt, sys
from utils.validacoes import validar_email, validar_senha, validar_cpf

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
