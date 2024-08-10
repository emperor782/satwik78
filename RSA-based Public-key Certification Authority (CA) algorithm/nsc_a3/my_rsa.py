import random
import ast
from datetime import datetime, timedelta

# Helper functions for RSA
def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def modinv(a, m):
    m0, x0, x1 = m, 0, 1
    while a > 1:
        q = a // m
        m, a = a % m, m
        x0, x1 = x1 - q * x0, x0
    return x1 + m0 if x1 < 0 else x1

def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

# RSA keys generation
def generate_rsa_keys(p,q):
    n = p * q
    phi = (p-1) * (q-1)
    e = random.randrange(1, phi)
    while gcd(phi, e) != 1:
        e = random.randrange(1, phi)
    d = modinv(e, phi)
    print(f"Generated RSA keys with  modulus n={n}, public exponent e={e}, private exponent d={d}.")
    return (e, n), (d, n)  # Public key, Private key

def rsa_encrypt(private_or_public_key, plaintext):
    key, n = private_or_public_key
    return [pow(ord(char), key, n) for char in plaintext]

def rsa_decrypt(private_or_public_key, ciphertext):
    key, n = private_or_public_key
    return ''.join(chr(pow(char, key, n)) for char in ciphertext)

class CertificateAuthority:
    def __init__(self,p,q):
        self.public_key,self.private_key = generate_rsa_keys(p,q)
        self.certificates = {}
        self.public_keys = {}
        self.id = 'CA'
        print(f"CA initialized with ID {self.id}.")

    def issue_certificate(self, client_id, public_key):
        now = datetime.now()
        valid_from = now.strftime('%Y-%m-%d %H:%M:%S')
        valid_to = (now + timedelta(days=365)).strftime('%Y-%m-%d %H:%M:%S')
        certificate_info = (client_id, public_key, valid_from, valid_to, self.id)
        
        result_string = '|'.join(str(element) for element in certificate_info)
        
        signed_certificate = rsa_encrypt(self.private_key, result_string)

        certificate = {
            'info': result_string,
            'signed': signed_certificate
        }
        self.certificates[client_id] = certificate
        self.public_keys[client_id] = public_key  # CA stores the public key
        print(f"CA issued certificate for client {client_id}.")
        return certificate  # Encrypt the certificate with CA's public key before sending

    def give_key(self):
        return self.public_key
    
    def get_certificate(self, client_id):
        print(f"CA is providing certificate for client {client_id}.")
        return self.certificates[client_id]

class Client:
    def __init__(self, ca, client_id,p,q):
        self.ca = ca
        self.ca_key = ca.give_key()
        self.client_id = client_id
        self.public_key,self.private_key = generate_rsa_keys(p,q)
        self.certificate = self.ca.issue_certificate(self.client_id, self.public_key)
        self.other_certi = None
        self.other_client_public_key = ""
        print(f"Client {self.client_id} has been created with public key {self.public_key}.")

    def request_certificate(self,other_id):
        self.other_certi = self.ca.get_certificate(other_id)
        print(f"Client {self.client_id} received receiver certificate from CA.")

    def request_public_key(self):
        certi = self.other_certi  
        decry = rsa_decrypt(self.ca_key,certi['signed'])
        
        if(decry == certi['info']): #verify receiver certificate
            split_tuple = tuple(decry.split('|'))
            print("\nreceiver certificate verified")
            self.other_client_public_key = ast.literal_eval(split_tuple[1])
            print(f"other client key = {self.other_client_public_key}\n")
        else:
            print("receiver certificate is not valid\n")

    def send_message(self, to_client_id, message):
        encrypted_message = rsa_encrypt(self.other_client_public_key, message)
        print(f'{self.client_id} sent message to {to_client_id} - {message}')
        return encrypted_message

    def receive_message(self,to_client_id, message, ack_msg, ori_msg):
        decrypted_message = rsa_decrypt(self.private_key, message)
        if(decrypted_message == ori_msg):
            print(f'message-{decrypted_message} recevied to {self.client_id}') #msg received
            ack_message = rsa_encrypt(self.other_client_public_key, ack_msg)
            print(f'{self.client_id} sent ack message to {to_client_id} - {ack_msg}')
            return ack_message
        else:
            print("message not received\n")

    def recv_ack(self, msg):
        dec = rsa_decrypt(self.private_key, msg)
        print(f'ack message-{dec} recevied to {self.client_id}') #ack msg received
        
        
if __name__ == '__main__':
    print("Starting Public Key Infrastructure Simulation...")
    
    input_string = input("Enter p,q for CA: ")
    n1, n2 = map(int, input_string.split())
    if(is_prime(n1)and is_prime(n2)):
        ca = CertificateAuthority(n1,n2)
    else:
        print("try again with orime numbers\n")
    
    str_client1 = input("Enter p,q for alice: ")
    p1, q1 = map(int, str_client1.split())
    if(is_prime(p1)and is_prime(q1)):
        alice = Client(ca, 'Alice',p1,q1)
    else:
        print("try again with prime numbers\n")
    
    str_client2 = input("Enter p,q for Bob: ")
    p2, q2 = map(int, str_client2.split())
    if(is_prime(p2)and is_prime(q2)):
        bob = Client(ca, 'Bob',p2,q2)
    else:
        print("try again with prime numbers\n")
    
    print("\nAlice and Bob request each other's certificates:")
    alice.request_certificate('Bob')
    bob.request_certificate('Alice')

    print("\nAlice and Bob request each other's public keys:")
    alice.request_public_key()  # Alice requests Bob's public key from CA
    bob.request_public_key()  # Bob requests Alice's public key from CA

    print("\nAlice and Bob communicate with each other:")
    for i in range(1, 4):
        message = f"Hello {i} from Alice"
        msg = alice.send_message( 'Bob',message)
        ack = bob.receive_message('Alice', msg, f'ACK {i} from Bob',message)
        alice.recv_ack( ack)
