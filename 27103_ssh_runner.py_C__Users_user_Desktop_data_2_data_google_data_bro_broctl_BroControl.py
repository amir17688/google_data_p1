import ast
import collections
import json
import subprocess
import select
import time
import os
import base64
import zlib
import logging
from threading import Thread

from BroControl import py3bro
Queue = py3bro.Queue
Empty = py3bro.Empty


def get_muxer(shell):
    # The full path of the Python interpreter.  Configured by CMake.
    pythonpath = "@PYTHON_EXECUTABLE@"

    muxer = r"""
import os,sys,subprocess,signal,select,json
TIMEOUT=120

def w(s):
	sys.stdout.write(repr(s) + "\n")
	sys.stdout.flush()

def exec_cmds(cmds):
	p=[]
	for i,cmd in enumerate(cmds):
		try:
			proc=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE __SHELL__)
			p.append((i,proc))
		except Exception as e:
			w((i,(1,'',str(e))))
	return p

w("ready")
commands=[]
signal.alarm(TIMEOUT)
for line in iter(sys.stdin.readline,"done\n"):
	commands.append(json.loads(line))

procs=exec_cmds(commands)
cmd_map={}
fd_map={}
fds=set()
for i,proc in procs:
	o={"idx":i, "proc":proc, "stdout":[], "stderr":[], "waiting":2}
	fd_map[proc.stdout]=o["stdout"]
	fd_map[proc.stderr]=o["stderr"]
	cmd_map[proc.stdout]=o
	cmd_map[proc.stderr]=o
	fds.update((proc.stdout,proc.stderr))

while fds:
	r,_,_=select.select(fds,[],[])
	for fd in r:
		output=os.read(fd.fileno(),1024)
		if output:
			fd_map[fd].append(output)
			continue

		cmd=cmd_map[fd]
		fds.remove(fd)
		cmd["waiting"]-=1
		if cmd["waiting"]:
			continue

		proc=cmd["proc"]
		status=proc.wait()
		out=b"".join(cmd["stdout"])
		err=b"".join(cmd["stderr"])
		w((cmd["idx"],(status,out,err)))

w("done")
"""

    if shell:
        muxer = muxer.replace("__SHELL__", ",shell=True")
    else:
        muxer = muxer.replace("__SHELL__", "")

    if py3bro.using_py3:
        muxer = muxer.encode()

    muxer = base64.b64encode(zlib.compress(muxer))

    if py3bro.using_py3:
        muxer = muxer.decode()

    # Note: the "b" string prefix here for Py3 is ignored by Py2.6-2.7
    muxer = "%s -c 'import zlib,base64; exec(zlib.decompress(base64.b64decode(b\"%s\")))'\n" % (pythonpath, muxer)

    if py3bro.using_py3:
        muxer = muxer.encode()

    return muxer


CmdResult = collections.namedtuple("CmdResult", "status stdout stderr")

class SSHMaster:
    def __init__(self, host, localaddrs):
        self.host = host
        self.base_cmd = [
            "ssh",
            "-o", "BatchMode=yes", "-o", "LogLevel=error",
            host,
        ]
        self.need_connect = True
        self.master = None
        self.localaddrs = localaddrs
        self.run_mux = get_muxer(False)
        self.run_mux_shell = get_muxer(True)

    def connect(self):
        if self.need_connect:
            if self.host in self.localaddrs:
                cmd = ["sh"]
            else:
                cmd = self.base_cmd + ["sh"]
            self.master = subprocess.Popen(cmd, bufsize=0, stdout=subprocess.PIPE, stdin=subprocess.PIPE, close_fds=True, preexec_fn=os.setsid)
            self.need_connect = False

    def readline_with_timeout(self, timeout):
        readable, _, _ = select.select([self.master.stdout], [], [], timeout)
        if not readable:
            return False
        jtxt = self.master.stdout.readline()
        if py3bro.using_py3:
            jtxt = jtxt.decode()
        return jtxt

    def exec_command(self, cmd, shell=False, timeout=60):
        return self.exec_commands([cmd], shell, timeout)[0]

    def exec_commands(self, cmds, shell=False, timeout=60):
        self.send_commands(cmds, timeout, shell)
        return self.collect_results(timeout)

    def send_commands(self, cmds, timeout, shell=False):
        self.connect()
        if shell:
            self.master.stdin.write(self.run_mux_shell)
        else:
            self.master.stdin.write(self.run_mux)
        self.master.stdin.flush()
        self.readline_with_timeout(timeout)
        for cmd in cmds:
            jcmd = "%s\n" % json.dumps(cmd)
            if py3bro.using_py3:
                jcmd = jcmd.encode()
            self.master.stdin.write(jcmd)
        # Note: the "b" string prefix here for Py3 is ignored by Py2.6-2.7
        self.master.stdin.write(b"done\n")
        self.master.stdin.flush()
        self.sent_commands = len(cmds)

    def collect_results(self, timeout):
        outputs = [Exception("Command timeout")] * self.sent_commands
        while True:
            line = self.readline_with_timeout(timeout)
            if not line:
                logging.debug("Command timeout on host %s", self.host)
                self.close()
                break
            resp = ast.literal_eval(line)
            if resp == "done":
                break
            idx, result = resp
            status, out, err = result

            if py3bro.using_py3:
                out = out.decode(errors="replace")
                err = err.decode(errors="replace")

            outputs[idx] = CmdResult(status, out, err)
        return outputs

    def ping(self, timeout=10):
        output = self.exec_command(["/bin/echo", "ping"], timeout=timeout)
        return output and output.stdout.strip() == "ping"

    def close(self):
        if not self.master:
            return
        self.master.stdin.close()
        try:
            self.master.kill()
        except OSError:
            pass
        self.master.wait()
        self.master = None
        self.need_connect = True
    __del__ = close


