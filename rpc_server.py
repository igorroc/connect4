import rpyc
from rpyc.utils.server import ThreadedServer
import threading
import utils.terminal as cmd
import utils.game as game
import colorama
import utils.threads as ServerThreads
from utils.ip import get_local_ip

cmd.clear_terminal_color()
cmd.clear_screen()

PORT = input("Digite a porta que deseja utilizar: ")
PORT = int(PORT) if PORT else 3000

cmd.clear_screen()
cmd.server_loading()
cmd.clear_screen()

currentClients = []
currentGames = []

class Connect4Service(rpyc.Service):
    def on_connect(self, conn):
        print(
            colorama.Fore.LIGHTGREEN_EX +
            f'+ Conexão estabelecida com o cliente: {conn._channel.stream.sock.getpeername()}'
            + colorama.Fore.RESET
        )
        self._conn = conn

    def on_disconnect(self, conn):
        print(
            colorama.Fore.LIGHTRED_EX +
            f'- Conexão encerrada com o cliente: {conn._channel.stream.sock.getpeername()}'
            + colorama.Fore.RESET
        )
        # Remove client from currentClients
        for client in currentClients:
            if client['conn'] == conn:
                currentClients.remove(client)
                break

    def exposed_add_client(self, username):
        currentClients.append({"conn": self._conn, "username": username})
        print(f"▶ Usuário conectado: {username}")

    def exposed_join_game(self, username, selectedIndex = None):
        available_games = [g for g in currentGames if len(g['players']) == 1]
        if available_games:
            while selectedIndex is None:
                selectedIndex = self._conn.root.choose_game(currentGames)
                if selectedIndex == "":
                    current_game = game.createGameTable(currentGames, username)
                    self._conn.root.set_player_symbol(1)
                    game_state = game.sendGameToMessage(current_game, 'wait', currentClients)
                    game_message = game.getGameFromMessage(game_state)
                    self._conn.root.update_game(game_message)
                    return game_message
                else:
                    try:
                        selectedIndex = int(selectedIndex)
                        if len(currentGames[selectedIndex]['players']) == 2:
                            selectedIndex = None
                    except:
                        selectedIndex = None
            game.joinPlayerToGame(currentGames, int(selectedIndex), username)
            self._conn.root.set_player_symbol(2)
            game_state = game.sendGameToMessage(currentGames[int(selectedIndex)], 'opponent_turn', currentClients)
            game_message = game.getGameFromMessage(game_state)
            self._conn.root.update_game(game_message)
            self.notify_players(int(selectedIndex))
            players = game_message['players']
            print(f"• Jogo iniciado entre " + colorama.Fore.RED + players[0] + colorama.Fore.RESET + " e " + colorama.Fore.YELLOW + players[1] + colorama.Fore.RESET)
            return game_message
        else:
            current_game = game.createGameTable(currentGames, username)
            self._conn.root.set_player_symbol(1)
            game_state = game.sendGameToMessage(current_game, 'wait', currentClients)
            game_message = game.getGameFromMessage(game_state)
            self._conn.root.update_game(game_message)
            return game_message

    def exposed_play_move(self, username, position):
        for g in currentGames:
            if username in g['players']:
                current_player = game.checkCurrentPlayer(g['table'])
                valid_play = game.play(g['table'], current_player, position)
                
                if not valid_play:
                    return False
                
                self.notify_players(currentGames.index(g))
                return True
        return None

    def notify_players(self, game_index):
        try:
            current_player = game.checkCurrentPlayer(currentGames[game_index]['table'])
            connectionMessages = []
            
            game_winner = game.checkWinner(currentGames[game_index]['table'])
            
            for client in currentClients:
                if client['username'] in currentGames[game_index]['players']:
                    try:
                        if len(currentGames[game_index]['players']) == 2:
                            if game_winner != 0 and client['conn'].root.get_player_symbol() == game_winner:
                                action = 'winner'
                            elif game_winner != 0 and client['conn'].root.get_player_symbol() != game_winner:
                                action = 'loser'
                            elif current_player == client['conn'].root.get_player_symbol():
                                action = 'play'
                            else:
                                action = 'opponent_turn'
                            
                            game_state = game.sendGameToMessage(currentGames[game_index], action, currentClients)
                            connectionMessages.append((client['conn'], game.getGameFromMessage(game_state)))

                    except Exception as e:
                        print(colorama.Fore.RED + f"Falha ao notificar {client['username']}: {e}" + colorama.Fore.RESET)

            # grant that the message with action "opponent_turn" is sent first
            connectionMessages.sort(key=lambda x: x[1]['action'] == 'opponent_turn', reverse=True)
            threading.Thread(target=self.send_messages, args=(connectionMessages,game_index,)).start()

        except Exception as e:
            print(colorama.Fore.RED + f"Erro ao notificar: {e}" + colorama.Fore.RESET)

    def send_messages(self, messages, game_index):
        for conn, message in messages:
            try:
                if message['action'] == 'winner' or message['action'] == 'loser':
                    if len(currentGames) > game_index:
                        currentGames.pop(game_index)
                    if message['action'] == 'winner':
                        print(colorama.Fore.GREEN + f"Vencedor: {conn.root.get_username()}" + colorama.Fore.RESET)
                conn.root.update_game(message)
            except Exception as e:
                print(colorama.Fore.RED + f"Erro ao enviar mensagem: {e}" + colorama.Fore.RESET)

if __name__ == "__main__":
    server = ThreadedServer(Connect4Service, port=PORT)
    print(
        '↪ Servidor iniciado no host: ' +
        colorama.Back.LIGHTCYAN_EX + colorama.Fore.BLACK + f' {get_local_ip()} ' + colorama.Back.RESET + colorama.Fore.RESET
    )
    print(
        '↪ Utilizando a porta: ' +
        colorama.Back.LIGHTMAGENTA_EX + colorama.Fore.BLACK + f' {server.port} ' + colorama.Back.RESET + colorama.Fore.RESET
    )
    print('↪ Aguardando conexões...')   
    server.start()
