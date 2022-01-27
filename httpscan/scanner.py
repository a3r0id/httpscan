from classes import Ports, Threads, Opts
from tryport import try_port
from printresult import print_result

from threading import Thread
from time import sleep
from json import dumps

def scan():
    
    # Establish candy bucket for threadWorkers
    Ports.establishPool()
    
    if Opts.threads > len(Ports.pooled) / 4: #sanity check
        raise OverflowError(f'[-] Cannot use more than {round(len(Ports.pooled) / 4)} threads (rounded) against your current total of {len(Ports.pooled)} ports. (total ports / 4)')
    
    def thread_worker(thread_id):
        
        try:
            
            while len( Ports.pooled ) > 0:
                
                Threads.lock.acquire()
                try:
                    port = Ports.pooled.pop()
                except: # if we pop from an empty list OR if two threads are trying to pop at the same time (which theoretically should never happen but logically COULD)
                    Threads.lock.release()
                    continue
                
                Threads.lock.release()
                result = try_port(port)
                
                if Opts.all:
                    Ports.results.append(result)
                    if not Opts.json:
                        Threads.lock.acquire()
                        print_result(result)
                        Threads.lock.release()      
                        
                else:
                    if result['status'].startswith('open'):
                        Ports.results.append(result)
                        if not Opts.json:
                            Threads.lock.acquire()
                            print_result(result)
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
                if Opts.json:
                    if Opts.all:
                        print(dumps(Ports.results))  
                    else:
                        open_ports = []
                        for result in Ports.results:
                            if result['status'] == 'open':
                                open_ports.append(result)    
                        print(dumps(open_ports))    
                break
            sleep(0.1)            
        except (KeyboardInterrupt, SystemExit):
            print("\n[-] Exiting...")

