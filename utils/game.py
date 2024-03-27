import colorama

def createGameTable(currentGames, connection):
    currentGames.append({
        'players': [connection],
        'table': [[0 for i in range(7)] for j in range(6)]
    })

def joinPlayerToGame(currentGames, index, connection):
    if index >= len(currentGames):
        return False
    currentGames[index]['players'].append(connection)
    return True

def getGameFromMessage(message):
    players = message.split('players:')[1].split(';')[0].split(',')
    table = message.split('table:')[1].split(';')
    return {'players': players, 'table': table}

def sendGameToMessage(game):
    message = 'players:'
    message += ','.join([p[0] for p in game['players']]) + ';'
    message += 'table:'
    for i in game['table']:
        message += ','.join(map(str, i)) + ';'
    return message

def printTable(table):
    print('  1   2   3   4   5   6   7')
    for i in range(6):
        print('┌   ┬   ┬   ┬   ┬   ┬   ┬   ┐')
        print('│', end='')
        for j in range(7):
            if table[i][j] == 0:
                print('   ', end='')
            elif table[i][j] == 1:
                print(colorama.Fore.RED + ' X ' + colorama.Fore.RESET, end='')
            elif table[i][j] == 2:
                print(colorama.Fore.YELLOW + ' O ' + colorama.Fore.RESET, end='')
            print('│', end='')
        print()
    print('└───┴───┴───┴───┴───┴───┴───┘')
    print('\n')
    
def play(table, player, position):
    position = int(position) - 1
    if table[0][position] != 0:
        return 'Coluna cheia! Tente novamente.'
    
    if(position < 0 or position > 6):
        return 'Posição inválida! Tente novamente.'
    
    for i in range(5, -1, -1):
        if table[i][position] == 0:
            table[i][position] = player
            break
    
    return table

def checkWinner(table):
    # horizontal
    for i in range(6):
        for j in range(4):
            if table[i][j] == table[i][j + 1] == table[i][j + 2] == table[i][j + 3] != 0:
                return table[i][j]
    
    # vertical
    for i in range(3):
        for j in range(7):
            if table[i][j] == table[i + 1][j] == table[i + 2][j] == table[i + 3][j] != 0:
                return table[i][j]
    
    # diagonal
    for i in range(3):
        for j in range(4):
            if table[i][j] == table[i + 1][j + 1] == table[i + 2][j + 2] == table[i + 3][j + 3] != 0:
                return table[i][j]
    
    for i in range(3):
        for j in range(3, 7):
            if table[i][j] == table[i + 1][j - 1] == table[i + 2][j - 2] == table[i + 3][j - 3] != 0:
                return table[i][j]
    
    return 0

