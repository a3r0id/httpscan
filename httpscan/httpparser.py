from htmlparser import parseHTML

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
        #print("\n\n\nODD RESPONSE:\n")
        #print(string)
        #print("\n\n\n")
            
        return dict(
            status_code=0,
            status_desc="unknown",
            headers = [],
            body="",
            notes=["Non-HTTP response"]
        )   