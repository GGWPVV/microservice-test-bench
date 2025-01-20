import argparse
import subprocess
import sys


def run_command(command):
    try:
        subprocess.check_call(command, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {command}\nError: {e}")
        sys.exit(1)

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest="command")
subparsers.required = True

def start_func(args):
    run_command("echo Starting service...")
    run_command("kubectl apply -f nvidia-device-plugin.yaml")

def stop_func(args):
    run_command("echo Stopping service...")
    run_command("kubectl delete -f nvidia-device-plugin.yaml")

def build_func(args):
    run_command("echo Building project...")
    run_command("docker build -t registry.localhost:5001/ollama:local projects/ollama")
    run_command("docker push registry.localhost:5001/ollama:local")

def default_func(args):
    print("No command provided. Use --help to see available commands.")

parser.set_defaults(func=default_func)

start_parser = subparsers.add_parser("start", help="Start the service")
start_parser.set_defaults(func=start_func)
stop_parser = subparsers.add_parser("stop", help="Stop the service")
stop_parser.set_defaults(func=stop_func)
build_parser = subparsers.add_parser("build", help="Build the project")
build_parser.set_defaults(func=build_func)

if __name__ == "__main__":
    args = parser.parse_args()
    args.func(args)