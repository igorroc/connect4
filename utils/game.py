import colorama

def createGameTable(currentGames, player):
    currentGames.append({
        'players': [player],
        'table': [[0 for i in range(7)] for j in range(6)]
    })

def joinPlayerToGame(currentGames, index, player):
    if index >= len(currentGames):
        return False
    currentGames[index]['players'].append(player)
    return True

# exemplo de mensagem: 
# table:0,0,0,0,0,0,0;0,0,0,0,0,0,0;0,0,0,0,0,0,0;0,0,0,0,0,0,0;0,0,0,0,0,0,0;0,0,0,0,0,0,0;
def getGameTableFromMessage(message):
    table = message.split('table:')[1].split(';')
    table = [list(map(int, i.split(','))) for i in table if i]
    return table

def sendGameTableToMessage(game):
    message = 'table:'
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