import socket


def draw_board(content):
    if len(content) != 9:
        #  board content len error
        return
    print('Current board:\n')
    print(f'|{content[0]}|{content[1]}|{content[2]}|\n')
    print(f'|{content[3]}|{content[4]}|{content[5]}|\n')
    print(f'|{content[6]}|{content[7]}|{content[8]}|\n')


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_socket.connect(('localhost', 7777))


#  print welcome messag from server
print(client_socket.recv(1024).decode())
#  print match info from server
print(client_socket.recv(1024).decode())

#  confirmation to server that the player is ready to start
client_socket.send(b'ready')

while True:
    board_content = client_socket.recv(16).decode()
    print(board_content)
    draw_board(board_content)
    is_my_turn = client_socket.recv(5).decode().strip()
    print(is_my_turn)

    if is_my_turn == 'YES':
        while True:
            try:
                move = int(input('Your turn! Enter a position (1-9)>>>'))
                if move in range(1, 10):
                    break
            except ValueError as err:
                #  error
                print('Move value have wrong type')

        client_socket.sendall(str(move).encode())
    else:
        print('Wait for the other player move...')


client_socket.shutdown(socket.SHUT_RDWR)
client_socket.close()
