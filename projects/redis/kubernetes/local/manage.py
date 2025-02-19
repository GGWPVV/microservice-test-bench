import subprocess
import sys
import argparse

REDIS_MANIFEST_FILE = "main.yaml"

def run_command(command):
    try:
        subprocess.check_call(command, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"\033[91mCommand failed: {command}\nError: {e}\033[0m")
        # sys.exit(1)

def kubectl_operation(operation, filename):
    command = f"kubectl {operation} -f {filename}"
    run_command(command)

def apply_command(args):
    print(f"Applying with arguments: {args}")
    kubectl_operation("apply", REDIS_MANIFEST_FILE)


def delete_command(args):
    print(f"Deleting with arguments: {args}")
    kubectl_operation("delete", REDIS_MANIFEST_FILE)


def main():
    parser = argparse.ArgumentParser(description="Tool with apply and delete commands for Redis.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Apply command
    apply_parser = subparsers.add_parser("apply", help="Apply a configuration")
    apply_parser.set_defaults(func=apply_command)

    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a configuration")
    delete_parser.set_defaults(func=delete_command)

    args = parser.parse_args()

    if args.command:
        args.func(args)  # Call the appropriate function
    else:
        parser.print_help()


if __name__ == "__main__":
    main()