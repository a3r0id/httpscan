import socket
from time import time, sleep   

from classes import Opts 
from httprequest import format_http
from httpparser import parse_http_response

def try_port(port):
    closed = {'port': port, 'status': 'closed', 'status_code': None, 'data': None, 'error': ''}  
    try:
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(Opts.socket_timeout)
        s.connect((Opts.host, port))
        time_conn = time()
        s.send(format_http(port))
            
        while True:
            data = s.recv(1024)
            if data:
                s.close()
                parsed = parse_http_response(data.decode())
                break

            else:
                if time() >= time_conn + Opts.response_timeout:
                    try:
                        closed['error'] += "\nClosing connection after exceeding response timeout..."
                        s.close()
                    except Exception as e:
                        closed['error'] += '\n' + str(e)
                    closed['status'] = 'Open - no response'
                    closed['error'] += '\nPort is open but no response.'
                
            sleep(0.1)

        
        return {'port': port, 'status': 'open', 'status_code': parsed['status_code'], 'data': data.decode(), 'status_parsed': parsed}
    
    except Exception as e:
        closed['error'] += str(e) 
        return closed
    