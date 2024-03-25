import colorama
import time
import utils.game as game

BUFFER_SIZE = 1024

def new_client_instructions(clientSocket, currentGames):
    clientSocket.send(
        bytes(
            colorama.Fore.LIGHTGREEN_EX +
            '+ Conexão estabelecida com o servidor', 'utf-8'
        )
    )
    time.sleep(0.2)
    clientSocket.send(
        bytes(colorama.Fore.RESET, 'utf-8')
    )
    clientSocket.send(
        'Bem vindo(a) ao Connect 4!'.encode()
    )
    time.sleep(0.2)
    # filtra pelos jogos que tem apenas 1 jogador
    available_games = list(filter(lambda x: len(x['players']) == 1, currentGames))
    if(len(available_games) > 0):
        clientSocket.send(
            f'Existem {len(available_games)} jogos em andamento.'.encode()
        )
        time.sleep(0.2)
        clientSocket.send(
            f'Escolha o número do jogo que deseja entrar: {available_games.keys()}'.encode()
        )
        time.sleep(0.4)
        clientSocket.send('start-choose'.encode())
    else:
        clientSocket.send(
            'Não existem jogos em andamento.'.encode()
        )
        time.sleep(0.2)
        clientSocket.send(
            'Estamos criando um novo jogo para você!'.encode()
        )
        time.sleep(0.2)
        

def handle_messages(connection, address, currentGames):
    while True:
        msg = connection.recv(BUFFER_SIZE)
        msg = msg.decode().split(':')
        user = msg[0]
        msg = msg[1]

        if msg == 'sair':
            print(
                colorama.Fore.LIGHTRED_EX
                + '[LEFT_USER]: ' + colorama.Fore.RESET
                + f'{user} ' + colorama.Style.DIM
                + f'{address}' + colorama.Style.RESET_ALL
            )
            connection.send('close'.encode())
            connection.close()

            break

        fraseInterpretada = 'test'
        connection.send(fraseInterpretada.encode())
        print(
            colorama.Fore.LIGHTMAGENTA_EX
            + '[REQUEST]: ' + colorama.Fore.RESET +
            colorama.Fore.LIGHTCYAN_EX
            + f'@{user} ' + colorama.Fore.RESET + colorama.Style.DIM
            + f'\'{msg}\' ' + colorama.Style.RESET_ALL
            + colorama.Back.MAGENTA + f' {fraseInterpretada} '
            + colorama.Back.RESET
        )

    connection.close()
