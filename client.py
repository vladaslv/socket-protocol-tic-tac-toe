import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_socket.connect(('localhost', 7777))

while True:
    message = input('Please enter the message or quit to end game:')
    data_out = message.encode()

    client_socket.sendall(data_out)

    if message.lower() == 'quit':
        break

    data_in = client_socket.recv(1024)
    message = data_in.decode()
    print(message)


client_socket.shutdown(socket.SHUT_RDWR)
client_socket.close()
