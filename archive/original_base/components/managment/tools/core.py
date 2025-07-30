import subprocess
import argparse


def run_command(command):
    """
    Runs a shell command and prints any errors to stderr.
    """
    try:
        subprocess.check_call(command, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"\033[91mCommand failed: {command}\nError: {e}\033[0m")


def kubectl_operation(operation, filename):
    """
    Runs a kubectl operation (apply, delete, etc.) on a given file.
    """
    command = f"kubectl {operation} -f {filename}"
    run_command(command)


def kubectl_apply_manifest(manifest):
    """
    Applies a Kubernetes manifest from str using kubectl.
    """
    command = f"cat <<EOF | kubectl apply -f -\n{manifest}\nEOF"
    run_command(command)


def kubectl_delete_manifest(manifest):
    """
    Deletes a Kubernetes manifest from str using kubectl.
    """
    command = f"cat <<EOF | kubectl delete -f -\n{manifest}\nEOF"
    run_command(command)


def create_parser(description):
    """
    Creates an argument parser with apply and delete subcommands.
    Returns the parser and the subparsers object.
    """
    parser = argparse.ArgumentParser(description=description)
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Apply command
    apply_parser = subparsers.add_parser("apply", help="Apply a configuration")
    apply_parser.set_defaults(func=None)  # Placeholder, to be set by the caller

    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a configuration")
    delete_parser.set_defaults(func=None)  # Placeholder, to be set by the caller
    return parser, subparsers  # Return both parser and subparsers


def execute_command(parser, args):
    """
    Executes the command based on the parsed arguments.
    """
    if args.command:
        if args.func:
            args.func(args)  # Call the appropriate function
        else:
            print("No function associated with this command.")
            parser.print_help()
    else:
        parser.print_help()