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
        self.board_content = list('0'*9)
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
            game.player1.connection.sendall(''.join(game.board_content).encode())
            game.player2.connection.sendall(''.join(game.board_content).encode())

            game.player1.connection.sendall(b'YES\r\n')
            game.player2.connection.sendall(b'NO\r\n')

            move = int(game.player1.connection.recv(4).decode())
            game.board_content[move-1] = game.player1.sign

            game.player1.connection.sendall(''.join(game.board_content).encode())
            game.player2.connection.sendall(''.join(game.board_content).encode())

            game.player1.connection.sendall(b'NO\r\n')
            game.player2.connection.sendall(b'YES\r\n')

            move = int(game.player2.connection.recv(4).decode())
            print(move)
            game.board_content[move-1] = game.player2.sign

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
