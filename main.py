from utilities.sender import SecureSender
from utilities.receiver import Receiver

def main():
    role = input("Enter role [sender/receiver]: ").lower()
    
    if role.startswith('s'):
        SecureSender().run()
    elif role.startswith('r'):
        Receiver().run()
    else:
        print("Invalid role")

if __name__ == "__main__":
    main()