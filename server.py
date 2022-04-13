# Pseudocode Implementation
# Infinite Loop that waits for requests
#   If receive request
#       check if resource is in cache
#       if not in cache
#           make request
#       else
#            return the resource from the cache

# should be able to handle requests for HTML pages, images

# Frontend
# add a few buttons to make a request
# user input a request
# should show the amount of time needed to make a request
# show a list of previous attempts to make the request (number, wURL, round-trip time)

import socket
# import urllib.request
import urllib.error
from bs4 import BeautifulSoup
import requests
from requests import adapters
import json
import ssl
from urllib3 import poolmanager
from urllib.request import Request, urlopen

HOST = 'localhost'
PORT = 8001
BUFFER_SIZE = 1024


class TLSAdapter(adapters.HTTPAdapter):

    def init_poolmanager(self, connections, maxsize, block=False):
        """Create and initialize the urllib3 PoolManager."""
        ctx = ssl.create_default_context()
        ctx.set_ciphers('DEFAULT@SECLEVEL=1')
        self.poolmanager = poolmanager.PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_version=ssl.PROTOCOL_TLS,
            ssl_context=ctx)

def main():

    server_cache = {}

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    print(f'Server listening on port {PORT}')

    while True:
        client_connection, client_address = server_socket.accept()
        request = client_connection.recv(BUFFER_SIZE).decode()

        headers = request.split('\n')
        search = headers[0].split()[1][1:]
        print(f'URL received: {search}')
        # print(server_cache)
        if search in server_cache:
            response = 'HTTP/1.0 200 OK\n\n' + server_cache[search]
            client_connection.sendall(response.encode())
        else:
            # get resource
            try:

                # session = requests.session()
                # # session = requests.sessions.Session()
                # session.mount('https://', TLSAdapter())
                # new_http_response = session.get(f'https://{search}')

                # new_http_response = requests.get(f'https://{search}')

                url = 'https://' + search
                q = Request(url)
                response = urlopen(q)

                response_headers = response.info()
                content = response.read().decode('latin-1')
                # print(content)

                # TODO: add logic for file type (binary, text), retrieving images from site
                # TODO: error handling for the urllib3.exceptions.MaxRetryError (only make one request?)
                # response = new_http_response.text
                # print(response)
                # To see returned resource's encoding
                # soup = BeautifulSoup(response, features="html.parser")
                # print(soup.head.meta)

                # add it to cache
                if content:
                    server_cache[search] = content
                    client_connection.sendall(content.encode())

            # except requests.exceptions.RequestException as e:
            except urllib.error.URLError as e:
                print('URLError: {}'.format(e))
                # if e.code == 404:
                #     response = 'HTTP/1.0 404 NOT FOUND\n\nFile Not Found'
                # else:
                #     response = 'HTTP/1.0 500\n\nCould Not Connect To Server'

def retry_with_http(site_name):
    try:
        url = 'http://' + site_name
        q = Request(url)
        response = urlopen(q)
        content = response.read().decode('latin-1')
        print(content)
    except urllib.error.URLError as e:
        print('URLError: {}'.format(e))
# Findings

# www.google.com
# accessing a site often triggers additional requests
# sometimes a DNS server limits request rates; get a URLError:
# URLError: <urlopen error [Errno 8] nodename nor servname provided, or not known>

# www.401games.ca
# URLError: <urlopen error [SSL: SSLV3_ALERT_HANDSHAKE_FAILURE] sslv3 alert handshake failure (_ssl.c:1108)>

# www.walmart.ca
# got a message asking if I'm a bot (webcrawling)




# To Run:
# 1. Run on separate computers
# 2. Run proxy and browser on same computer


if __name__ == '__main__':
    main()
