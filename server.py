from socket import *
import threading
import utils.terminal as cmd
import utils.game as game
import colorama
import utils.threads as ServerThreads

HOST = gethostname()
PORT = 55551
MAX_QUEUE = 5
BUFFER_SIZE = 1024

cmd.clear_terminal_color()
cmd.clear_screen()

PORT = int(input("Digite a porta que deseja utilizar: "))

cmd.server_loading()
cmd.clear_screen()

print(
    '↪ Servidor iniciado no host: ' +
    colorama.Back.LIGHTCYAN_EX + colorama.Fore.BLACK + f' {HOST} ' + colorama.Back.RESET + colorama.Fore.RESET
)
print(
    '↪ Utilizando a porta: ' +
    colorama.Back.LIGHTMAGENTA_EX + colorama.Fore.BLACK + f' {PORT} ' + colorama.Back.RESET + colorama.Fore.RESET
)

print('↪ Aguardando conexões...')

server = socket(AF_INET, SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(MAX_QUEUE)

currentClients = []
currentGames = []

while True:
    clientSocket, address = server.accept()
    print(
        colorama.Fore.LIGHTGREEN_EX +
        f'+ Conexão estabelecida com o cliente: {address}'
        + colorama.Fore.RESET
    )
    
    ServerThreads.new_client_instructions(clientSocket, currentGames)

    selectedGame = None

    available_games = {str(i): game for i, game in enumerate(currentGames) if len(game['players']) == 1}

    if(len(available_games) > 0):
        msg = clientSocket.recv(BUFFER_SIZE)
        selectedIndex = msg.decode().split('choose:')[1]
        if(selectedIndex == ''):
            selectedIndex = 0
        else:
            selectedIndex = int(selectedIndex)
            
        if selectedIndex >= len(currentGames) or selectedIndex < 0:
            print(
                colorama.Fore.LIGHTRED_EX +
                f'[ERROR]: Jogo {selectedIndex} não encontrado'
                + colorama.Fore.RESET
            )
            clientSocket.send('not-found'.encode())
            continue

        game.joinPlayerToGame(currentGames, selectedIndex, address)
        print(
            colorama.Fore.LIGHTCYAN_EX +
            f'[NEW_PLAYER]: `{address}` entrou no jogo {selectedIndex}'
            + colorama.Fore.RESET
        )
        clientSocket.send(
            game.sendGameToMessage(currentGames[selectedIndex], 'wait').encode()
        )
        selectedGame = currentGames[selectedIndex]
    else:
        game.createGameTable(currentGames, address)
        clientSocket.send(
            game.sendGameToMessage(currentGames[0], 'wait').encode()
        )
        print(
            colorama.Fore.LIGHTCYAN_EX +
            f'[NEW_GAME]: Jogo {len(currentGames)} criado'
            + colorama.Fore.RESET
        )

    msg = clientSocket.recv(BUFFER_SIZE)
    msg = msg.decode().split('name:')[1]
    print(
        colorama.Fore.LIGHTCYAN_EX +
        '[NEW_USER]: '
        + colorama.Fore.RESET
        + msg
    )

    currentClients.append(
        {"socket": clientSocket, "address": address, "username": msg})
    
    
    if(selectedGame != None):
        clientSocket.send(
            game.sendGameToMessage(selectedGame, 'opponent_turn').encode()
        )
        
        for client in currentClients:
            if client['address'] == selectedGame['players'][0]:
                print(
                    colorama.Fore.LIGHTGREEN_EX +
                    '[GAME_START]: Jogo iniciado'
                    + colorama.Fore.RESET
                )
                client['socket'].send(
                    game.sendGameToMessage(selectedGame, 'play').encode()
                )
                break

    thread = threading.Thread(
        target=ServerThreads.handle_messages, args=[clientSocket, address, currentGames, currentClients])
    thread.start()
