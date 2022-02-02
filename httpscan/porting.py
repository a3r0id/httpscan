from httpparser import parse_http_response
from httprequest import format_http

class ResponseObject(object):
    def __init__(self, content):
        content = content.decode() if type(content) is bytes else content
        self.parsed      = parse_http_response(content)
        self.status_code = self.parsed['status_code']
        self.status_desc = self.parsed['status_desc']
        self.headers     = self.parsed['headers']
        self.body        = self.parsed['body']
        self.notes       = self.parsed['notes']
        
class RequestObject(object):
    def __init__(self, port, host=None, path=None, headers=[], request_verb="GET", httpVersion="HTTP/1.1"):
        self.request = format_http(port, host=host, path=path, headers=headers, request_verb=request_verb, httpVersion=httpVersion)
        
        