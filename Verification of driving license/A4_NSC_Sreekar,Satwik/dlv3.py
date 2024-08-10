from datetime import datetime, timedelta
import hashlib
import json
import random


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
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True


# RSA keys generation
def generate_rsa_keys(p, q):
    n = p * q
    phi = (p - 1) * (q - 1)
    e = random.randrange(1, phi)
    while gcd(phi, e) != 1:
        e = random.randrange(1, phi)
    d = modinv(e, phi)
    # print(f"Generated RSA keys with modulus n={n}, public exponent e={e}, private exponent d={d}.")
    return (e, n), (d, n)  # Public key, Private key


# Hash function for generating hash code
def hash_function(data):
    if isinstance(data, str):
        return hashlib.sha256(data.encode()).hexdigest()
    elif isinstance(data, bytes):
        return hashlib.sha256(data).hexdigest()
    else:
        raise ValueError("Input data must be either a string or bytes object.")



# Encryption function using RSA public key
def rsa_encrypt(public_key, plaintext):
    key, n = public_key
    return [pow(ord(char), key, n) for char in plaintext]


# Decryption function using RSA private key
def rsa_decrypt(private_or_public_key, ciphertext):
    key, n = private_or_public_key
    if isinstance(ciphertext, str):
        # Convert string to list of integers
        ciphertext = json.loads(ciphertext)
    return ''.join(chr(pow(char, key, n)) for char in ciphertext)



# Generate RSA key pair for the server (pka1 and puk1)
p1, q1 = 61, 53  # Example prime numbers
server_public_key_1, server_private_key_1 = generate_rsa_keys(p1, q1)

# Generate RSA key pair for the police officer (pka2 and puk2)
p2, q2 = 67, 71  # Example prime numbers
police_public_key_2, police_private_key_2 = generate_rsa_keys(p2, q2)

# Generate RSA key pair for hash code encryption/decryption (Key 3)
p3, q3 = 73, 79  # Example prime numbers
encryption_public_key_3, encryption_private_key_3 = generate_rsa_keys(p3, q3)


# Function to generate encrypted message
def generate_encrypted_message(name, dob, encryption_key):
    # Concatenate name and dob
    data = name.encode() + dob.encode()
    # Generate hash code
    hash_code = hash_function(data)
    # Encrypt hash code using encryption key
    encrypted_message = rsa_encrypt(encryption_key, hash_code)
    return encrypted_message


# Function to register a driver
def register_driver(name, dob):
    # Get current date and time
    current_time = datetime.now()

    # Calculate expiry date (10 years from registration)
    expiry_date = current_time + timedelta(days=3652)  # 10 years assuming leap years

    # Generate encrypted message
    encrypted_message = generate_encrypted_message(name, dob, encryption_public_key_3)

    # Construct license object
    license_info = {
        'name': name,
        'dob': dob,
        'expiry_date': expiry_date.strftime('%Y-%m-%d %H:%M:%S'),
        'encrypted_message': encrypted_message
    }

    return license_info


# # Function to verify license
# def verify_license(data):
#     encrypted_message = data['encrypted_message']

#     # Decrypt the encrypted message using the encryption public key (Key 3)
#     decrypted_message = rsa_decrypt(encryption_private_key_3, encrypted_message)

#     # Generate hash code from name and dob received from the license
#     name = data['name']
#     dob = data['dob']
#     received_data = name + dob
#     received_hash_code = hash_function(received_data)

#     # Compare the received hash code with decrypted hash code
#     if received_hash_code == decrypted_message:
#         # Encrypt the license information with the server's private key (pka1)
#         encrypted_license_info = rsa_encrypt(server_private_key_1, json.dumps(data))
#         return {'message': 'Driver verified', 'encrypted_license': encrypted_license_info}
#     else:
#         return {'message': 'Driver not verified'}

# Function to verify license
# Function to send verification request
def send_verification_request(name, dob, encrypted_message, police_private_key):
    # Encrypt the details with the police officer's private key
    encrypted_details = rsa_encrypt(police_private_key, json.dumps({
        'name': name,
        'dob': dob,
        'encrypted_message': encrypted_message
    }))
    
    # Call the verify_license function with the encrypted details
    response = verify_license(encrypted_details)
    response1 = rsa_decrypt(server_public_key_1,response['encrypted_verification'])
    # Check server response
    print(response1)


# Function to verify license
def verify_license(encrypted_details):
    # Decrypt the message with the police officer's public key
    decrypted_message = rsa_decrypt(police_public_key_2, encrypted_details)

    # Extract the encrypted message in the license info sent by police
    police_data = json.loads(decrypted_message)
    encrypted_message = police_data['encrypted_message']

     # Call the original verification process with the decrypted message and encrypted_message
    response = original_verify_license(police_data, encrypted_message)

    if response['message'] == 'Driver verified':
        # Encrypt the verification message with the server's private key
        response['encrypted_verification'] = rsa_encrypt(server_private_key_1, response['message'])
    elif response['message'] == 'Driver not verified':
        # Encrypt the verification message with the server's private key
        response['encrypted_verification'] = rsa_encrypt(server_private_key_1, response['message'])
        
    return response


def original_verify_license(police_data, encrypted_message):
    # Decrypt the encrypted message using the encryption public key (Key 3)
    decrypted_message = rsa_decrypt(encryption_private_key_3, encrypted_message)

    # Extract the received name and date of birth from police data
    received_name = police_data['name']
    received_dob = police_data['dob']

    # Generate hash code from received name and dob
    received_data = received_name + received_dob
    received_hash_code = hash_function(received_data)

     # Compare the received hash code with decrypted hash code
    if decrypted_message == received_hash_code:
        # Return the verification result
        return {'message': 'Driver verified'}
    else:
        return {'message': 'Driver not verified'}




def register_driver_cli():
    name = input("Enter your name: ")
    dob = input("Enter your date of birth (YYYY-MM-DD): ")
    
    license_info = register_driver(name, dob)

    print("Driver registered successfully!")
    print("License details:")
    print("Name:", license_info['name'])
    print("Date of Birth:", license_info['dob'])
    print("Expiry Date:", license_info['expiry_date'])
    print("Encrypted Message:", license_info['encrypted_message'])


def main():
    while True:
        print("Welcome to the License Verification System!")
        print("Please select an option:")
        print("1) Police Officer")
        print("2) Driver")
        print("3) Exit")

        option = input("Enter your choice (1, 2, or 3): ")

        if option == "1":
            print("You selected Police Officer.")
            name = input("Enter driver's name: ")
            dob = input("Enter driver's date of birth (YYYY-MM-DD): ")
            encrypted_message = input("Enter encrypted message: ")
            send_verification_request(name, dob, encrypted_message,police_private_key_2)
        elif option == "2":
            print("You selected Driver.")
            register_driver_cli()
        elif option == "3":
            print("Exiting the program.")
            break
        else:
            print("Invalid option. Please select 1, 2, or 3.")


if __name__ == "__main__":
    main()