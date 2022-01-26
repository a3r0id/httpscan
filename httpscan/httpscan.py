#!/usr/bin/python3
from genericpath import isfile
from json import JSONDecodeError, dumps, load
import socket
from sys import stdout, argv
from threading import Thread, Lock
from time import sleep
import argparse
from colorama import Fore, Style, init

class Opts:
    def setArgs(args):
        Opts.host             = args.host
        Opts.all              = args.all
        Opts.json             = args.json
        Opts.print_headers    = args.print_headers
        Opts.print_body       = args.print_body
        Opts.user_agent       = args.user_agent
        Opts.add_headers      = [f'User-Agent: {Opts.user_agent}\r\n'] if args.user_agent else []
        Opts.headers_file     = args.headers_file
        
        if not isfile(Opts.headers_file):
            raise FileNotFoundError(f'[-] Error loading HTTP request headers from file: {args.headers_file}')
        with open(Opts.headers_file, 'r') as f:
            try:
                _ = load(f)
            except Exception as e:
                print(e)
                raise JSONDecodeError(f'[-] Error loading HTTP request headers from file: {args.headers_file}')
        
        try:
            with open(args.http_ports_file, 'r') as f:
                Ports.http_ports = load(f)
            if not Opts.json:
                print(f'[+] Loaded HTTP ports from file: {args.http_ports_file}')
        except Exception as e:
            print(e)
            raise Exception(f'[-] Error loading HTTP ports from file: {args.http_ports_file}')
                
        try:
            with open(args.ssl_ports_file, 'r') as f:
                Ports.ssl_ports = load(f)
            if not Opts.json:
                print(f'[+] Loaded SSL ports from file: {args.ssl_ports_file}')  
        except Exception as e:
            print(e)
            raise Exception(f'[-] Error loading SSL ports from file: {args.ssl_ports_file}')      
                
class Ports:
    http_ports  = None
    
    ssl_ports   = None
    
    results     = []
        
LOCK = Lock()

init()

def get_from_headers(key, headers):
    for header in headers:
        if key.lower() == header[0].lower():
            return header[1]
    return None

def parse_http_response(string):
    if 'HTTP/1.1' in string:
        try:
            status_line = string.split('HTTP/1.1')[1].split('\r\n')[0]
            status_code = int(status_line.split(' ')[1])
            status_desc = status_line.split()[1] + status_line.split( status_line.split()[1] )[1]
            
            headers     = []
            for header in string.split('\r\n')[1:]:
                if ':' in header and '\r\n' not in header and '<HTML>' not in header.upper():
                    headers.append([header.split(':')[0], header.split(':', 1)[1].strip()])
            
            notes = ""
            if get_from_headers('Server', headers):
                notes += get_from_headers('Server', headers)
             
            return dict(
                status_code=status_code,
                status_desc=status_desc,
                headers = headers,
                body=string.split('\r\n\r\n')[1],
                notes=notes
            )            
            
        except Exception as e:
            return dict(
                status_code=0,
                status_desc="Error While Parsing HTTP response",
                headers = [],
                error=str(e)
            )            

    else:
        return None

def format_http(port):
    
    line = ['GET / HTTP/1.1', 'Host: ' + Opts.host]
    ssl  = True if port in Ports.ssl_ports else False
    
    with open(Opts.headers_file, 'r') as f: main_headers = load(f)
    
    for header in main_headers:
        line.append(header)
        
    for header in Opts.add_headers:
        line.append(header)
        
    new_line = []
    for l in line:
        if '//scheme//' in header:
            l = l.replace('//scheme//', 'https' if ssl else 'http')    
        if not header.endswith("\r\n"):
            l += "\r\n"    
            
        new_line.append(l)
    
    return str('\r\n'.join(new_line) + "\r\n").encode()
    
def scan():
    
    def thread_worker():
        ports = Ports.http_ports + Ports.ssl_ports
        for port in ports:
            
            result = try_port(port)
            
            if Opts.all:
                Ports.results.append(result)
                if not Opts.json:
                    LOCK.acquire()
                    print_result(result)
                    LOCK.release()      
                    
            else:
                if result['status'] == 'open':
                    Ports.results.append(result)
                    if not Opts.json:
                        LOCK.acquire()
                        print_result(result)
                        LOCK.release()  
                                                        
    T = Thread(target=thread_worker)
    
    T.start()
    
    while True:
        if not T.is_alive():
            if bool(Opts.json):
                print(Ports.results)
                print(dumps(Ports.results))            
            break
        sleep(0.1)
    
