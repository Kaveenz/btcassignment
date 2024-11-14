from socket import *

serverName = 'localhost'
serverPort = 12000

serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))
print("The server is ready to receive.")

users = {
    'A': {'password': 'A', 'current_balance': 10},
    'B': {'password': 'B', 'current_balance': 10},
    'C': {'password': 'C', 'current_balance': 10},
    'D': {'password': 'D', 'current_balance': 10}
}


transactions = []

while True:

    message, clientAddress = serverSocket.recvfrom(2048)
    print(f"Received a message from {clientAddress}: {message.decode()}")  

    message_parts = message.decode().split()

    if message_parts[0] == 'Authenticate':
        username = message_parts[1]
        password = message_parts[2]
        print(f"Received an authentication request from user {username}") 

        if username in users and users[username]['password'] == password:
            authenticated = True
            balance = users[username]['current_balance']
            tx_history = []  
            response = f"User {username} is authenticated. Current balance: {balance}. Transaction history: {tx_history}"
            print(f"User {username} is authenticated.") 
        else:
            authenticated = False
            response = "Authentication failed. Invalid username or password."

        serverSocket.sendto(response.encode(), clientAddress)
    

    elif message_parts[0] == 'FetchTransactions':
        username = message_parts[1]
        print(f"Send the list of transactions to user {username}") 
        
        user_transactions = [tx for tx in transactions if tx['payer'] == username or tx['payee'] == username]
        

        response = "List of transactions:\n"
        for tx in user_transactions:
            response += f"TX ID: {tx['id']}, Payer: {tx['payer']}, Amount: {tx['amount']}, Payee: {tx['payee']}\n"

        

        serverSocket.sendto(response.encode(), clientAddress)
    

    elif message_parts[0] == 'MakeTransaction':
        username = message_parts[1]
        amount_to_transfer = float(message_parts[2])

        if len(message_parts) < 4:
            response = "Error: No payee information provided."
            serverSocket.sendto(response.encode(), clientAddress)
            continue

        payee1 = message_parts[3]
        amount_received_payee1 = float(message_parts[4])
        payee2 = message_parts[5] if len(message_parts) > 5 else None
        amount_received_payee2 = float(message_parts[6]) if len(message_parts) > 6 else 0
        print(f"Received a transaction request from user {username}") 

        if payee1 is None and payee2 is None:  # Check if both payees are None
            response = "Error: No payee selected."
            serverSocket.sendto(response.encode(), clientAddress)
            continue

        if payee1 and payee1 not in users:  # Check if payee1 exists
            response = f"Error: Payee {payee1} does not exist."
            serverSocket.sendto(response.encode(), clientAddress)
            continue

        if users[username]['current_balance'] < amount_to_transfer:
            response = f"Error: Insufficient balance. Current balance: {users[username]['current_balance']}"
            serverSocket.sendto(response.encode(), clientAddress)
            continue

        # Update balance for the first payee
        users[username]['current_balance'] -= amount_to_transfer
        users[payee1]['current_balance'] += amount_received_payee1

        # If payee2 exists, update its balance
        if payee2:
            if payee2 not in users:
                response = f"Error: Payee {payee2} does not exist."
                serverSocket.sendto(response.encode(), clientAddress)
                continue
            users[payee2]['current_balance'] += amount_received_payee2

        # Determine transaction ID based on username
        tx_id_prefix = {'A': 100, 'B': 200, 'C': 300, 'D': 400}
        transaction_id = tx_id_prefix.get(username, 0) + len(transactions) + 1  

        transactions.append({
            'id': transaction_id,
            'payer': username,
            'payee': payee1,
            'amount': amount_to_transfer
        })

        response = f"Transaction successful. TX ID: {transaction_id}. Current balance: {users[username]['current_balance']}"
        serverSocket.sendto(response.encode(), clientAddress)




