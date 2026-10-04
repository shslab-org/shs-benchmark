#!/usr/bin/env python3
"""Double-fork daemonizer (same survival mechanism as SHS-Code --detach).

Usage: daemonize.py <logfile> <command...>
Forks twice, setsid, redirects stdio to logfile, then execs command.
Parent returns immediately; the daemon survives the launching shell.
"""
import os, sys

def daemonize(exec_path, args, logfile):
    pid = os.fork()
    if pid == 0:
        os.setsid()
        pid2 = os.fork()
        if pid2 == 0:
            fd = os.open(logfile, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
            os.dup2(fd, 1); os.dup2(fd, 2)
            devnull = os.open(os.devnull, os.O_RDONLY)
            os.dup2(devnull, 0)
            os.execv(exec_path, args)
        else:
            os._exit(0)
    else:
        os.waitpid(pid, 0)

if __name__ == "__main__":
    logfile = sys.argv[1]
    cmd = sys.argv[2:]
    daemonize(cmd[0], cmd, logfile)
    print(f"daemonized: {' '.join(cmd)} -> {logfile}")