STOP_RUNNING = object()

class HostHandler(Thread):
    def __init__(self, host, localaddrs, timeout):
        self.host = host
        self.localaddrs = localaddrs
        self.timeout = timeout
        self.q = Queue()
        self.alive = "Unknown"
        self.master = None
        Thread.__init__(self)

    def shutdown(self):
        self.q.put((STOP_RUNNING, None, None))

    def connect(self):
        if self.master:
            self.master.close()
        self.master = SSHMaster(self.host, self.localaddrs)

    def ping(self):
        try:
            return self.master.ping()
        except Exception as e:
            logging.debug("Host %s is not alive", self.host)
            return False

    def connect_and_ping(self):
        if self.alive != True:
            self.connect()
        self.alive = self.ping()

    def run(self):
        while True:
            if self.iteration():
                return

    def iteration(self):
        try:
            item, shell, rq = self.q.get(timeout=30)
        except Empty:
            self.connect_and_ping()
            return False

        if item is STOP_RUNNING:
            return True

        self.connect_and_ping()
        if not self.alive:
            resp = [Exception("Host %s is not alive" % self.host)] * len(item)
            rq.put(resp)
            return False

        try:
            resp = self.master.exec_commands(item, shell, self.timeout)
        except Exception as e:
            self.alive = False
            msg = "Exception in iteration for %s: %s" % (self.host, e)
            logging.debug(msg)
            resp = [Exception(msg)] * len(item)
            time.sleep(2)
        rq.put(resp)

        return False

    def send_commands(self, commands, shell, rq):
        self.q.put((commands, shell, rq))


class MultiMasterManager:
    def __init__(self, localaddrs=[]):
        self.masters = {}
        self.response_queues = {}
        self.localaddrs = localaddrs

    def setup(self, host, timeout):
        if host not in self.masters:
            self.masters[host] = HostHandler(host, self.localaddrs, timeout)
            self.masters[host].start()

    def send_commands(self, host, commands, timeout, shell=False):
        self.setup(host, timeout)
        rq = Queue()
        self.response_queues[host] = rq
        self.masters[host].send_commands(commands, shell, rq)

    def get_result(self, host, timeout):
        rq = self.response_queues[host]
        try:
            return rq.get(timeout=timeout)
        except Empty:
            logging.debug("Host timeout %s", host)
            self.shutdown(host)
            return [Exception("Host timeout")] #FIXME: needs to be the right length

    def exec_command(self, host, command, timeout=30):
        return self.exec_commands(host, [command], timeout)[0]

    def exec_commands(self, host, commands, timeout=65):
        self.send_commands(host, commands, timeout)
        return self.get_result(host, timeout)

    def exec_multihost_commands(self, cmds, shell=False, timeout=65):
        hosts = collections.defaultdict(list)
        for host, cmd in cmds:
            hosts[host].append(cmd)

        for host, cmds in hosts.items():
            self.send_commands(host, cmds, timeout, shell)

        for host in hosts:
            for res in self.get_result(host, timeout):
                yield host, res

    def host_status(self):
        for h, o in self.masters.items():
            if h not in self.localaddrs:
                yield h, o.alive

    def shutdown(self, host):
        self.masters[host].shutdown()
        del self.masters[host]

    def shutdown_all(self):
        for handler in self.masters.values():
            handler.shutdown()
        self.masters = {}

    __del__ = shutdown_all

