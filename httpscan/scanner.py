from classes import Ports, Threads, Opts
from requestengine import RequestEngine
from printresult import print_result

from threading import Thread
from time import sleep
from json import dumps
from sys import stdout

def scan():
    
    # Establish candy bucket for threadWorkers
    Ports.establishPool()
    
    if Opts.threads > len(Ports.pooled) / 4: #sanity check
        raise IndexError(f'[-] Cannot use more than {round(len(Ports.pooled) / 4)} threads (rounded) against your current total of {len(Ports.pooled)} ports. (total ports / 4)')
    
    def thread_worker(thread_id):
        try:
            while len( Ports.pooled ) > 0:
                
                Threads.lock.acquire()
                try:
                    port = Ports.pooled.pop()
                except:
                    Threads.lock.release()
                    continue
                Threads.lock.release()
                
                engine = RequestEngine(port)
                engine.doRequest()
                
                if not Opts.all and engine.response is None:
                    continue
                
                Ports.results.append({
                    "port": port,
                    "status": 0,
                    "data": engine.json()
                })
                
                if not Opts.json:
                    Threads.lock.acquire()
                    print_result(engine)
                    Threads.lock.release()      
                            
        except (KeyboardInterrupt, SystemExit):
            print(f"\n[-] Thread {thread_id} Exiting...")
                                
    for i in range(Opts.threads):                        
        Threads.pool.append(Thread(target=thread_worker, args=(i,)))
        
    i = 0.1
    for t in Threads.pool:
        t.start()
        sleep(i) #sanity check
        i += 0.3
        
    while True:
        try:
            if Threads.allDead():
                # Print JSON
                if Opts.json:
                    if Opts.all:
                        stdout.write(dumps(Ports.results))  
                    else:
                        open_ports = []
                        for result in Ports.results:
                            if result['status'] != 0 and result['status'] is not None:
                                open_ports.append(result)    
                        stdout.write(dumps(open_ports)) 
                break
            sleep(0.1)            
        except (KeyboardInterrupt, SystemExit):
            print("\n[-] Exiting...")

