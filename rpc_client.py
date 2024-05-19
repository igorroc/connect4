import rpyc
import colorama

import utils.game as game
import utils.terminal as cmd
from utils.ip import get_local_ip

class Connect4Client(rpyc.Service):
    game_over = False
    def on_connect(self, conn):
        self._conn = conn
        self.game_state = None
        self.username = input(
            colorama.Fore.LIGHTCYAN_EX + "Digite seu nome de usuário: " + colorama.Fore.RESET
        )

        try:
            conn.root.add_client(self.username)
            conn.root.join_game(self.username)
            self.wait_for_updates()
            
        except Exception as e:
            if not self.game_over:
                print(
                    colorama.Fore.LIGHTRED_EX +
                    f'\n- Ocorreu um erro: {e}' + colorama.Fore.RESET
                )
        finally:
            print('\n')
            print(colorama.Fore.LIGHTRED_EX + f'- Conexão encerrada com o servidor')
            cmd.clear_terminal_color()
            input("Aperte <Enter> para finalizar...")

    def on_disconnect(self, conn):
        self._conn = None

    def exposed_update_game(self, game_state):
        self.game_state = game_state
        self.render_game()

    def print_players(self):
        opponent = [p for p in self.game_state['players'] if p != self.username][0]
        if self.PLAYER_SYMBOL == 1:
            print(
                colorama.Fore.RED +
                self.username
                + colorama.Fore.RESET +
                " vs " +
                colorama.Fore.YELLOW +
                opponent +
                colorama.Fore.RESET
            )
            print(
                colorama.Fore.RED +
                f"Você é o X"
                + colorama.Fore.RESET
            )
        else:
            print(
                colorama.Fore.YELLOW +
                self.username
                + colorama.Fore.RESET +
                " vs " +
                colorama.Fore.RED +
                opponent +
                colorama.Fore.RESET
            )
            print(
                colorama.Fore.YELLOW +
                f"Você é o O"
                + colorama.Fore.RESET
            )
            
    def render_game(self):
        cmd.clear_screen()
        print()
        game.printTable(self.game_state['table'])
        
        if self.game_state['action'] == 'draw':
            print(
                colorama.Fore.LIGHTYELLOW_EX +
                f"O jogo empatou!"
                + colorama.Fore.RESET
            )
            self.game_over = True
            self._conn.close()
        if self.game_state['action'] == 'winner':
            print(
                colorama.Fore.LIGHTGREEN_EX +
                f"Você venceu o jogo! Parabéns!"
                + colorama.Fore.RESET
            )
            self.game_over = True
            self._conn.close()
        elif self.game_state['action'] == 'loser':
            print(
                colorama.Fore.LIGHTRED_EX +
                f"Você perdeu o jogo! Tente novamente!"
                + colorama.Fore.RESET
            )
            self.game_over = True
            self._conn.close()
        elif self.game_state['action'] == 'invalid_play':
            print(
                colorama.Fore.LIGHTRED_EX +
                f"Jogada inválida! Tente novamente."
                + colorama.Fore.RESET
            )
        elif self.game_state['action'] == 'wait_player' or self.game_state['action'] == 'wait':
            print(f"Aguardando jogadores...")
        elif self.game_state['action'] == 'opponent_turn':
            self.print_players()
            print(f"Aguardando a jogada do oponente...")
        elif self.game_state['action'] == 'play' or self.game_state['action'] == 'invalid_play':
            self.print_players()
                
            isValid = False
            while not isValid:
                position = input(
                    '\n' +
                    colorama.Fore.LIGHTCYAN_EX +
                    "Sua jogada ▶ " + colorama.Fore.RESET
                )
                isValid = self._conn.root.play_move(self.username, position)
                if not isValid:
                    print(
                        colorama.Fore.LIGHTRED_EX +
                        f"Jogada inválida! Tente novamente."
                        + colorama.Fore.RESET
                    )
    
    def exposed_choose_game(self, games):
        print("Partidas:")
        for i, game in enumerate(games):
            if len(game['players']) == 2:
                print(colorama.Fore.RED + f"~: {game['players'][0]} X {game['players'][1]}" + colorama.Fore.RESET)
            else:
                print(colorama.Fore.GREEN + f"{i}: {game['players'][0]}" + colorama.Fore.RESET)
        selected_index = input("\nDigite o índice da partida (aperte <enter> para criar a sua própria): ")
        return selected_index
    
    def wait_for_updates(self):
        try:
            while True:
                self._conn.serve(1)  # Keep the connection alive and serve requests
        except KeyboardInterrupt:
            print('\n')
            print(colorama.Fore.LIGHTRED_EX + '- Conexão encerrada com o servidor' + colorama.Fore.RESET)
            cmd.clear_terminal_color()

    def exposed_set_player_symbol(self, symbol):
        self.PLAYER_SYMBOL = symbol
    
    def exposed_get_player_symbol(self):
        return self.PLAYER_SYMBOL
    
    def exposed_get_username(self):
        return self.username

def main():
    cmd.clear_screen()
    HOST = input("Digite o host que deseja conectar: ") or get_local_ip()
    PORT = input("Digite a porta que deseja conectar: ")
    PORT = int(PORT) if PORT else 3000
    print('Tentando se conectar ao servidor...')
    print(f'HOST: {HOST},PORT:{PORT}')
    cmd.delay_loading(10)
    cmd.clear_screen()

    try:
        rpyc.connect(HOST, PORT, service=Connect4Client)
    except Exception as e:
        print(
            colorama.Fore.LIGHTRED_EX +
            f'\n- Não foi possível se conectar ao servidor. Ele está ativo? Erro: {e}'
        )
        return cmd.clear_terminal_color()



if __name__ == "__main__":
    main()