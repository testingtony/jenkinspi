import socket
from time import sleep
from uerrno import ETIMEDOUT
import ujson


def get_broadcast_address():
    import network

    wlan = network.WLAN(network.STA_IF)
    for i in range(0, 3):
        if wlan.isconnected():
            ifconfig = wlan.ifconfig()
            local_addr = [int(x) & 0xff for x in ifconfig[0].split('.')]
            netmask_addr = [int(x) & 0xff for x in ifconfig[1].split('.')]
            broadcast_addr = [str((x | ~y) & 0xff) for x, y in zip(local_addr, netmask_addr)]
            local_addr = [str(x) for x in local_addr]
            return '.'.join(local_addr), '.'.join(broadcast_addr)
        sleep(3)


def get_mq_address(board_name):
    my_addr, broadcast_addr = get_broadcast_address()
    UDP_PORT = 5005
    MESSAGE = bytes(board_name)

    print("Broadcast {} to {}:{}".format(MESSAGE, broadcast_addr, UDP_PORT))

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    sock.sendto(MESSAGE, (broadcast_addr, UDP_PORT))

    sock.settimeout(4)
    sock.bind((my_addr, UDP_PORT))

    addr = (None,)
    try:
        data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        if data != b'localhost':
            addr=(str(data, 'utf-8'),)
    except OSError as e:
        if e.args[0] != ETIMEDOUT:
            raise
    finally:
        sock.close()

    return addr[0]


if __name__ == '__main__':
    print("{!s}!".format(get_mq_address(b'121212')))
