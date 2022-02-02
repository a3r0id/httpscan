from socket import gethostbyname

def ensureIP(ipOrHost):
    tryIp = ipOrHost.split(".")
    if len(tryIp) == 4:
        o = [int(i) for i in tryIp]
        if all(0 <= i <= 255 for i in o):
            return ipOrHost
    return gethostbyname(ipOrHost)
    
    