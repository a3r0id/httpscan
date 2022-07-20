import socket
import ssl
from time                import time, sleep
from urllib.parse        import urlparse

from classes             import Opts, Ports
from httpparser          import get_from_headers
from utils               import ensureIP
from porting             import ResponseObject, RequestObject

# Debugging
# import traceback
# from sys import stdout

class Timer(object):
    def __init__(self):
        """
        A basic timer for awaiting responses
        """
        self.start   = None
        self.end     = None
        self.elapsed = None
        
    def getElapsed(self):
        """
        Set then get the elapsed time since start
        """
        self.end     = time()
        self.elapsed = self.end - self.start
        return self.elapsed
    
    def expired(self):
        """
        Check if the timer has expired
        """
        return bool(self.getElapsed() > Opts.response_timeout)
    
    def engage(self):
        """
        Start the timer
        """
        self.reset()
        self.start = time()
        
    def reset(self):
        """
        Reset the timer
        """
        self.start   = time()
        self.end     = None
        self.elapsed = None        
        
class RequestEngine(object):
    def __init__(self, port, is_redirect=False, host=None, path=None, headers=[], request_verb="GET", httpVersion="HTTP/1.1", scheme="http"):
        
        self.port         = port
        self.host         = host if host else Opts.host
        self.path         = path
        self.headers      = headers
        self.request_verb = request_verb
        self.httpVersion  = httpVersion
        self.scheme       = scheme
        
        self.is_redirect  = is_redirect
        
        self.request      = RequestObject(self.port, host=self.host, path=self.path, headers=self.headers, request_verb=self.request_verb, httpVersion=self.httpVersion)
        
        self.sock         = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        self.sock.settimeout(Opts.socket_timeout)
        
        self.response     = None
        
        self.raw          = None
        
        self.timer        = Timer()
        
        self.redirects    = []

    def checkSocket(self):
        """
        Closes the socket if data is received,
        also mounts the response content to the ResponseObject
        """
        try:
            self.raw = self.sock.recv(1024)
        except:
            try:
                self.sock.close()
            except:
                pass
            return False
        
        if self.raw:
            try:
                self.sock.close()
            except:
                pass
            
            self.response = ResponseObject(self.raw)
            
            # If Redirect
            if self.response.status_code in [301, 302, 303, 307, 308] and Opts.follow_redirects:
                
                redirect        = self.parseRedirect(get_from_headers('Location', self.response.headers))
                
                redirect_object = RequestEngine(
                    redirect['port'],
                    is_redirect=True,
                    host=redirect['host'], 
                    path=redirect['path'],
                    scheme=redirect['scheme']
                )
                
                redirect_object.doRequest()
                
                if redirect_object.response:    
                    # Save to redirects if a response was received
                    self.redirects.append(dict(
                        response    = redirect_object.response.parsed,
                        url         = redirect
                    ))
                else:
                    # Save to redirects if a response was not received
                    self.redirects.append(dict(
                        response    = None,
                        url         = redirect
                    ))                    
     
            return True
        
        return False
                
    def doRequest(self):    
        try:
            ip = ensureIP(self.host)
            
            self.sock.connect((ip, self.port)) ## Error point for initial timeout
            
            self.ssl_context = None
            if self.scheme is not None and "https" in self.scheme or self.port in Ports.ssl_ports:
                self.ssl_context = ssl.create_default_context()
                with self.ssl_context.wrap_socket(
                    self.sock,
                    server_hostname=self.host
                ) as this_sock:
                    this_sock.sendall(self.request.request) ## Error point for SSL attempts
            
            if self.ssl_context is None:
                self.sock.sendall(self.request.request) ## Error point for standard HTTP attempts
        
        except ssl.SSLError:
            #if not Opts.json:
            #    print ("SSL Error: Handshake failed")
            #traceback.print_exc(file=stdout)
            return   
        
        except socket.timeout:
            #if not Opts.json:
            #    print ("Socket Error: Socket timeout")
            #traceback.print_exc(file=stdout)
            return      
        
        except OSError:
            # General socket failure
            return
         
        self.timer.engage()
        
        while True:
            if self.checkSocket():                    
                break
            else:
                if self.timer.expired():
                    break
            sleep(0.1)
            
    def json(self):
        response = self.response.parsed if self.response else None
        return dict(
            response    = response,
            redirects   = self.redirects
        )
            
    @staticmethod
    def parseRedirect(location):
        """
        port = surePort,
        
        host = href.hostname,
        
        path = href.path,
        
        scheme = href.scheme
        
        """
        href = urlparse(location)
        surePort = href.port
        if surePort == None: # When port is not specified, use the default ports | IETF Standard
            if href.scheme == "https":
                surePort = 443
            else:
                surePort = 80       
        return dict(
            port = surePort,
            host = href.hostname,
            path = href.path,
            scheme = href.scheme
        )