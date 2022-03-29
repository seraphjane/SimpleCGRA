import os
import sys
import random
import datetime as dt
import subprocess as sp

if __name__ == "__main__": 
    assert len(sys.argv) >= 3

    fileDFG    = sys.argv[1]
    fileCompat = sys.argv[2]
    numThreads = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    if len(sys.argv) < 6: 
        rrgfile = "./arch/ADRES.txt"
        coordfile = "./arch/ADRES_coords.txt"
    else: 
        rrgfile = sys.argv[4]
        coordfile = sys.argv[5]

    processes = []
    pids = []
    times = []
    for idx in range(numThreads):
        processes.append(sp.Popen(["python3", "./test/single.py", fileDFG, fileCompat, rrgfile, coordfile, "False"], stdout=sp.PIPE, stderr=sp.DEVNULL))
        pids.append(processes[idx].pid)
        times.append(dt.datetime.now())
    
    finished = False
    countQuited = 0
    while not finished and countQuited < numThreads: 
        for idx in range(numThreads):
            if not processes[idx].poll() is None: 
                countQuited += 1
                if processes[idx].poll() == 0: 
                    finished = True
                    time = dt.datetime.now() - times[idx]
                    print("Time:", str((time.seconds + time.microseconds / 1000000)), 's')
                    print("STDOUT: ")
                    print(processes[idx].stdout.read())
                    break
    
    for idx in range(numThreads):
        if processes[idx].poll() is None:  
            processes[idx].kill()

    if not finished: 
        print("ALL FAILED")
        exit(1)
    else: 
        exit(0)



