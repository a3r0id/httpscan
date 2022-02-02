from requests import get
from classes import Opts, Versioning

# Must be run *AFTER* opts have been set!!!
def check_version():
    
    if Opts.silence_updates:
        return
    
    try:
        version_info = get(Versioning.URL).json()
    except:
        return
    print(version_info)
    if version_info['version_new'] != Versioning.VERSION:    
        print("[+] New version available: " + version_info['version_new'])
        print("[i] Current version: " + Versioning.VERSION)
        print("[i] Update at: " + version_info['update_url'])
        print("[i] Changelog: ")
        [print(">\t" + line) for line in version_info['changelog']]
        
        if version_info['update_required']:
            print("[-] [Update required]. Exiting...")
            exit(1)
        
