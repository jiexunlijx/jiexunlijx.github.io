#Example of salt generation and password hashing using HMAC and PBKDF2 according as per IM8 guidelines
import hmac
import hashlib
import getpass
import csv
import secrets
import re

def main():
    #obtain user information. check validity of password.
    """
    Main function to handle user input for username and password, validate password strength,
    and store the salted hash and salt securely. It prompts the user to enter a username and 
    a password twice, checks that the passwords match and meet strength requirements. If valid, 
    it generates a salt and a salted hash using the salting function. The username, salt, 
    salted hash, and number of iterations are then stored in a CSV file for demonstration 
    purposes. Actual implementations should use secure databases for storage.
    """
    username = input("Enter your email ID: ")
    if id_check(username) == False:
        print("Invalid email ID. Please try again.")
        main()
    elif id_check(username) == True:
        pass

    #obtains password from user without echo, checks for password strength
    pwd = userinput(getpass.getpass("Enter your password (min 12 characters, must include numbers and different cases): "))
    pwd2 = userinput(getpass.getpass("Enter your password again: "))
    
    #checking that entered passwords match
    if pwd != pwd2:
        print ("Password does not match. Please start over.")
        main()
    elif pwd == pwd2:
        pass

    #passing checked password into salting function which generates random salt and salted hash for storage
    salt, salted, iterations = salting(pwd)
    print (f'salt:', salt)
    print (f'salted:', salted)
    print (f'No. of iterations:', iterations)

    #writing to csv file as example. Actual implementation would be to write to an encrypted database
    with open("password.csv", "a", newline="") as csvfile:
        #define fieldnames
        writefile = csv.DictWriter(csvfile, fieldnames=["username", "salt", "salted", "iterations"])
        #write row in the new file
        writefile.writerow({
            "username": username, 
            "salt": salt, 
            "salted": salted, 
            "iterations": iterations
        })

def id_check(username: str) -> bool:
    pattern = r"^([A-Z0-9_+\-]+\.?)*[A-Z0-9_+\-]@([A-Z0-9][A-Z0-9\-]*\.)+[A-Z]{2,}$"
    return bool(re.match(pattern, username, re.IGNORECASE))

#checks password strength for minimum length, numbers, and upper and lower cases
def userinput(password_input):
    #change this line for minimum characters
    if len(password_input) < 12:
        print("Password is too short. Minimum 12 characters")
        main()

    #check for numbers
    non_alpha_count = 0
    for char in password_input:
        if not char.isalpha():
            non_alpha_count = non_alpha_count + 1
    if non_alpha_count < 2:
        print("Password has less than 2 numbers. Please try again")
        main()

    #check for upper and lower cases
    upper_count = 0
    lower_count = 0
    for char in password_input:
        if char.isupper():
            upper_count += 1
    if upper_count < 2:
        print("Password has less than 2 upper cases. Please try again")
        main()

    for char in password_input:
        if char.islower():
            lower_count += 1
    if lower_count < 2:
        print("Password has less than 2 lower cases. Please try again")
        main()

    #check for special characters
    special_symbols = "!@#$%^&*()_+-=[]{}|;:'\",.<>?/`~"
    if sum(1 for char in password_input if char in special_symbols) < 2:
        print("Password has less than 2 special characters. Please try again")
        main()

    #return value to main()
    return password_input

def salting(password):
    # Define the output length in bytes
    length = 16

    # Generate a random key and entropy input using secrets module
    key = secrets.token_bytes(32)
    entropy = secrets.token_bytes(32)

    # Create an HMAC object with the key and SHA-256 as the hash function
    hmac_obj = hmac.new(key, digestmod=hashlib.sha256)

    # Update the HMAC object with the entropy input
    hmac_obj.update(entropy)

    # Generate a 128 bit salt by taking the first 16 bytes of the HMAC digest
    salt = hmac_obj.digest()[:length]

    # Define the number of iterations and the output length
    iterations = 1000000
    hash_length = 64

    # Digest the password
    digested = password.encode("utf-8")

    # Generates the salted hash
    salted = hashlib.pbkdf2_hmac("sha256", digested, salt, iterations, hash_length)

    # Return the salt, the salted hash as hexadecimal strings, and the number of iterations
    return salt.hex(), salted.hex(), str(iterations)


if __name__ == "__main__":
    main()