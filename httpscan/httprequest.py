from classes import Ports, Opts
from json import load

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