import logging
import socket
import sys
import ssl
import os
from urllib.parse import urlparse


def retrieve_url(url: object) -> object:
    domain = urlparse(url).netloc
    path = urlparse(url).path
    if path == '':
        path = '/'
    port = check_for_port(domain)
    result = domain.find(':')
    if result != -1:
        domain = domain.split(':', 1)[0]

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as err:
        print("Socket creation failed error: %s", err)

    # creating a default client SSL context
    # placing ca file in cwd
    context = ssl.create_default_context()
    filepath = f'{os.getcwd()}\cacert.pem'
    # context.load_verify_locations(filepath)

    # s = context.wrap_socket(s, server_hostname=domain)
    try:
        s.connect((domain, port))

        request = f'GET {path} HTTP/1.1\r\nHost:{domain}\r\nConnection: close\r\n\r\n'
        s.send(request.encode())

        # receive some data
        response = b''
        while True:
            buf = s.recv(1024)
            if not buf:
                break
            response += buf
    except:
        return None

    # check if we have a redirect response
    #if isRedirect(response):
        #url = get_new_url(response).decode()
        #return retrieve_url(url)



    body = getBody(response)

    if body == b'':
        return None

    result = body
    if isChunked(response):
        result = remove_chunk_size(body)

    return result


def getBody(response):
    if response.find(b'200 OK') == -1:
        return b''
    newstring = response.split(b'\r\n\r\n', 2)
    body = newstring[1]

    return body


def check_for_port(domain):
    result = domain.find(':')
    if result == -1:
        return 80
    else:
        newstring = domain.split(':', 1)
        port = int(newstring[1])
        return port




def remove_chunk_size(body):
    split_body = body.split(b'\r\n')
    length = len(split_body)
    result = b''
    for i in range(length):
        if i % 2 != 0:
            result += split_body[i]
    return result


def isChunked(body):
    if body.find(b'transfer-encoding: chunked') == -1:
        return False
    return True


def isRedirect(response):
    response = response.split(b'\r\n')
    if not response[0].find(b'30') == -1:
        return True
    return False


def get_new_url(data):
    strings = data.split(b'Location: ', 1)
    url = strings[1].split(b'\r\n')[0]
    return url






if __name__ == "__main__":
    print(retrieve_url('http://bombus.myspecies.info/node/24').decode())
