import socket
import mapping
import urllib.parse
import os
import subprocess
HOST, PORT = '', 8080

# Create a socket object
listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Re-use the socket
listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind to the address and port
listen_socket.bind((HOST, PORT))

# Start listening for incoming connections
listen_socket.listen(2)

print('Serving HTTP on port %s ...' % PORT)



def get_link(request_data_bytes):
    """Extract the requested URL and method from the request data."""
    request_data_str = request_data_bytes.decode('utf-8')
    request_lines = request_data_str.split('\n')
    try:
       request_line = request_lines[0]
       request_url = request_line.split()[1]
       method = request_line.split()[0]
    except IndexError:
          # Return 400 Bad Request if request is malformed
         return "400 Bad Request", "<h1>400 Bad Request</h1><p>Your request is malformed.</p>"
    print ("method is:",method)
    url = urllib.parse.unquote(request_url).split('?')[0]
    # if url == '/favicon.ico':
    #     return '/',''
    # else:
    return method, url



def handle_get_request(request_url):
    """Handle a GET request."""
    try:
        file_path = mapping.mappings[request_url]
        if file_path.endswith('.py'):
            response_body = subprocess.check_output(['python', file_path])
            response_header = 'HTTP/1.1 200 OK\nContent-Type: text/plain\nContent-Length: %d\n\n' % len(response_body)
            response = response_header.encode() + response_body
        else:
             with open(mapping.mappings[request_url], 'r') as f:
                response_body = f.read()
                response_header = 'HTTP/1.1 200 OK\nContent-Type: text/html\nContent-Length: %d\n\n' % len(response_body)
                response = response_header.encode() + response_body.encode()
    except KeyError:
        response_body = '404 Not Found'
        response_header = 'HTTP/1.1 404 Not Found\nContent-Type: text/plain\nContent-Length: %d\n\n' % len(response_body)
        response = response_header.encode() + response_body.encode()

    return response






def handle_post_request(request_url, request_data_bytes):
    """Handle a POST request."""
    try:
        with open(mapping.mappings[request_url], 'w') as f:
            f.write(request_data_bytes.decode('utf-8'))
        response_body = "Resource created successfully"
        response_header = 'HTTP/1.1 201 Created\nContent-Type: text/plain\nContent-Length: %d\n\n' % len(response_body)
        response = response_header + response_body
    except KeyError:
        response_body = '404 Not Found'
        response_header = 'HTTP/1.1 404 Not Found\nContent-Type: text/plain\nContent-Length: %d\n\n' % len(response_body)
        response = response_header + response_body
    except:
        response_body = '500 Internal Server Error'
        response_header = 'HTTP/1.1 500 Internal Server Error\nContent-Type: text/plain\nContent-Length: %d\n\n' % len(response_body)
        response = response_header + response_body

    return response


def handle_put_request(request_url, request_body):
    """Handle a PUT request."""
    try:
        with open(mapping.mappings[request_url], 'w') as f:
            f.write(request_body)
        response_body = "Resource updated successfully"
        response_header = 'HTTP/1.1 200 OK\nContent-Type: text/plain\nContent-Length: %d\n\n' % len(response_body)
        response = response_header + response_body
    except KeyError:
        response_body = '404 Not Found'
        response_header = 'HTTP/1.1 404 Not Found\nContent-Type: text/plain\nContent-Length: %d\n\n' % len(response_body)
        response = response_header + response_body
    except:
        response_body = '500 Internal Server Error'
        response_header = 'HTTP/1.1 500 Not Found\nContent-Type: text/plain\nContent-Length: %d\n\n' % len(response_body)
    return response


def handle_delete_request(request_url):
    """Handle a DELETE request."""
    try:
        os.remove(mapping.mappings[request_url])
        response_body = "Resource deleted successfully"
        response_header = 'HTTP/1.1 200 OK\nContent-Type: text/plain\nContent-Length: %d\n\n' % len(response_body)
        response = response_header + response_body
    except KeyError:
        response_body = '404 Not Found'
        response_header = 'HTTP/1.1 404 Not Found\nContent-Type: text/plain\nContent-Length: %d\n\n' % len(response_body)
        response = response_header + response_body
    except:
        response_body = '500 Internal Server Error'
        response_header = 'HTTP/1.1 500 Internal Server Error\nContent-Type: text/plain\nContent-Length: %d\n\n' % len(response_body)
        response = response_header + response_body
        
    return response


while True:
    # Wait for a connection
    client_connection, client_address = listen_socket.accept()

    # Get the request data from the client
    request_data = client_connection.recv(1024)
    method, request_url = get_link(request_data)

    print(method, request_url)

    # Handle the request based on the method
    if method == 'GET':
        response = handle_get_request(request_url)
    elif method == 'POST':
        content_length = request_data.decode('utf-8').split('\n')[-3].split()[1]
        request_data_bytes = b''
        while len(request_data_bytes) < int(content_length):
            request_data += client_connection.recv(1024)
            request_data_bytes = request_data.split(b'\r\n\r\n')[-1]
        response = handle_post_request(request_url, request_data_bytes)
    elif method == 'PUT':
        response = handle_put_request(request_url)
    elif method == 'DELETE':
        response = handle_delete_request(request_url)
    else:
        response_body = "Invalid HTTP method"
        response_header = 'HTTP/1.1 400 Bad Request\nContent-Type: text/plain\nContent-Length: %d\n\n' % len(response_body)
        response = response_header.encode() + response_body.encode()

    # Send the response back to the client
    client_connection.sendall(response)

    # Close the client connection
    client_connection.close()
