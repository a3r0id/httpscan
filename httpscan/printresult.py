from colorama import Fore, Style

from classes import Opts

BLOCK = "██████"

def print_result(port):
    print(Style.RESET_ALL)
    if port['status'] == 'open':
        print(Fore.GREEN + BLOCK + ' ' + str(port['port']) + ' ' + BLOCK + Style.RESET_ALL)
        print("\n[+] Port " + str(port['port']) + " has a service running!")
        print("[i] Status code: {}".format(port['status_parsed']['status_code']))
        print("[i] Status description: {}".format(port['status_parsed']['status_desc']))
        print("[i] Notes: {}".format(port['status_parsed']['notes']))
        
        if Opts.print_headers:
            print(Fore.YELLOW + "\nHeaders:" + Style.RESET_ALL)
            for header in port['status_parsed']['headers']:
                print(Style.RESET_ALL)
                print(Fore.CYAN + "{}:\n{}".format(header[0], header[1]) + Style.RESET_ALL)
            print()
            print(Style.RESET_ALL + "\n")
            
        if Opts.print_body:
            try:
                print(Fore.YELLOW + "\nBody:\n" +  Style.RESET_ALL + port['status_parsed']['body'] + "\n")
            except Exception as e:
                print(Fore.YELLOW + "\nBody:\n[" + Fore.RED + "Error" + Style.RESET_ALL + Fore.YELLOW + "]: " + Style.RESET_ALL + "{}".format(e) + "\n")
    
    
    elif port['status'] == 'open - no response':
        print(Fore.BLUE + BLOCK + ' ' + str(port['port']) + ' ' + BLOCK)
        print("\n[+] Port " + str(port['port']) + " seems to be open,\nsocket was established but did not receive any data within the allowed response timeout or the socket was closed by the remote machine.")
        print("[i] Error: {}".format(port['error'] + Style.RESET_ALL if 'error' in port else 'Unknown' + Style.RESET_ALL))        
                
    else:
        print(Fore.RED + BLOCK + ' ' + str(port['port']) + ' ' + BLOCK)
        print("\n[-] No services on port " + str(port['port']) + '.')
        print("[i] Error: {}".format(port['error'] + Style.RESET_ALL if 'error' in port else 'Unknown' + Style.RESET_ALL))
        