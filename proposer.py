import socket
import sys 

HOST = 'localhost'  
PORT = 5000

proposed_ids = [1]

promises = []

can_replicate = False

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    while True:
        print("-----------status------------")
        print("Received Promises: ", len(promises))
        ch = input("1.Send Prepare Message\n2.Start Replication Phase\nEnter Choice:")

        if ch == "1":
            id = max(proposed_ids)+1
            proposed_ids.append(id)
            data_str = str(id) + "," + "null"

            if not data_str:
                break

            try:
                data_tuple = (int(data_str.split(",")[0]), data_str.split(",")[1])
            except ValueError:
                print("Invalid data format! Please send a tuple like (id,value)")
                continue

            # Convert and send data
            data_string = str(data_tuple).encode()
            s.sendall(data_string)
            print(f"Sent Prepare Message: {data_tuple}")

        elif ch == "2":
            if can_replicate:
                print("Starting replication phase...")
                pid = input("Enter proposal id to replicate: ")
                pid_val = input("Enter value to replicate: ")
                data_str = pid + "," + pid_val

                try:
                    data_tuple = (int(data_str.split(",")[0]), data_str.split(",")[1])
                except ValueError:
                    print("Invalid data format! Please send a tuple like (id,value)")
                    continue

                # Convert and send data
                data_string = str(data_tuple).encode()
                s.sendall(data_string)
                print(f"Deciding On Values: {data_tuple}")
                continue
            else:
                print("Cannot start replication phase. Not enough promises")
                continue

        # Receive response from server
        data = s.recv(1024)
        if data:
            # Decode and print response
            received_tuple = eval(data.decode())
            print(f"Received response: {received_tuple}")
            #updte received promise list
            if received_tuple[1].startswith("value"):
                promises.append({
                    "id" : received_tuple[0],
                    "value" : "null"
                }
            )
            #update if this node can be leader
            if received_tuple[2] == True:
                can_replicate = True
            else:
                can_replicate = False
        else:
            print("No data received from server")

