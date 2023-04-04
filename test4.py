import socket
import urllib.parse
import os.path
import mapping
import re
HOST, PORT = '', 8080
SAFE_DIR = '/webserver/datahtml'

# Create a socket object
listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Re-use the socket
listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind to the address and port
listen_socket.bind((HOST, PORT))

# Start listening for incoming connections
listen_socket.listen(1)

print('Serving HTTP on port %s ...' % PORT)


def validate_url(url):
    """Validate that the given URL is safe and within the safe directory."""
    parsed_url = urllib.parse.urlparse(url)
    if parsed_url.scheme not in ['http', 'https']:
        return False
    if not parsed_url.netloc:
        return False
    path = parsed_url.path.lstrip('/')
    safe_path = os.path.join(SAFE_DIR, path)
    if not os.path.abspath(safe_path).startswith(SAFE_DIR):
        return False
    return True


def get_link(request_data_bytes):
    """Extract the requested URL from the request data."""
    request_data_str = request_data_bytes.decode('utf-8')
    link_regex = r"(?P<url>https?://[^\s]+)"
    match = re.search(link_regex, request_data_str)
    if match:
        url = match.group("url")
        if validate_url(url):
            return url
    return None


while True:
    # Wait for a connection
    client_connection, client_address = listen_socket.accept()

    # Get the request data from the client
    request_data = client_connection.recv(1024)
    request_url = get_link(request_data)

    if not request_url:
        # Invalid URL, return a 400 Bad Request error
        response_body = '400 Bad Request'
        response_header = 'HTTP/1.1 400 Bad Request\nContent-Type: text/plain\nContent-Length: %d\n\n' % len(response_body)
        response = response_header + response_body
    else:
        # Look up the requested URL in the mapping dictionary
        try:
            file_path = mapping.mappings[request_url]
            safe_file_path = os.path.join(SAFE_DIR, file_path.lstrip('/'))
            with open(safe_file_path, "r") as f:
                r = f.read()
            response_body = r
            response_header = 'HTTP/1.1 200 OK\nContent-Type: text/html\nContent-Length: %d\n\n' % len(response_body)
            response = response_header + response_body
        except KeyError:
            # URL not found in mapping dictionary, return a 404 Not Found error
            response_body = '404 Not Found'
            response_header = 'HTTP/1.1 404 Not Found\nContent-Type: text/plain\nContent-Length: %d\n\n' % len(response_body)
            response = response_header + response_body

    # Send the response to the client
    client_connection.sendall(response.encode())

    # Close the client connection
    client_connection.close()
