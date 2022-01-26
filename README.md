# httpscan
 
### Scan a host for open HTTP ports and gain information about the services present.

### Usage:

```
Scan a host for open HTTP ports and gain information about the services present.

positional arguments:
  host                  The domain to scan. EX: example.com.

optional arguments:
  -h, --help            show this help message and exit
  --json                Print raw JSON output instead of shell presentation.
  --all                 Print each port's status, not just open ones.
  --print_headers       Print HTTP response headers along with existing output.
  --print_body          Print HTTP response body along with existing output.
  --user_agent USER_AGENT
                        Arbitrarily set your user-agent request-header. EX: --user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)
                        Chrome/73.0.3683.103 Safari/537.36".
  --origin ORIGIN       Arbitrarily set the origin request-header. EX: --origin="https://example.com".
  --http_ports_file HTTP_PORTS_FILE
                        File name of JSON array of HTTP ports to scan. Default: http_ports.json.
  --ssl_ports_file SSL_PORTS_FILE
                        File name of JSON array of HTTPS ports to scan. Default: ssl_ports.json.
  --headers_file HEADERS_FILE
                        File name of JSON array of HTTP request headers to use.

Example: python3 httpscan.py example.com | python3 httpscan.py -h
```


