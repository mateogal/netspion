import subprocess
import sys
from tqdm import tqdm
from datetime import datetime
import os
import asyncio
from shlex import quote

PROCS = []


# Array of params
# def runBackground(command, savePath):
#     if savePath is not None:
#         os.makedirs(savePath, exist_ok=True)
#         file_path = f"{savePath}{command[0]}_{datetime.now()}"
#     else:
#         os.makedirs("/tmp/netspion/processes/", exist_ok=True)
#         file_path = f"/tmp/netspion/processes/{command[0]}_{datetime.now()}"
#     f_out = open(f"{file_path}.out", "w")
#     f_err = open(f"{file_path}.err", "w")
#     p = subprocess.Popen(
#         command,
#         stdout=f_out,
#         stderr=f_err,
#         stdin=subprocess.PIPE,
#         text=True,
#     )
#     PROCS.insert(
#         len(PROCS),
#         {"id": len(PROCS), "command": p.args, "proc": p, "out": f_out, "err": f_err},
#     )


async def handle_process(p, file_out, file_err):
    # Esperar a que el proceso termine
    await p.wait()

    # Obtener el returncode
    print(f"El proceso {p.pid} terminó con el código: {p.returncode}")

    # Cerrar los archivos
    file_out.close()
    file_err.close()


async def runBackground(command, savePath):
    os.makedirs("/tmp/netspion/processes/", exist_ok=True)
    file_path = f"/tmp/netspion/processes/{command[0]}_{datetime.now():%Y%m%d_%H%M%S}"
    f_out = open(f"{file_path}.out", "w")
    f_err = open(f"{file_path}.err", "w")

    # Crear el proceso de forma asíncrona
    p = await asyncio.create_subprocess_exec(
        command[0], *command[1].split(), stdout=f_out, stderr=f_err
    )

    # Guardar el proceso en la lista PROCS
    PROCS[p.pid] = {
        "id": p.pid,
        "command": str(command),
        "proc": p,
        "out": f_out,
        "err": f_err,
    }

    # Crear una tarea asíncrona para manejar el proceso y no bloquear runBackground
    asyncio.create_task(handle_process(p, f_out, f_err))


def showRunningProcs():
    for value in PROCS:
        print((value["proc"]).returncode)
        if (value["proc"]).returncode == None:
            print(f"PID: {value['id']} {str(value['command'])} RUNNING")
        else:
            print(f"PID: {value['id']} {str(value['command'])} FINISHED")
            value["out"].close()
            value["err"].close()


def showProcessData(id):
    if (PROCS[id]["proc"]).returncode == None:
        while True:
            try:
                print((PROCS[id]["out"]).read())
            except KeyboardInterrupt:
                break
    else:
        f = open((PROCS[id]["out"]).name, "r")
        print(f.read())
        f.close()


def endProcess(id):
    PROCS[id]["proc"].terminate()


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
