import socket
import threading
import time
import random

lock_matching = threading.Lock()


class Player:
    def __init__(self, id, connection, client_address, is_waiting):
        self.id = id
        self.connection = connection
        self.client_address = client_address
        self.is_waiting = is_waiting

    def send_matching_info(self):
        self.connection.sendall(
            f'''Your opponent is {self.opponent.id}. Game is getting started!
            \r\n'''.encode()
        )


class Game:
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        #  init empty board
        self.board_content = list(' '*9)
        self.turns = 0


choices = ['X', 'O']


def matching_player(new_player):
    lock_matching.acquire()
    try:
        for player in players:
            if player.is_waiting and player.id != new_player.id:
                new_player.opponent = player
                player.opponent = new_player
                new_player.sign = random.choice(choices)
                player.sign = choices[0] if new_player.sign == choices[1] else choices[1]
                player.is_waiting = new_player.is_waiting = False
                return player
    finally:
        lock_matching.release()
    return None


def handle_client(player):
    player.connection.send(
        b'''Welcome to Tic Tac Toe!\n
        Please wait for another player to join the game ...\r\n''')

    while True:
        if player.is_waiting:
            opponent = matching_player(player)

            if not opponent:
                time.sleep(1)
            else:
                new_game = Game(player, opponent)
                handle_game(new_game)

                return
        else:
            #  if the player has already been matched end the loop
            return


def handle_move(game, active_player, waiting_player):
    active_player.connection.sendall(''.join(game.board_content).encode())
    waiting_player.connection.sendall(''.join(game.board_content).encode())

    active_player.connection.sendall(b'YES\r\n')
    waiting_player.connection.sendall(b'NO\r\n')

    try:
        move = int(active_player.connection.recv(4).decode())
        game.board_content[move-1] = active_player.sign

        game.turns += 1
        print(game.turns)
        if game.turns >= 5:
            result = check_winner(game, active_player)
            if result != -1:
                if result == 0:
                    active_player.connection.sendall(''.join(game.board_content).encode())
                    waiting_player.connection.sendall(''.join(game.board_content).encode())

                    active_player.connection.sendall(b'DRAW\r\n')
                    waiting_player.connection.sendall(b'DRAW\r\n')
                    return True
                elif result == 1:
                    active_player.connection.sendall(''.join(game.board_content).encode())
                    waiting_player.connection.sendall(''.join(game.board_content).encode())

                    active_player.connection.sendall(b'WIN\r\n')
                    waiting_player.connection.sendall(b'LOSE\r\n')
                    return True
        return False

    except TypeError as err:
        #  error
        print(err)


def check_winner(game, player):
    '''1 stands for winner;   0 for draw;
    -1 for result cant be determined yet'''

    winning_moves = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6],
        [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6]
    ]
    board = game.board_content

    for w_move in winning_moves:
        if len(set([board[index] for index in w_move] + [player.sign])) == 1:
            return 1
        elif ' ' not in board:
            return 0
        return -1


def handle_game(game):
    game.player1.send_matching_info()
    game.player2.send_matching_info()

    player1_msg = game.player1.connection.recv(1024).decode().lower()
    player2_msg = game.player2.connection.recv(1024).decode().lower()

    if player1_msg == player2_msg == 'ready':
        print('New game started')
    else:
        print('Error occured')

    while True:
        try:
            if handle_move(game, game.player1, game.player2):
                return
            print('second player turn')
            if handle_move(game, game.player2, game.player1):
                return
            print('first loop end')
        except ValueError as err:
            #  send error message
            return


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.bind(('localhost', 7777))
server_socket.listen(1)

players = []

while True:
    connection, client_address = server_socket.accept()
    new_player = Player(1 + len(players), connection, client_address, True)
    players.append(new_player)
    threading.Thread(target=handle_client, args=(new_player,)).start()

server_socket.close()
