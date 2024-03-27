from socket import *
import utils.terminal as cmd
import colorama
import utils.game as game

HOST = gethostname()
PORT = 55551
BUFFER_SIZE = 1024


def main():
    cmd.clear_screen()
    HOST = input("Digite o host que deseja conectar: ")
    PORT = int(input("Digite a porta que deseja conectar: "))
    print('Tentando se conectar ao servidor...')
    print(f'HOST: {HOST},PORT:{PORT}')
    cmd.delay_loading(10)
    cmd.clear_screen()

    try:
        server = socket(AF_INET, SOCK_STREAM)
        server.connect((HOST, PORT))
    except:
        print(
            colorama.Fore.LIGHTRED_EX +
            '\n- Não foi possível se conectar ao servidor. Ele está ativo?'
        )
        return cmd.clear_terminal_color()

    # Instruções para o cliente
    msg = server.recv(BUFFER_SIZE)
    while msg.decode() != 'start-choose' and msg.decode().startswith('players:') == False:
        print(msg.decode())
        msg = server.recv(BUFFER_SIZE)

    CURRENT_GAME = None
    if(msg.decode() == 'start-choose'):
        CURRENT_GAME = input(
            colorama.Fore.LIGHTCYAN_EX + " ▶ " + colorama.Fore.RESET
        )
        server.send(f'choose:{CURRENT_GAME}'.encode())
        msg = server.recv(BUFFER_SIZE)
        if msg.decode() == 'not-found':
            print(
                colorama.Fore.LIGHTRED_EX +
                '- Jogo não encontrado. Tente novamente mais tarde'
            )
            server.close()
            return cmd.clear_terminal_color()
        else:
            GAME = game.getGameFromMessage(msg.decode())
            print(
                colorama.Fore.LIGHTGREEN_EX +
                '+ Conectado ao jogo ' + CURRENT_GAME
            )
    else:
        GAME = game.getGameFromMessage(msg.decode())
        print(
            colorama.Fore.LIGHTGREEN_EX +
            '+ Conectado a um novo jogo'
        )

    print("\n")
    print("Digite seu nome de usuário:")
    USER = input(
        colorama.Fore.LIGHTCYAN_EX + " ▶ " + colorama.Fore.RESET
    )
    server.send(f'name:{USER}'.encode())

    # Loop de interação com o servidor
    while msg.decode() != 'close':
        cmd.clear_screen()
        print(f"Jogo -> {USER} x INIMIGO 2\n")
        game.printTable(GAME['table'])
        position = input(
            colorama.Fore.LIGHTCYAN_EX +
            " Sua jogada ▶ " + colorama.Fore.RESET
        )
        server.send(f'{USER}:{position}'.encode())

        msg = server.recv(BUFFER_SIZE)
        if msg.decode() != 'close':
            GAME = game.getGameFromMessage(msg.decode())
        

    print('\n')
    print(colorama.Fore.LIGHTRED_EX + f'- Conexão encerrada com o servidor')
    server.close()
    cmd.clear_terminal_color()
    input("Aperte <Enter> para finalizar...")


main()
