from classes import Ports, Opts
from json import load

def format_http(port, host=None, path=None, headers=[], request_verb="GET", httpVersion="HTTP/1.1"):
    
    if host == None:
        host = Opts.host
        
    if path == None:
        path = Opts.path
        
    main_headers  = []   
    added_headers = [] 
    if not len(headers):
        with open(Opts.headers_file, 'r') as f:
            main_headers = load(f)
            
        with open(Opts.add_headers_file, 'r') as f:
            added_headers = load(f)      
    else:
        main_headers = headers      
    
    line = [request_verb + " " + path + " " + httpVersion] + main_headers + added_headers # actally [request_line, header, header, ...]
    
    ssl  = True if port in Ports.ssl_ports else False
            
    new_line = [] # Same as $line but formatted
    for l in line:
        
        if '//host//' in l:
            portRef = host
            if port != 80:
                portRef = host + ':' + str(port)
            l = l.replace('//host//', portRef)
        
        if '//scheme//' in l:
            l = l.replace('//scheme//', 'https' if ssl else 'http')    
            
        if '//origin//' in l:
            l = l.replace('//origin//', Opts.origin)
            
        if '//user-agent//' in l:
            l = l.replace('//user-agent//', Opts.user_agent)
            
        if '//path//' in l:
            l = l.replace('//path//', path)
               
        # For user error prevention
        if l.endswith("\r\n"):
            l = l.replace("\r\n", "")    
            
        new_line.append(l)
        
    return_string = str('\r\n'.join(new_line) + "\r\n\r\n")
    
    #print(return_string) # @debug
    
    return return_string.encode()