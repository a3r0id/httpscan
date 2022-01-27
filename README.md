# httpscan
 
### Scan a host for open HTTP ports and gain information about the services present.

### Setup:

> `pip -r requirements.txt`
### Usage:

```
usage: httpscan [-h] [--json] [--all] [--print_headers] [--print_body] [--user_agent USER_AGENT] [--origin ORIGIN]
                [--path PATH] [--http_ports_file HTTP_PORTS_FILE] [--ssl_ports_file SSL_PORTS_FILE]
                [--headers_file HEADERS_FILE] [--add_headers_file ADD_HEADERS_FILE] [--socket_timeout SOCKET_TIMEOUT]
                [--response_timeout RESPONSE_TIMEOUT] [--threads THREADS]
                host

Scan a host for open HTTP ports and gain information about the services present.

positional arguments:
  host                  [Host To Scan] The domain to scan. EX: example.com.

optional arguments:
  -h, --help            show this help message and exit
  --json                [JSON Override] Print raw JSON output instead of shell presentation.
  --all                 [Save All] Print each port's status, not just open ones.
  --print_headers       [Shell] Print HTTP response headers along with existing output.
  --print_body          [Shell] Print HTTP response body along with existing output.
  --user_agent USER_AGENT
                        [Request Header] Arbitrarily set your user-agent request-header. EX: --user_agent="Mozilla/5.0
                        (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103
                        Safari/537.36".
  --origin ORIGIN       [Request Header] Arbitrarily set the origin request-header. EX: --origin="https://example.com".
  --path PATH           [Request Header] Arbitrarily set the path request-header. EX: --path="/".
  --http_ports_file HTTP_PORTS_FILE
                        [Resource] File name of JSON array of HTTP ports to scan. Default:
                        httpscan/resources/http_ports.json.
  --ssl_ports_file SSL_PORTS_FILE
                        [Resource] File name of JSON array of HTTPS ports to scan. Default:
                        httpscan/resources/ssl_ports.json.
  --headers_file HEADERS_FILE
                        [Resource] File name of JSON array of HTTP request headers to use. Default:
                        httpscan/resources/http_headers.json
  --add_headers_file ADD_HEADERS_FILE
                        [Resource] File name of JSON array of HTTP request headers to add to existing headers. Default:
                        httpscan/resources/add_http_headers.json
  --socket_timeout SOCKET_TIMEOUT
                        [Tuning] Timeout in seconds (float) until socket connection establishment effort is aborted.
  --response_timeout RESPONSE_TIMEOUT
                        [Tuning] Timeout in seconds (float) until current socket connection is aborted while waiting for
                        response.
  --threads THREADS     [Tuning] Number of threads to use for scanning. Default: 1.

Example: python3 httpscan.py example.com | python3 httpscan.py -h
```

### Service Tagging:
![](https://github.com/hostinfodev/httpscan/blob/main/img/tagged_services.png?raw=true)

### Example Uses:

`python3 httpscan github.com --all`
![](https://github.com/hostinfodev/httpscan/blob/main/img/all.png?raw=true)

`python3 httpscan github.com --json`
![](https://github.com/hostinfodev/httpscan/blob/main/img/json.png?raw=true)

### Other Uses:

> `python3 httpscan example.com --print_headers --print_body`

> `python3 httpscan example.com --print_headers --print_body --all`

> `python3 httpscan example.com --print_headers --print_body --all --user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36"`

> `python3 httpscan example.com --all --json --user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36"`

> `python3 httpscan example.com --all --json --add_headers_file=moreHeaders.json`

> `python3 httpscan example.com --origin="https://example.com" --path="/test" --all --json`