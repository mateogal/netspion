import subprocess
import sys
from tqdm import tqdm
from datetime import datetime
import os

PROCS = []


# Array of params
def runBackground(command):
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
    )
    PROCS.insert(
        len(PROCS),
        {"id": len(PROCS), "command": p.args, "proc": p, "out": f_out, "err": f_err},
    )


def showRunningProcs():
    for value in PROCS:
        if (value["proc"]).poll() == None:
            print(f"ID: {value['id']} {str(value['command'])} RUNNING")
        else:
            print(f"ID: {value['id']} {str(value['command'])} FINISHED")
            value["out"].close()
            value["err"].close()


def showProcessData(id):
    if (PROCS[id]["proc"]).poll() == None:
        while True:
            try:
                print((PROCS[id]["proc"]).stdout.readline())
            except KeyboardInterrupt:
                break
    else:
        f = open((PROCS[id]["out"]).name, "r")
        print(f.read())
        f.close()


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
