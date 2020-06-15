import socket
import threading
import time

lock_matching = threading.Lock()


class Player:
    def __init__(self, id, connection, client_address, is_waiting):
        self.id = id
        self.connection = connection
        self.client_address = client_address
        self.is_waiting = is_waiting


def matching_player(new_player):
    lock_matching.acquire()
    try:
        for player in players:
            if player.is_waiting and player.id != new_player.id:
                new_player.match = player
                player.is_waiting = new_player.is_waiting = False
                return player
    finally:
        lock_matching.release()
    return None


def handle_client(player):
    connection.sendall(b'Welcome to Tic Tac Toe\r\n')

    while True:
        if player.is_waiting:
            opponent = matching_player(player)

            if not opponent:
                time.sleep(1)
            else:
                message = 'Your opponent is {}. Game is getting started!\r\n'
                player.connection.sendall(message.format(opponent.id).encode())
                opponent.connection.sendall(message.format(player.id).encode())
        data_in = connection.recv(1024)
        message = data_in.decode()

        if message.lower() == 'quit':
            break

        print(f'Message from client: {message}')
        connection.sendall(data_in)


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.bind(('localhost', 7777))
server_socket.listen(1)

players = []

while True:
    connection, client_address = server_socket.accept()
    new_player = Player(100 + len(players), connection, client_address, True)
    players.append(new_player)
    threading.Thread(target=handle_client, args=(new_player,)).start()

server_socket.close()
