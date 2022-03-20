from algosdk import account, encoding

def generate_acc():
    # generate an account
    private_key, address = account.generate_account()
    print("Private key:", private_key)
    print("Address:", address)

    # check if the address is valid
    if encoding.is_valid_address(address):
        print("The address is valid!")
    else:
        print("The address is invalid.")

if __name__ == '__main__':
    generate_acc()