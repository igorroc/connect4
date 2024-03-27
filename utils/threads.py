import colorama
import time
import utils.game as game

BUFFER_SIZE = 1024

# tipo de currentGames é uma lista de dicionarios
# com os campos 'players' e 'table'

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
    available_games = {str(i): game for i, game in enumerate(currentGames) if len(game['players']) == 1}
    if(len(available_games) > 0):
        clientSocket.send(
            f'Existem {len(available_games)} jogos em andamento.'.encode()
        )
        time.sleep(0.2)
        options = 'Escolha o ID do jogo que deseja entrar: '
        options += ', '.join(available_games.keys())
        clientSocket.send(options.encode())
        time.sleep(0.4)
        clientSocket.send(
            f'Deixe em branco para criar sua própria partida.'.encode()
        )
        clientSocket.send('start-choose'.encode())
    else:
        clientSocket.send(
            'Não existem jogos disponíveis em andamento.'.encode()
        )
        time.sleep(0.2)
        clientSocket.send(
            'Estamos criando um novo jogo para você!'.encode()
        )
        time.sleep(0.2)
        

def handle_messages(connection, address, currentGames, currentClients):
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
            for _game in currentGames:
                if address in _game['players']:
                    _game['players'].remove(address)
                    break
            for _client in currentClients:
                if _client['address'] == address:
                    currentClients.remove(_client)
                    break
            connection.send('close'.encode())
            connection.close()
            break

        playerGame = None
        for _game in currentGames:
            if address in _game['players']:
                playerGame = _game
                break
        
        if playerGame == None:
            connection.send('close'.encode())
            connection.close()
            break
        
        
        currentPlayer = game.checkCurrentPlayer(playerGame['table']) # 1 or 2
        
        if currentPlayer == 1 and playerGame['players'][0] != address:
            connection.send('close'.encode())
            connection.close()
            break
        if currentPlayer == 2 and playerGame['players'][1] != address:
            connection.send('close'.encode())
            connection.close()
            break

        validPlay = game.play(playerGame['table'], currentPlayer, msg)
        
        if not validPlay:
            connection.send(
                game.sendGameToMessage(playerGame, 'invalid_play', currentClients).encode()
            )
            continue
        
        print(
            colorama.Fore.LIGHTMAGENTA_EX
            + '[GAME_PLAY]: ' + colorama.Fore.RESET +
            colorama.Fore.LIGHTCYAN_EX
            + f'@{user} ' + colorama.Fore.RESET + colorama.Style.DIM
            + f'\'{msg}\' ' + colorama.Style.RESET_ALL
        )
        
        gameWinner = game.checkWinner(playerGame['table'])
        
        # 0 para nenhum ganhador, 1 para player 1 e 2 para player 2
        if gameWinner != 0:
            print(
                colorama.Fore.LIGHTGREEN_EX
                + '[GAME_WINNER]: ' + colorama.Fore.RESET
                + colorama.Fore.LIGHTCYAN_EX
                + f'@{user} ' + colorama.Fore.RESET
                + colorama.Fore.LIGHTGREEN_EX
                + f'venceu o jogo!' + colorama.Fore.RESET
            )
            # remove from currentGames and currentClients
            currentGames.remove(playerGame)
            
            connection.send(
                game.sendGameToMessage(playerGame, 'winner', currentClients).encode()
            )
            for _client in currentClients:
                if _client['address'] in playerGame['players'] and _client['address'] != address:
                    _client['socket'].send(
                        game.sendGameToMessage(playerGame, 'loser', currentClients).encode()
                    )
            break
        
        connection.send(
            game.sendGameToMessage(playerGame, 'opponent_turn', currentClients).encode()
        )
        
        for _client in currentClients:
            if _client['address'] in playerGame['players'] and _client['address'] != address:
                _client['socket'].send(
                    game.sendGameToMessage(playerGame, 'play', currentClients).encode()
                )

    connection.close()
