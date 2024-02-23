import socket
import threading

HOST = 'localhost'  
PORT = 5000        
received_ids = []

BACKLOG = 5

promise_list = []

id_value_pairs = []


def get_conn_of_max_promise():
    max_promise = -1
    max_conn = None
    for promise in promise_list:
        if promise["promise_cnt"] > max_promise:
            max_promise = promise["promise_cnt"]
            max_conn = promise["conn"]

    return max_conn

def handle_client(conn, addr):
    try:
        # Receive and process data from client
        while True:
            data = conn.recv(1024)
            if not data:
                break
            # Receive and unpack the data
            try:
                received_data = eval(data.decode())
                message_id, value = received_data
            except (ValueError, IndexError):
                print("Invalid data format! Please send a tuple like (id,value).")
                continue

            if value == "null": # not in replication phase
                max_conn = get_conn_of_max_promise()
                can_replicate = False
                if max_conn is not None and max_conn == conn:
                    can_replicate = True
                else:
                    can_replicate = False

                processed_data = (message_id, f"value: {value}" , can_replicate)

                #send promise
                if len(received_ids)==0 or (message_id > max(received_ids) and message_id not in received_ids):
                    data_string = str(processed_data).encode()
                    conn.sendall(data_string)

                    # Add received ID to the list
                    received_ids.append(message_id)    
                    #update promise list
                    for promise in promise_list:
                        if promise["conn"] == conn:
                            promise["promise_cnt"] += 1
                            break
                    print(f"Acceptor {addr[1]} sent promise for message with ID {message_id}") 
                #send ignore         
                else:
                    data_string = str((message_id , "Ignored" , can_replicate)).encode()
                    conn.sendall(data_string)
                    print(f"Ignored message with ID {message_id} (not largest)")

            else: #replication phase
                id_value_pairs.append({
                    "id" : message_id,
                    "value" : value
                })
                print(f"Node {addr[1]} decided on id {message_id} value: {value}")

        print(f"Acceptor {addr[1]} disconnected")
    finally:
        conn.close()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(BACKLOG)
    print(f"Server listening on port {PORT}, backlog: {BACKLOG}")

    while True:
        conn, addr = s.accept()
        print(f"Connected by {addr}")
        #acceptor maintains a list of sent promises to decide on leader
        promise_list.append({
                    "conn" : conn,
                    "promise_cnt" : 0
                })

        client_thread = threading.Thread(target=handle_client, args=(conn, addr))
        client_thread.start()


