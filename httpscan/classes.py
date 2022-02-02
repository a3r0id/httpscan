from threading import Lock
from os.path import isfile
from json import JSONDecodeError, load

class Versioning:
    VERSION = '1.0.2'
    URL     = "https://github.com/hostinfodev/httpscan/blob/main/httpscan/version.dat/raw"
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
        Opts.follow_redirects = args.follow_redirects
        Opts.max_redirects    = args.max_redirects
        Opts.silence_updates  = args.silence_updates
        
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
    redirects   = {} # {port: {'redirects': [], 'complete': False}}
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
class Services:
    service_tags = None
class Strings:
    block = "██████"
    logo  = ""
with open('httpscan/resources/service_tags.json', 'r') as f:
    Services.service_tags = load(f)
