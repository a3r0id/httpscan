from htmlparser import parseHTML
from classes import Services

def get_from_headers(key, headers):
    for header in headers:
        if key.lower() == header[0].lower():
            return header[1]
    return None

def parse_http_response(string):
    if 'HTTP/1.' in string: # note: this is not a perfect check // Just removed the HTTP/1.1 , now all the HTTP/1.x are accepted
        status_line = string.split('HTTP/1.')[1].split('\r\n')[0][1:]
        status_code = int(status_line.split(' ')[1])
        status_desc = status_line.split()[1] + status_line.split( status_line.split()[1] )[1]
        
        headers     = []
        for header in string.split('\r\n')[1:]:
            if ':' in header and '\r\n' not in header:
                headers.append([header.split(':')[0], header.split(':', 1)[1].strip()])
        
        notes = ""
        notes += "\n> HTTP: " + string[0:8]
        
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
            
        for service in Services.service_tags:
            for tags in Services.service_tags[service]['indicators']:
                if tags in string:
                    notes += '\n> Tagged Service: ' + Services.service_tags[service]['name'] + " (" + Services.service_tags[service]['description'] + ")"
                        
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
        return dict(
            status_code=0,
            status_desc="unknown",
            headers = [],
            body="",
            notes="Non-HTTP response"
        )   