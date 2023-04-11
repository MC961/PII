import socket
import mapping
import urllib.parse
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





def get_link(request_data_bytes):
    """Extract the requested URL from the request data."""
    request_data_str = request_data_bytes.decode('utf-8')
    request_lines = request_data_str.split('\n')
    request_line = request_lines[0]
    request_url = request_line.split()[1]
    url = urllib.parse.unquote(request_url).split('?')[0]

    # if url == '/favicon.ico':
    #     return '/'
    # if url == '/images/Software-Engineer.jpg':
    #      return'/'
    return url






while True:
    # Wait for a connection
    client_connection, client_address = listen_socket.accept()
    
    # Get the request data from the client
    request_data = client_connection.recv(1024)
    request_url = get_link(request_data)

    print(request_url)
    
    
    try:
        with open(mapping.mappings[request_url],"r") as a:
            r = a.read()
        response_body=r
        response_header = 'HTTP/1.1 200 OK\nContent-Type: text/html\nContent-Length: %d\n\n' % len(response_body)
        response = response_header + response_body
    except KeyError:
        # URL not found in mappings
        response_body = '404 Not Found'
        response_header = 'HTTP/1.1 404 Not Found\nContent-Type: text/plain\nContent-Length: %d\n\n' % len(response_body)
        response = response_header + response_body
    # # Send the response to the client
    client_connection.sendall(response.encode())

    # Close the client connection
    client_connection.close()




