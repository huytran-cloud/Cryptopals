# giá trị A được gửi đến server không phải là một giá trị ngẫu nhiên như
# thông thường, mà là một giá trị cố định bằng 3*N. Điều này dẫn đến việc
# u và S_c đều bằng 0, bất kể mật khẩu thực sự là gì. Do đó, client
# có thể xác minh mình với server mà không cần biết mật khẩu.
import hashlib
import hmac
import json
import secrets
import socket

from Crypto.Util.number import long_to_bytes

# Consts
BUFFER_SIZE = 1024

# Server and Client consts
N = """00:c0:37:c3:75:88:b4:32:98:87:e6:1c:2d:a3:32:
       4b:1b:a4:b8:1a:63:f9:74:8f:ed:2d:8a:41:0c:2f:
       c2:1b:12:32:f0:d3:bf:a0:24:27:6c:fd:88:44:81:
       97:aa:e4:86:a6:3b:fc:a7:b8:bf:77:54:df:b3:27:
       c7:20:1f:6f:d1:7f:d7:fd:74:15:8b:d3:1c:e7:72:
       c9:f5:f8:ab:58:45:48:a9:9a:75:9b:5a:2c:05:32:
       16:2b:7b:62:18:e8:f1:42:bc:e2:c3:0d:77:84:68:
       9a:48:3e:09:5e:70:16:18:43:79:13:a8:c3:9c:3d:"""

N = int("".join(N.split()).replace(":", ""), 16)
g, k = 2, 3

# server connection params
HOST = "localhost"
PORT = 9999


def hash_func(*args) -> int:
    """A one-way hash function."""
    a = ":".join(str(a) for a in args)
    return int(hashlib.sha256(a.encode("utf-8")).hexdigest(), 16)


def normal_connection(password):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        # CLIENT to SERVER: Send I, A=g**a % N
        print("\nSend username I and public ephemeral value A to the server")
        a = secrets.randbits(1024)
        A = pow(g, a, N)
        s.sendall(json.dumps({'I': I, 'A': A}).encode('utf-8'))
        print(f"{I = }\n{A = }")

        # Receive salt and B from server
        data = json.loads(s.recv(BUFFER_SIZE).decode('utf-8'))
        salt, B = data['salt'], data['B']

        # BOTH: Compute string uH = SHA256(A|B), u = integer of uH
        print("\nClient and server calculate the random scrambling parameter")
        u = hash_func(A, B)
        print(f"{u = }")

        # CLIENT:
        print("\nClient computes session key")
        x = hash_func(salt, P)
        S_c = pow(B - k * pow(g, x, N), a + u * x, N)
        K_c = hash_func(S_c)
        print(f"{S_c = }\n{K_c = }")

        # send verification to server
        client_verification = hmac.digest(key=long_to_bytes(K_c), msg=long_to_bytes(salt), digest='sha256')
        s.sendall(client_verification)

        # receive server response
        verification_response = s.recv(BUFFER_SIZE)
        if verification_response == b'User authenticated.':
            return True
        else:
            return False


def attack_1() -> bool:
    """ Log in without password using 0 as the A value """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        # CLIENT to SERVER: Send I, A=g**a % N
        print("\nSend username I and public ephemeral value A to the server")
        A = 3*N
        s.sendall(json.dumps({'I': I, 'A': A}).encode('utf-8'))
        print(f"{I = }\n{A = }")

        # Receive salt and B from server
        data = json.loads(s.recv(BUFFER_SIZE).decode('utf-8'))
        salt, B = data['salt'], data['B']

        # BOTH: Compute string uH = SHA256(A|B), u = integer of uH
        print("\nClient and server calculate the random scrambling parameter")
        u = hash_func(A, B)
        print(f"{u = }")

        # CLIENT:
        print("\nClient computes session key")
        S_c = 0
        K_c = hash_func(S_c)
        print(f"{S_c = }\n{K_c = }")

        # send verification to server
        client_verification = hmac.digest(key=long_to_bytes(K_c), msg=long_to_bytes(salt), digest='sha256')
        s.sendall(client_verification)

        # receive server response
        verification_response = s.recv(BUFFER_SIZE)
        if verification_response == b'User authenticated.':
            return True
        else:
            return False


if __name__ == '__main__':
    I = 'Unbreakable@key.com'
    P = 'StrongPassword'

    passed1 = normal_connection(P)
    print(f'{passed1=}')

    passed2 = attack_1()
    print(f'{passed2=}')
