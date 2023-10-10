import subprocess


def main() -> None:
    # list all python processes on windows, and collect pids in list

    # list all python processes on windows sorted by start time

    command = "tasklist | findstr python"
    result = subprocess.run(command, shell=True, capture_output=True)
    lines = result.stdout.decode("utf-8").split("\r\n")
    pids = []
    for line in lines:
        # replace multiple spaces with single space
        line = " ".join(line.split())
        if "python" in line:
            pid = line.split(" ")[1]
            pids.append(int(pid))

    # pids = sorted(pids)
    print(pids)
    for pid in pids:
        command = f"taskkill /F /PID {pid}"
        print(command)
        subprocess.run(command, shell=True)


if __name__ == "__main__":
    main()
