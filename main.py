import socket
import threading


def start_server():
    while True:
        host = input("Введите IP сервера или введите 'stop': ")
        if host == "stop":
            return
        port = input("Введите порт сервера или введите 'stop': ")
        if port == "stop":
            return
        try:
            port = int(port)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as test_socket:
                test_socket.bind((host, port))
            break
        except ValueError:
            print("Пожалуйста, введите корректный номер порта.")
        except OSError:
            print(f"Порт {port} уже используется. Пожалуйста, выберите другой порт.")

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Сервер запущен на {host}:{port}.")

    clients = []

    def handle_client(client_socket, client_address, username):
        print(f"Клиент {username} подключился.")
        broadcast_message(f"{username} присоединился к чату.", client_socket)

        while True:
            try:
                message = client_socket.recv(1024).decode('utf-8')
                if not message:
                    break
                print(f"{client_address} [{username}] {message}")
                broadcast_message(f"{username}: {message}", client_socket)
            except ConnectionResetError:
                break
        print(f"Клиент {username} отключился.")
        clients.remove(client_socket)
        broadcast_message(f"{username} покинул чат.", client_socket)
        client_socket.close()

    def broadcast_message(message, sender_socket):
        for client in clients:
            if client != sender_socket:
                try:
                    client.send(message.encode('utf-8'))
                except:
                    clients.remove(client)

    def accept_clients():
        while True:
            client_socket, client_address = server_socket.accept()
            username = client_socket.recv(1024).decode('utf-8')
            clients.append(client_socket)
            threading.Thread(target=handle_client, args=(client_socket, client_address, username)).start()

    threading.Thread(target=accept_clients, daemon=True).start()

    try:
        while True:
            command = input("Введите 'stop' для завершения работы сервера:\n")
            if command.lower() == 'stop':
                break
    finally:
        server_socket.close()
        print("Сервер остановлен.")


def start_client():
    while True:
        host = input("Введите IP-адрес сервера: ")
        port = input("Введите порт сервера: ")
        user_ip = input("Введите IP-адрес пользователя: ")
        username = input("Введите имя пользователя: ")

        try:
            port = int(port)
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.bind((user_ip, 0))
            client_socket.connect((host, port))
            client_socket.send(username.encode('utf-8'))
            print(f"Подключено к серверу {host}:{port}.")
            break
        except ValueError:
            print("Пожалуйста, введите корректный номер порта.")
        except ConnectionRefusedError:
            print(f"Не удалось подключиться к серверу {host}:{port}. Убедитесь, что сервер запущен.")
        except OSError:
            print("Ошибка при подключении. Проверьте IP-адрес и порт.")

    def receive_messages():
        while True:
            try:
                message = client_socket.recv(1024).decode('utf-8')
                if not message:
                    print("Соединение с сервером потеряно.")
                    break
                print(message)
            except ConnectionResetError:
                print("Соединение с сервером потеряно.")
                break
        client_socket.close()

    threading.Thread(target=receive_messages, daemon=True).start()

    try:
        while True:
            message = input()
            if message.lower() == 'exit':
                break
            client_socket.send(message.encode('utf-8'))
    finally:
        client_socket.close()
        print("Клиент завершил работу.")


if __name__ == "__main__":
    print("Выберите сущность: 1 - Сервер, 2 - Клиент, 3 - Выход")
    while True:
        mode = input()
        if mode == "1":
            start_server()
            break
        elif mode == "2":
            start_client()
            break
        elif mode == "3":
            break
        else:
            print("Некорректный выбор, пожалуйста, выберите 1 или 2 или 3.")