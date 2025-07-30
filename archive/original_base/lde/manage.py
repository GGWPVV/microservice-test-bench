import os
import argparse
import shutil
import subprocess
import sys

from managment.tools.core import (
    kubectl_operation,
    run_command,
)


K3D_CONFIG_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "k3d-default.yaml"
) # Path to the k3d configuration file
TRAEFIK_MANIFEST_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "traefik.yaml"
)


def check_kubectl():
    """
    Check if kubectl is installed and available in the system's PATH.
    If not, print an error message with installation instructions.
    """
    try:
        run_command("kubectl version --client")
    except FileNotFoundError:
        print("Error: kubectl command not found.")
        print("Please install kubectl to interact with your Kubernetes cluster.")
        print(
            "Installation instructions can be found here: https://kubernetes.io/docs/tasks/tools/"
        )
        exit(1)  # Exit if kubectl is not available


def check_poetry():
    """
    Check if poetry is installed, has a version greater than 2, and has the Polylith plugin installed.
    If not, print an error message with installation instructions.
    """

    def run_command_with_output(command):
        try:
            run_command("poetry --version")


        except FileNotFoundError:
            print("Error: poetry command not found.")
            print("Please install poetry.")
            print(
                "Installation instructions can be found here: https://python-poetry.org/docs/#installation"
            )
            exit(1)
        try:
            run_command('poetry self show plugins | grep -q "poetry-polylith-plugin"')
        except FileNotFoundError:
            print("Error: poetry-polylith-plugin command not found.")
            exit(1)

def check_docker():
    try:
        run_command("docker --version")
    except FileNotFoundError:
        print("Docker is not installed. Please install Docker to proceed.")
        sys.exit(1)

def start_command(args):
    print(f"Starting with arguments: {args}")
    check_kubectl()
    check_poetry()
    check_docker()
    # Check if the cluster already exists
    result = subprocess.run("k3d cluster list lde-cluster", shell=True, capture_output=True, text=True)
    if "lde-cluster" in result.stdout:
        print(f"Cluster 'lde-cluster' already exists. Starting the cluster...")
        run_command("k3d cluster start lde-cluster")
    else:
        print(f"Cluster 'lde-cluster' does not exist. Creating and starting the cluster using configuration file '{K3D_CONFIG_FILE}'...")
        run_command(f"k3d cluster create --config {K3D_CONFIG_FILE}")
    
    # Wait for the cluster to be ready
    print("Waiting for the cluster to be ready...")
    run_command("kubectl wait --for=condition=Ready nodes --all --timeout=300s")

    kubectl_operation("apply", TRAEFIK_MANIFEST_FILE)


def stop_command(args):
    print(f"Stopping k3d cluster 'lde-cluster'...")
    run_command(f"k3d cluster stop lde-cluster")


def delete_command(args):
    print("Deleting k3d cluster 'lde-cluster'...")
    run_command(f"k3d cluster delete lde-cluster")


def main():
    parser = argparse.ArgumentParser(
        description="Tool with apply and delete commands for Redis."
    )
    subparsers = parser.add_subparsers(
        title="Commands", dest="command", help="Available commands"
    )

    # Start command
    start_parser = subparsers.add_parser("start", help="Start the application")
    start_parser.set_defaults(func=start_command)

    # Stop command
    stop_parser = subparsers.add_parser("stop", help="Stop the application")
    stop_parser.set_defaults(func=stop_command)

    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete resources")
    delete_parser.set_defaults(func=delete_command)

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
