#!/usr/bin/python3
from ast import Lambda
from genericpath import isfile
from json import JSONDecodeError, dumps, load
import socket
from sys import stdout, argv
from threading import Thread, Lock
from time import sleep, time
import argparse
from colorama import Fore, Style, init
from htmlparser import parseHTML


BLOCK = "██████"

class Opts:
    def setArgs(args):
        Opts.host             = args.host
        Opts.all              = args.all
        Opts.json             = args.json
        Opts.print_headers    = args.print_headers
        Opts.print_body       = args.print_body
        Opts.user_agent       = args.user_agent
        Opts.add_headers_file = args.add_headers_file
        Opts.headers_file     = args.headers_file
        Opts.origin           = args.origin
        Opts.path             = args.path
        Opts.socket_timeout   = args.socket_timeout
        Opts.response_timeout = args.response_timeout
        Opts.threads          = args.threads
        
        if not isfile(Opts.headers_file):
            raise FileNotFoundError(f'[-] Error loading HTTP request headers from file: {args.headers_file}')
        with open(Opts.headers_file, 'r') as f:
            try:
                _ = load(f)
                if not Opts.json:
                    print(f'[+] Loaded HTTP request headers from file: {args.headers_file}')
            except Exception as e:
                print(e)
                raise JSONDecodeError(f'[-] Error loading HTTP request headers from file: {args.headers_file}')
            
        if not isfile(Opts.add_headers_file):
            raise FileNotFoundError(f'[-] Error loading added HTTP request headers from file: {args.add_headers_file}')
        with open(Opts.add_headers_file, 'r') as f:
            try:
                _ = load(f)
                if not Opts.json:
                    print(f'[+] Loaded added HTTP request headers from file: {args.add_headers_file}')
            except Exception as e:
                print(e)
                raise JSONDecodeError(f'[-] Error loading added HTTP request headers from file: {args.add_headers_file}')        
        
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
    pooled      = []
    def establishPool():
        Ports.pooled = Ports.http_ports + Ports.ssl_ports
        Ports.pooled.reverse()
        
class Threads:
    pool = []      
    # Checks if all threads are dead.
    def allDead():
        for thread in Threads.pool:
            if thread.is_alive():
                return False 
        return True
    lock = Lock()

init()

def get_from_headers(key, headers):
    for header in headers:
        if key.lower() == header[0].lower():
            return header[1]
    return None

def parse_http_response(string):
    if 'HTTP/1.1' in string.upper():
        status_line = string.split('HTTP/1.1')[1].split('\r\n')[0]
        status_code = int(status_line.split(' ')[1])
        status_desc = status_line.split()[1] + status_line.split( status_line.split()[1] )[1]
        
        headers     = []
        for header in string.split('\r\n')[1:]:
            if ':' in header and '\r\n' not in header:
                headers.append([header.split(':')[0], header.split(':', 1)[1].strip()])
        
        notes = ""
        if get_from_headers('Server', headers):
            notes += '\n> Server: ' + get_from_headers('Server', headers)
            
        if get_from_headers('X-Powered-By', headers):
            notes += '\n> X-Powered-By: ' + get_from_headers('X-Powered-By', headers)
            
        if get_from_headers('X-AspNet-Version', headers):
            notes += '\n> X-AspNet-Version: ' + get_from_headers('X-AspNet-Version', headers)
            
        if get_from_headers('Content-Length', headers):
            notes += '\n> Content-Length: ' + get_from_headers('Content-Length', headers)         
            
        if get_from_headers('Location', headers):
            notes += '\n> Location: ' + get_from_headers('Location', headers)         
                        
        body = string.split('\r\n\r\n')[1]
        
        if '<html>' in body.lower():
            other_notes = '\n> '.join(parseHTML(body))
            notes += '\n> ' + other_notes
            
        return dict(
            status_code=status_code,
            status_desc=status_desc,
            headers = headers,
            body=body,
            notes=notes
        )            
                      

    else:
        print("\n\n\nODD RESPONSE:\n")
        print(string)
        print("\n\n\n")
            
        return dict(
            status_code=0,
            status_desc="unknown",
            headers = [],
            body="",
            notes=["Non-HTTP response"]
        )       

def format_http(port):
    
    ssl  = True if port in Ports.ssl_ports else False
    
    with open(Opts.headers_file, 'r') as f:
        main_headers = load(f)

    with open(Opts.add_headers_file, 'r') as f:
        added_headers = load(f)
        
    line = main_headers + added_headers # actally [request_line, header, header, ...]
        
    new_line = [] # Same as $line but formatted
    for l in line:
        
        if '//host//' in l:
            portRef = Opts.host
            if port != 80:
                portRef = Opts.host + ':' + str(port)
            l = l.replace('//host//', portRef)
        
        if '//scheme//' in l:
            l = l.replace('//scheme//', 'https' if ssl else 'http')    
            
        if '//origin//' in l:
            l = l.replace('//origin//', Opts.origin)
            
        if '//user-agent//' in l:
            l = l.replace('//user-agent//', Opts.user_agent)
            
        if '//path//' in l:
            l = l.replace('//path//', Opts.path)
            
            
        # For user error prevention
        if l.endswith("\r\n"):
            l = l.replace("\r\n", "")    
            
        new_line.append(l)
    
    return_string = str('\r\n'.join(new_line) + "\r\n\r\n")
    # print(return_string) @debug
    return return_string.encode()
    
