import os
import random
import socket
import datetime
import getpass
import csv


HOST = '127.0.0.1'
PORT = 64000
key = str(random.randint(99999, 10000001))

listening = True



help_com = ['listen - прослушивание порта', 'quit - отключение', 'logs - логи']




info_users = 'users_Data.csv'


log_file = 'log.txt'


log_info = {1: 'Сервер запустился', 2: 'Сервер выключен', 3: 'Соединение установлено', 4: 'Прослушивание порта',
                5: 'Изменение порта',
                6: 'Получение данных', 7: 'Отправка', 8: 'Соединение с клиентом прервано',
                9: 'Логи', 10: 'список команд',
                11: 'Повторная попытка ввода пароля'}

class Server():

    def __init__(self, using_right_now, host):
        self.using_right_now = using_right_now
        self.host = host


    @staticmethod
    def identify_users(ip, sock):
        comm = []
        with open(info_users) as file:
            reader = csv.reader(file, delimiter=',')
            for row in reader:
                comm.append(row)
        for i, row in enumerate(comm):
            if row[0] == ip:
                if row[3] == 'True':
                    sock.send(f'здравствуйте, {row[1]}'.encode())
                    break
                else:
                    count_pass = 1
                    while True:
                        sock.send(f'check {row[1]}'.encode())
                        answer = sock.recv(1024).decode()
                        data = Server.code(row[4], answer)
                        if data == row[2]:
                            sock.send(f'здравствуйте, {row[1]}'.encode())
                            comm[i][3] = 'True'
                            break
                        else:
                            if count_pass == 3:
                                Server.create_log(8)
                                sock.send(f'again {count_pass}'.encode())
                                break
                            count_pass +=1
                            Server.create_log(11)
                            sock.send(f'Введен неправильно пароль, повторите еще'.encode())

                    break
        else:
            sock.send('login'.encode())
            name = sock.recv(1024).decode()
            sock.send('password'.encode())
            password = sock.recv(1024).decode()
            password = Server.code(key, password)
            sock.send(f'здравствуйте, {name}'.encode())
            comm.append([ip, name, password, 'True', key])
        with open(info_users, 'w') as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerows(comm)
    @staticmethod
    def main():
            if info_users in os.listdir(os.getcwd()):
                pass
            else:
                s = open(info_users, 'w')
                s.close()

            used_port = getpass.getpass(prompt="Введите порт: ", stream=None)
            used_port = Server.check(used_port)
            if used_port == False:
                while used_port == False:
                    print('Попробуйте еще раз')
                    used_port = getpass.getpass(prompt="Введите порт: ", stream=None)
                    used_port = Server.check(used_port)
                    if used_port != False:
                        break
            s = Server(used_port, HOST)
            s.commands()

    def commands(self):
            Server.create_log(1)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                while True:
                    try:
                        s.bind((HOST, self.using_right_now))
                        break
                    except:
                        self.change_port(self.using_right_now+1)
                        Server.create_log(5)
                s.listen(5)
                print(f'Прослушивание порта: {self.using_right_now}')
                Server.create_log(4)
                while True:
                    command = input('Введите команду: ')
                    if command == 'help':
                        print(' '.join(Server.help_com))
                        Server.create_log(10)
                    elif command == 'quit':
                        Server.create_log(2)
                        raise SystemExit
                    elif command == 'logs':
                        print('Логи: ')
                        Server.create_log(9)
                        with open(log_file, 'r') as ss:
                            text = ss.read()
                            print(text)

                    elif command == 'listen':
                        print(f'Прослушивание порта: {self.using_right_now}')
                        if listening:
                            try:
                                conn, addr = s.accept()
                                Server.create_log(3)
                                Server.identify_users(addr[0], conn)
                                with conn:
                                    while True:
                                        text = Server.receive_info(conn)
                                        if text == 'exit':
                                            comm = []
                                            # чтение и запись файла
                                            with open(info_users, 'r') as file:
                                                reader = csv.reader(file, delimiter=',')
                                                for i, row in enumerate(reader):
                                                    comm.append(row)
                                                    if row[0] == addr[0]:
                                                        comm[i][3] = 'False'
                                                        break
                                            with open(info_users, 'w') as file:
                                                writer = csv.writer(file, delimiter=',')
                                                writer.writerows(comm)
                                        elif text:
                                            Server.send_info(conn, text)
                                        else:
                                            break
                            except:
                                break
                    elif command != '':
                        print('неверная команда ')
    @staticmethod
    def code(n, m):
            n = n*(len(m)//len(n)) + n[-(len(m) % len(n)):]
            return ''.join(map(chr, [i ^ x for i, x in zip(map(ord, m), map(ord, n))]))


    def user_info(self):
            # хранение данных о пользователей
            if info_users in os.listdir(os.getcwd()):
                pass
            else:
                s = open(info_users, 'w')
                s.close()

    @staticmethod
    def check(used_port):
        try:
            used_port = int(used_port) if used_port != '' else PORT
            used_port = used_port if 1 < used_port < 64000 else PORT
            return used_port
        except:
            return False
        

            
            
    @staticmethod
    def create_log(code):
            with open(log_file, 'a') as file:
                file.write(datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S') + '\t' + log_info[code] + '\n')

    def change_port(self, port):
            self.using_right_now = port




    @staticmethod
    def receive_info(sock):
        masseges = sock.recv(1024)
        if masseges:
            print(masseges.decode('utf-8'))
            text = masseges.decode('utf-8').split('\t')[0]
            Server.create_log(6)
            return masseges
        else:
            Server.create_log(8)
            return False
        

    

if __name__ == '__main__':
    Server.main()