def try_port(port):
    slept  = 0
    closed = {'port': port, 'status': 'closed', 'status_code': None, 'data': None}  
    try:
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        s.connect((Opts.host, port))
        http_request = format_http(port)
        s.send(http_request)
            
        while True:
            data = s.recv(1024)
            if data:
                s.close()
                parsed = parse_http_response(data.decode())
                break

            else:
                if slept == 5:
                    s.close()
                    return closed
                
            sleep(0.1)
            slept += 1
        
        return {'port': port, 'status': 'open', 'status_code': parsed['status_code'], 'data': data.decode(), 'status_parsed': parsed}
    
    except Exception as e:
        closed['error'] = str(e) 
        return closed
    
def print_result(port):
    print(Style.RESET_ALL)
    if port['status'] == 'open':
        print(Fore.GREEN + "[|||| " + str(port['port']) + " ||||]" + Style.RESET_ALL)
        print("\n[+] Port " + str(port['port']) + " has a service running!")
        print("[i] Status code: {}".format(port['status_parsed']['status_code']))
        print("[i] Status description: {}".format(port['status_parsed']['status_desc']))
        print("[i] Server: {}".format(port['status_parsed']['notes']))
        
        if Opts.print_headers:
            print(Fore.YELLOW + "\nHeaders:" + Style.RESET_ALL)
            for header in port['status_parsed']['headers']:
                print(Style.RESET_ALL)
                print(Fore.CYAN + "{}:\n{}".format(header[0], header[1]) + Style.RESET_ALL)
            print()
            print(Style.RESET_ALL + "\n")
            
        if Opts.print_body:
            try:
                print(Fore.YELLOW + "\nBody:\n" +  Style.RESET_ALL + port['status_parsed']['body'] + "\n")
            except Exception as e:
                print(Fore.YELLOW + "\nBody:\n[" + Fore.RED + "Error" + Style.RESET_ALL + Fore.YELLOW + "]: " + Style.RESET_ALL + "{}".format(e) + "\n")
            
    else:
        print(Fore.RED + "[|||| " + str(port['port']) + " ||||]")
        print("\n[+] No services on port " + str(port['port']) + '.')
        print("[i] Error: {}".format(port['error'] + Style.RESET_ALL if 'error' in port else 'Unknown' + Style.RESET_ALL))
        
if __name__ == '__main__':
    argp = argparse.ArgumentParser(
        description='Scan a host for open HTTP ports and gain information about the services present.',
        epilog='Example: python3 httpscan.py example.com | python3 httpscan.py -h')
    argp.add_argument('host', help='The domain to scan. EX: example.com.', type=str)
    argp.add_argument('--json', help='Print raw JSON output instead of shell presentation.', action='store_true', default=False)
    argp.add_argument('--all', help='Print each port\'s status, not just open ones.', action='store_true', default=False)
    argp.add_argument('--print_headers', help='Print HTTP response headers along with existing output.', action='store_true', default=False)
    argp.add_argument('--print_body', help='Print HTTP response body along with existing output.', action='store_true', default=False)
    argp.add_argument('--user_agent', 
                      help='Arbitrarily set your user-agent request-header. EX: --user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36".', action='store', 
                      default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36")
    argp.add_argument('--origin',
                    help='Arbitrarily set the origin request-header. EX: --origin="https://example.com".', action='store',
                    default="https://google.com")
    argp.add_argument('--http_ports_file', help='File name of JSON array of HTTP ports to scan. Default: http_ports.json.', action='store', default="http_ports.json")
    argp.add_argument('--ssl_ports_file', help='File name of JSON array of HTTPS ports to scan. Default: ssl_ports.json.', action='store', default="ssl_ports.json")        
    argp.add_argument('--headers_file', help='File name of JSON array of HTTP request headers to use.', action='store', default="http_headers.json")
    args, leftovers = argp.parse_known_args()
    
    Opts.setArgs(args)

    scan()

    

    