import json, os, sys, time
mode = sys.argv[1]
print(json.dumps({'owned_child_pid': os.getpid(), 'mode': mode}), flush=True)
if mode == 'owned-timeout':
    time.sleep(5)
    raise SystemExit(99)
raise SystemExit(7)
