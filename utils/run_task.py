import subprocess, sys, time, os
from tqdm import tqdm
from datetime import datetime
from . import string_format as sf

PROCS = {}

# Problem: subprocess.Popen causes interference with input() doesn't show user text (stdout, stderr, stdin problem)
# Solution: start_new_session=True
# TODO: Find better way to manage this without using start_new_session
# Tried using Asyncio but had the same problem


def runBackground(command, savePath):
    if savePath is not None:
        os.makedirs(savePath, exist_ok=True)
        file_path = f"{savePath}{command[0]}_{datetime.now()}"
    else:
        os.makedirs("/tmp/netspion/processes/", exist_ok=True)
        file_path = f"/tmp/netspion/processes/{command[0]}_{datetime.now()}"
    f_out = open(f"{file_path}.out", "w")
    f_err = open(f"{file_path}.err", "w")
    p = subprocess.Popen(
        command,
        stdout=f_out,
        stderr=f_err,
        stdin=subprocess.PIPE,
        text=True,
        start_new_session=True,
    )
    PROCS[p.pid] = {
        "id": p.pid,
        "command": p.args,
        "proc": p,
        "out": f_out,
        "err": f_err,
    }

    print(f"PID: {p.pid} || Command: {' '.join(command)} || {sf.info('STARTED')}")


def showRunningProcs():
    for pid, info in PROCS.items():
        proc = info["proc"]
        status = sf.success("RUNNING") if proc.poll() is None else sf.fail("FINISHED")
        print(
            f"PID: {info['id']} || Command: {' '.join(info['command'])} || Status: {status}"
        )
        if status == "FINISHED":
            info["out"].close()
            info["err"].close()


def showProcessData(id):
    proc_info = PROCS.get(id)
    if not proc_info:
        print(sf.fail(f"Process with PID: {id} not found."))
        return

    proc = proc_info["proc"]
    out_file = proc_info["out"]
    err_file = proc_info["err"]
    if (proc.poll()) == None:
        while True:
            try:
                out_file.flush()
                with open((out_file).name, "r") as f:
                    x = f.read()
                time.sleep(1)
            except KeyboardInterrupt:
                break
    else:
        try:
            out_file.close()
            err_file.close()
        finally:
            f = open((out_file).name, "r")
            print(f.read())
            f.close()


def endProcess(id):
    PROCS.get(id)["proc"].terminate()


# Receive an plain string for subprocess
def progress(command):
    print("\n")
    return_code = 0
    with tqdm(unit="B", unit_scale=True, miniters=1) as progress:
        p = subprocess.Popen(
            [command],
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            text=True,
        )

        i = 1
        for line in p.stdout:
            progress.update()
            sys.stdout.flush()

        p.stdout.close()
        return_code = p.wait()

    return return_code


# Receive an array of parameters for subprocess
def newTerminal(command):
    print("\n")
    bash_exec = ""
    for c in command:
        bash_exec += " " + c
    command = [
        "qterminal",
        "-e",
        "bash",
        "-c",
        f"{bash_exec.strip()};read -rsp $'\nPress any key to exit...\n' -n 1 key",
    ]
    subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


# Receive an plain string for subprocess
def normalShell(command):
    print("\n")

    p = subprocess.run(
        [command],
        shell=True,
    )

    return p


# Receive an array of parameters for subprocess
def normalCapture(command):
    print("\n")
    p = subprocess.run(
        command,
        capture_output=True,
        text=True,
    )

    return p


# Receive an array of parameters for subprocess
def normal(command):
    print("\n")
    p = subprocess.run(
        command,
    )

    return p
