import threading

from udp_server import UDPCommandServer

UNIX_SOCK_PIPE_PATH_COMMAND_CLIENT = "/tmp/unixsock_command_client.sock"
UNIX_SOCK_PIPE_PATH_COMMAND_SERVER = "/tmp/unixsock_command_server.sock"
UNIX_SOCK_PIPE_PATH_STATUS_CLIENT = "/tmp/unixsock_status_client.sock"
UNIX_SOCK_PIPE_PATH_STATUS_SERVER = "/tmp/unixsock_status_server.sock"
HOST = "127.0.0.1"
# HOST = "169.254.70.55"
COMMAND_PORT = 9999
STATUS_PORT = 9998

if __name__ == '__main__':
    command_server = UDPCommandServer(UNIX_SOCK_PIPE_PATH_COMMAND_SERVER,
                                      UNIX_SOCK_PIPE_PATH_COMMAND_CLIENT,
                                      COMMAND_PORT)

    t1 = threading.Thread(target=command_server.run)

    t1.start()

    t1.join()
