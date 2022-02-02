from colorama import Fore, Style
from requestengine import RequestEngine
from classes import Opts, Strings
"""[response.*]
        self.port         = port
        self.host         = host
        self.path         = path
        self.headers      = headers
        self.request_verb = request_verb
        self.httpVersion  = httpVersion
        
        self.is_redirect  = is_redirect
        
        self.request      = RequestObject(self.port, host=self.host, path=self.path, headers=self.headers, request_verb=self.request_verb, httpVersion=self.httpVersion)
        
        self.sock         = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        self.sock.settimeout(Opts.socket_timeout)
        
        self.response     = None
        
        self.raw          = None
        
        self.timer        = Timer()
        
        self.redirects    = []
"""

"""[response.response.parsed]
        status_code=status_code,
        status_desc=status_desc,
        headers = headers,
        body=body,
        notes=notes
"""

def print_result(request):
    assert(type(request) == RequestEngine)
    if request.response:
        parsed = request.json()['response']
        print(Style.RESET_ALL)
        print(Fore.GREEN + Strings.block + ' ' + str(request.port) + ' ' + Strings.block + Style.RESET_ALL)
        print("\n[+] Port " + str(request.port) + " has a service running!")
        print("[i] Status code: {}".format(parsed['status_code']))
        print("[i] Status description: {}".format(parsed['status_desc']))
        print("[i] Notes: {}".format(parsed['notes']))
        
        if Opts.print_headers:
            print(Fore.YELLOW + "\n[i] Headers:" + Style.RESET_ALL)
            for header in parsed['headers']:
                print(Style.RESET_ALL)
                print(Fore.CYAN + "{}:\n{}".format(header[0], header[1]) + Style.RESET_ALL)
            print()
            print(Style.RESET_ALL + "\n")
            
        if Opts.print_body:
            try:
                print(Fore.YELLOW + "\n[i] Body:\n" +  Style.RESET_ALL + parsed['body'] + "\n")
            except Exception as e:
                print(Fore.YELLOW + "\n[i] Body:\n[" + Fore.RED + "Error" + Style.RESET_ALL + Fore.YELLOW + "]: " + Style.RESET_ALL + "{}".format(e) + "\n")
                
        if len(request.json()['redirects']):
            print("\n[i] Redirects:")
            print(Fore.YELLOW + f"[GET] ->" + Style.RESET_ALL)
            i = 1
            for redirect in request.redirects:
                url      = redirect['url']
                full_url = url['scheme'] + "://" + url['host'] +":" + str(url['port']) + url['path']
                print(('\t' * i) + Fore.YELLOW + f"[{i}] Redirect: {full_url} -> [{redirect['response']['status_code']}]" + Style.RESET_ALL)
                i += 1
            
    else:
        print(Style.RESET_ALL)
        print(Fore.RED + Strings.block + ' ' + str(request.port) + ' ' + Strings.block)
        
    print(Style.RESET_ALL)
        