def scan():
    
    # Establish candy bucket for threadWorkers
    Ports.establishPool()
    
    if Opts.threads > len(Ports.pooled) / 4: #sanity check
        raise OverflowError(f'[-] Cannot use more than {round(len(Ports.pooled) / 4)} threads (rounded) against your current total of {len(Ports.pooled)} ports. (total ports / 4)')
    
    def thread_worker(thread_id):
        
        try:
            
            while len( Ports.pooled ) > 0:
                
                Threads.lock.acquire()
                try:
                    port = Ports.pooled.pop()
                except: # if we pop from an empty list OR if two threads are trying to pop at the same time (which theoretically should never happen but logically COULD)
                    Threads.lock.release()
                    continue
                
                Threads.lock.release()
                result = try_port(port)
                
                if Opts.all:
                    Ports.results.append(result)
                    if not Opts.json:
                        Threads.lock.acquire()
                        print_result(result)
                        Threads.lock.release()      
                        
                else:
                    if result['status'] == 'open':
                        Ports.results.append(result)
                        if not Opts.json:
                            Threads.lock.acquire()
                            print_result(result)
                            Threads.lock.release()  
                            
        except (KeyboardInterrupt, SystemExit):
            print(f"\n[-] Thread {thread_id} Exiting...")
                                
    for i in range(Opts.threads):                        
        Threads.pool.append(Thread(target=thread_worker, args=(i,)))
        
    i = 0.1
    for t in Threads.pool:
        t.start()
        sleep(i) #sanity check
        i += 0.3
        
    while True:
        try:
            if Threads.allDead():
                if Opts.json:
                    if Opts.all:
                        print(dumps(Ports.results))  
                    else:
                        open_ports = []
                        for result in Ports.results:
                            if result['status'] == 'open':
                                open_ports.append(result)    
                        print(dumps(open_ports))    
                break
            sleep(0.1)            
        except (KeyboardInterrupt, SystemExit):
            print("\n[-] Exiting...")

    
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
    
def print_result(port):
    print(Style.RESET_ALL)
    if port['status'] == 'open':
        print(Fore.GREEN + BLOCK + ' ' + str(port['port']) + ' ' + BLOCK + Style.RESET_ALL)
        print("\n[+] Port " + str(port['port']) + " has a service running!")
        print("[i] Status code: {}".format(port['status_parsed']['status_code']))
        print("[i] Status description: {}".format(port['status_parsed']['status_desc']))
        print("[i] Notes: {}".format(port['status_parsed']['notes']))
        
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
    
    
    elif port['status'] == 'Open - no response':
        print(Fore.BLUE + BLOCK + ' ' + str(port['port']) + ' ' + BLOCK)
        print("\n[+] Port " + str(port['port']) + " seems to be open,\nsocket was established but did not receive any data within the allowed response timeout or the socket was closed by the remote machine.")
        print("[i] Error: {}".format(port['error'] + Style.RESET_ALL if 'error' in port else 'Unknown' + Style.RESET_ALL))        
                
    else:
        print(Fore.RED + BLOCK + ' ' + str(port['port']) + ' ' + BLOCK)
        print("\n[-] No services on port " + str(port['port']) + '.')
        print("[i] Error: {}".format(port['error'] + Style.RESET_ALL if 'error' in port else 'Unknown' + Style.RESET_ALL))
        
if __name__ == '__main__':
    argp = argparse.ArgumentParser(
        description='Scan a host for open HTTP ports and gain information about the services present.',
        epilog='Example: python3 httpscan.py example.com | python3 httpscan.py -h')
    argp.add_argument('host', help='[Host To Scan] The domain to scan. EX: example.com.', type=str)
    argp.add_argument('--json', help='[JSON Override] Print raw JSON output instead of shell presentation.', action='store_true', default=False)
    argp.add_argument('--all', help='[Save All] Print each port\'s status, not just open ones.', action='store_true', default=False)
    argp.add_argument('--print_headers', help='[Shell] Print HTTP response headers along with existing output.', action='store_true', default=False)
    argp.add_argument('--print_body', help='[Shell] Print HTTP response body along with existing output.', action='store_true', default=False)
    argp.add_argument('--user_agent', 
                      help='[Request Header] Arbitrarily set your user-agent request-header. EX: --user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36".', action='store', 
                      default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36")
    argp.add_argument('--origin',
                    help='[Request Header] Arbitrarily set the origin request-header. EX: --origin="https://example.com".', action='store',
                    default="https://google.com")
    argp.add_argument('--path', 
                        help='[Request Header] Arbitrarily set the path request-header. EX: --path="/".', action='store',
                        default="/")
    argp.add_argument('--http_ports_file', help='[Resource] File name of JSON array of HTTP ports to scan. Default: http_ports.json.', action='store', default="http_ports.json")
    argp.add_argument('--ssl_ports_file', help='[Resource] File name of JSON array of HTTPS ports to scan. Default: ssl_ports.json.', action='store', default="ssl_ports.json")        
    argp.add_argument('--headers_file', help='[Resource] File name of JSON array of HTTP request headers to use. Default: http_headers.json', action='store', default="http_headers.json")
    argp.add_argument('--add_headers_file', help='[Resource] File name of JSON array of HTTP request headers to add to existing headers. Default: add_http_headers.json', action='store', default="add_http_headers.json")
    argp.add_argument('--socket_timeout', help='[Tuning] Timeout in seconds (float) until socket connection establishment effort is aborted.', action='store', type=float, default=1.0)
    argp.add_argument('--response_timeout', help='[Tuning] Timeout in seconds (float) until current socket connection is aborted while waiting for response.', action='store', type=float, default=1.0)
    argp.add_argument('--threads', help='[Tuning] Number of threads to use for scanning. Default: 1.', action='store', type=int, default=1)
    args, leftovers = argp.parse_known_args()
    
    Opts.setArgs(args)

    scan()

    

    