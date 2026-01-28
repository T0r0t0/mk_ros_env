import subprocess
import sys

class docker_tools:
    def isRunning(name: str) -> bool:
        # Chech if the container exist and already running
        result = subprocess.run(f"docker ps | grep {name}", shell=True, capture_output=True, text=True)
        if result.stdout != "": # If is already running
            return True
        return False

    def exist(name: str) -> bool:
        # Check if it exist
        result = subprocess.run(f"docker ps -a | grep {name}", shell=True, capture_output=True, text=True)
        if result.stdout != "": # Exist so we start it
            return True
        return False
    
    def stop(name: str) -> bool:
        print(f"Stopping docker {name} ... ", end="")
        if executeSubProcess(f"docker stop {name}") == 0:
            print("Done")
            return True
        else:
            print("Failed")
            return False

    def start(name: str) -> bool:
        print(f"Starting docker {name} ... ", end="")
        if executeSubProcess(f"docker start {name}") == 0:
            print("Done")
            return True
        else:
            print("Failed")
            return False

    def rm(name: str) -> bool:
        print(f"removing docker {name} ... ", end="")
        if executeSubProcess(f"docker rm {name}") == 0:
            print("Done")
            return True
        else:
            print("Failed")
            return False

    def rmi(name) -> bool:
        print(f"Removing  image {name} ... ", end="")
        if executeSubProcess(f"docker rmi {name}") == 0:
            print("Done")
            return True
        else:
            print("Failed")
            return False

    def build() -> bool:
        print("Building image ... ", end="")
        process = subprocess.Popen(f"docker compose build",shell=True,stdin=sys.stdin.fileno(), stdout=sys.stdout.fileno(), stderr=sys.stderr.fileno())
        # Wait for the process to complete
        if process.wait() == 0:
            print("Done ")
            return True
        else:
            print("Failed")
            return False

    def attachTerminal(name) -> bool:
        process = subprocess.Popen(f"docker exec -it {name} bash",shell=True,stdin=sys.stdin.fileno(), stdout=sys.stdout.fileno(), stderr=sys.stderr.fileno())
        # Wait for the process to complete
        if process.wait() == 0: return True
        else: return False
    
    
def executeSubProcess(shell: str) -> int:
    result = subprocess.run(shell, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print("\nStandard error:", result.stderr)
        print("return code:", result.returncode)

    return result.returncode