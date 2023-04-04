import socket
import mapping

HOST, PORT = '', 8080

# Create a socket object
listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Re-use the socket
listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind to the address and port
listen_socket.bind((HOST, PORT))

# Start listening for incoming connections
listen_socket.listen(1)

print('Serving HTTP on port %s ...' % PORT)



import re

def get_link(request_data_bytes):
    request_data_str = request_data_bytes.decode('utf-8')
    link_regex = r"(?P<url>https?://[^\s]+)"
    match = re.search(link_regex, request_data_str)
    if match:
        return match.group("url")
    else:
        return None




while True:
    # Wait for a connection
    client_connection, client_address = listen_socket.accept()
    
    # Get the request data from the client
    request_data = client_connection.recv(1024)
    request_url = get_link(request_data)

    

    with open(mapping.mappings[request_url],"r") as a:
        r = a.read()
    response_body=r

    response_header = 'HTTP/1.1 200 OK\nContent-Type: text/html\nContent-Length: %d\n\n' % len(response_body)
    response = response_header + response_body
    
    # # Send the response to the client
    client_connection.sendall(response.encode())

    # Close the client connection
    client_connection.close()




