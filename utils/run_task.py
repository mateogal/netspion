import subprocess
import sys
from tqdm import tqdm


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
