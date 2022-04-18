import socket
import urllib.error
import requests
from urllib.request import Request, urlopen
import time

HOST = 'localhost'
PORT = 8001
BUFFER_SIZE = 2048
WEBSITE_REGEX = 'www.'
server_cache = {}

# server implementation using sockets
def main():

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    print(f'Server listening on port {PORT}')

    while True:
        client_connection, client_address = server_socket.accept()
        request = client_connection.recv(BUFFER_SIZE).decode()

        headers = request.split('\n')
        if len(headers) > 1:
            print(f'HEADERS {headers}')
            search = headers[0].split()[1][1:]  # TODO: fix to allow browsers that use proxy settings and passing in URLs like this: www.google.com (as opposed to localhost:8001/www.google.com)
            print(f'URL received: {search}')

            cache_start = time.time()
            if search in server_cache:
                retrieve_from_cache(cache_start, search, client_connection)
            else:
                retrieve_from_http(search, client_connection)

        client_connection.close()


def retrieve_from_http(search, client_connection):
    try:
        url = 'https://' + search
        url_start = time.time()
        content = requests.get(url).text

        if content:
            url_search_duration = time.time() - url_start
            server_cache[search] = insert_notification(content, get_notification(True, url_search_duration))
            client_connection.sendall(('HTTP/1.0 200 OK\n\n' + server_cache[search]).encode())

    except requests.exceptions.RequestException as e:
        print('URLError: {}'.format(e))


def retrieve_from_cache(cache_start, search, client_connection):
    cache_search_duration = time.time() - cache_start
    content = 'HTTP/1.0 200 OK\n\n' + server_cache[search]
    client_connection \
        .sendall(
            insert_notification(
                content,
                get_notification(False, cache_search_duration)).encode()
            )


def get_notification(init, duration):
    return f'<div style="text-align:center; color:green; padding-top:15px">' \
           f'{"Initial" if init else "Cache"} retrieval time: {duration} seconds' \
           f'</div'


def insert_notification(content, notification):
    body_open = '<body'
    body_close = '>'
    start = content.find(body_open)
    if start != -1:
        end = content.find(body_close, start)
        if end != -1:
            print(content[:end+1] + notification + content[end:])
            return content[:end+1] + notification + content[end:]
    return content

# unused
def retry_with_http(site_name):
    try:
        url = 'http://' + site_name
        q = Request(url)
        response = urlopen(q)
        content = response.read().decode('latin-1')
    except urllib.error.URLError as e:
        print('URLError: {}'.format(e))


if __name__ == '__main__':
    main()
