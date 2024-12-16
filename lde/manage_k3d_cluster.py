import argparse
import sys
import subprocess
import shutil

CONFIG_FILE = "k3d-default.yaml"  # Path to the k3d configuration file


def get_container_engine():
    if shutil.which("docker"):
        return "docker"
    elif shutil.which("podman"):
        return "podman"
    else:
        print("Neither Docker nor Podman is installed. Please install one of them to proceed.")
        sys.exit(1)


def run_command(command):
    try:
        subprocess.check_call(command, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {command}\nError: {e}")
        sys.exit(1)


def start_cluster():
    container_engine = get_container_engine()
    print(f"Using '{container_engine}' as the container engine.")
    print(f"Starting k3d cluster using configuration file '{CONFIG_FILE}'...")
    run_command(f"k3d cluster create --config {CONFIG_FILE}")


def stop_cluster():
    print(f"Stopping and deleting k3d cluster defined in configuration file '{CONFIG_FILE}'...")
    run_command(f"k3d cluster delete lde-cluster")  # `lde-cluster` must match the cluster name in the config file


def main():
    parser = argparse.ArgumentParser(description="Manage a k3d cluster using a k3d configuration file.")
    parser.add_argument(
        "action",
        choices=["start", "stop"],
        help="Specify the action to perform: 'start' to create/start the cluster or 'stop' to stop/delete the cluster."
    )
    args = parser.parse_args()

    if args.action == "start":
        start_cluster()
    elif args.action == "stop":
        stop_cluster()


if __name__ == "__main__":
    main()