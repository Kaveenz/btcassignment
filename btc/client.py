import socket

server_address = ('localhost', 12000)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def authenticate_user(username, password):
    while True:
        message = f"Authenticate {username} {password}"
        client_socket.sendto(message.encode(), server_address)

        response, _ = client_socket.recvfrom(2048)
        print(response.decode())

        if "authenticated" in response.decode().lower():
            break

        choice = input("Do you want to attempt login again? (yes/no): ")
        if choice.lower() != "yes":
            print("Exiting the program.")
            client_socket.close()
            exit(0)

        username = input("Enter your username: ")
        password = input("Enter your password: ")  


def fetch_transactions(username):
   
    message = f"FetchTransactions {username}"
    client_socket.sendto(message.encode(), server_address)
    
    response, _ = client_socket.recvfrom(2048)
    print(response.decode())  


def make_transaction(username):
    amount_to_transfer = float(input("How much do you want to transfer? "))

    user_tx_id = {'A': 100, 'B': 200, 'C': 300, 'D': 400}

    available_payees = {'A': ['B', 'C', 'D'],
                        'B': ['A', 'C', 'D'],
                        'C': ['A', 'B', 'D'],
                        'D': ['A', 'B', 'C']}

    print("Select a payee:")
    for index, payee in enumerate(available_payees[username]):
        print(f"{index+1}. {payee}")

    payee_option = input("Enter option: ")

    if payee_option.isdigit():
        payee_index = int(payee_option) - 1
        if payee_index in range(len(available_payees[username])):
            payee1 = available_payees[username][payee_index]

            amount_received_payee1 = float(input(f"How much will {payee1} receive? "))
            while amount_received_payee1 > amount_to_transfer:
                print("Amount received by Payee1 cannot be more than the transferring amount.")
                amount_received_payee1 = float(input(f"How much will {payee1} receive? "))

            remaining_amount = amount_to_transfer - amount_received_payee1

            if remaining_amount > 0:
                print("Select a second payee:")
                for index, payee in enumerate(available_payees[username]):
                    if payee != payee1:
                        print(f"{index+1}. {payee}")
                payee2_option = input("Enter option: ")
                if payee2_option.isdigit():
                    payee2_index = int(payee2_option) - 1
                    if payee2_index in range(len(available_payees[username])):
                        payee2 = available_payees[username][payee2_index]
                        amount_received_payee2 = remaining_amount  # Second payee receives remaining amount

                        tx_id = user_tx_id[username]

                        # Send the transaction request to the server
                        message = f"MakeTransaction {username} {amount_to_transfer} {payee1} {amount_received_payee1} {payee2} {amount_received_payee2} {tx_id}"
                        client_socket.sendto(message.encode(), server_address)

                        try:
                            response, _ = client_socket.recvfrom(2048)
                            print(response.decode())
                        except socket.timeout:
                            print("Timeout error: No response from the server. Please try again later.")

                        return
            else:
                payee2 = None
                amount_received_payee2 = 0
                tx_id = user_tx_id[username]

                # Send the transaction request to the server (no second payee)
                message = f"MakeTransaction {username} {amount_to_transfer} {payee1} {amount_received_payee1} {payee2} {amount_received_payee2} {tx_id}"
                client_socket.sendto(message.encode(), server_address)

                try:
                    response, _ = client_socket.recvfrom(2048)
                    print(response.decode())
                except socket.timeout:
                    print("Timeout error: No response from the server. Please try again later.")

                return
    print("Invalid option. Please select a valid payee.")



def display_menu():
    print("Menu:")
    print("1. Make a transaction")
    print("2. Fetch and display the list of transactions")
    print("3. Quit the program")
    choice = input("Enter your choice: ")
    return choice


def main():
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    
    authenticate_user(username, password)

    while True:
        choice = display_menu()
        
        if choice == '1':
            make_transaction(username)
        elif choice == '2':
            fetch_transactions(username)
        elif choice == '3':
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please try again.")

    client_socket.close()

if __name__ == "__main__":
    main()
