#Exmample of salt generation and password hashing using HMAC and PBKDF2 according as per IM8 guidelines
import hmac
import hashlib
import getpass
import csv
import os

def main():
    #obtain user information. check validity of password.
    username = input("Enter a username: ")

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
    salt, salted = salting(pwd)
    
    #writing to csv file as example. Actual implementation would be to write to an encrypted database
    with open("password.csv", "a") as csvfile:
        #define fieldnames
        writefile = csv.DictWriter(csvfile, fieldnames=["username", "salt", "salted"])
        #write row in the new file
        writefile.writerow({"username": username, "salt": salt, "salted": salted})

#checks password strength for minimum length, numbers, and upper and lower cases
def userinput(a):
    
    #change this line for minimum characters
    if len(a)<12:
        print ("Password is too short. Minimum 12 characters")
        main()

    #check for numbers
    d = 0
    for e in a:
        if e.isalpha() == False:
            d=d+1
    if d == 0:
        print ("Password does not contain numbers. Please try again")
        main()

    #check for upper and lower cases
    d = 0
    g = 0
    for e in a:
        if e.isupper():
            d += 1
    if d == 0 :
        print ("Password does not contain upper cases. Please try again")
        main()

    for f in a:
        if f.islower():
            g += 1
    if g == 0 :
        print ("Password does not contain lower cases. Please try again")
        main()

    #return value to main()
    return a

def salting(password):
    # Define the output length in bytes
    length = 8

    # Generate a random key and entropy input using os.urandom ()
    key = os.urandom(32)
    entropy = os.urandom(32)

    # Create an HMAC object with the key and SHA-256 as the hash function
    hmac_obj = hmac.new(key, digestmod=hashlib.sha256)

    # Update the HMAC object with the entropy input
    hmac_obj.update(entropy)

    # Generate a 64 bit salt by taking the first 8 bytes of the HMAC digest
    salt = hmac_obj.digest()[:length]

    # Define the number of iterations and the output length
    iterations = 100000
    hash_length = 32

    #Digest the password
    digested = password.encode("utf-8")

    #Generates the salted hash
    salted = hashlib.pbkdf2_hmac("sha256", digested, salt, iterations, hash_length)
    return salt, salted


if __name__ == "__main__":
    main()