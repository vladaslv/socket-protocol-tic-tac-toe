import socket
import threading


def handle_client(connection):
    connection.sendall(b'Welcome to Tic Tac Toe\r\n')

    while True:
        data_in = connection.recv(1024)
        message = data_in.decode()

        if message.lower() == 'quit':
            break

        print(f'Message from client: {message}')
        connection.sendall(data_in)


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.bind(('localhost', 7777))
server_socket.listen(1)

while True:
    connection, client_address = server_socket.accept()
    threading.Thread(target=handle_client, args=(connection,)).start()

server_socket.close()
