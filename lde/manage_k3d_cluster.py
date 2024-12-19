import argparse
import os
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


def configure_podman_environment():
    """Set environment variables to make k3d work with podman."""
    xdg_runtime_dir = os.getenv("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")
    os.environ["XDG_RUNTIME_DIR"] = xdg_runtime_dir
    os.environ["DOCKER_HOST"] = f"unix://{xdg_runtime_dir}/podman/podman.sock"
    print(f"Configured Podman environment. DOCKER_HOST={os.environ['DOCKER_HOST']}")


def run_command(command):
    try:
        subprocess.check_call(command, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {command}\nError: {e}")
        sys.exit(1)


def start_cluster():
    container_engine = get_container_engine()
    print(f"Using '{container_engine}' as the container engine.")

    # Configure podman-specific environment if podman is detected
    if container_engine == "podman":
        configure_podman_environment()

    print(f"Starting k3d cluster using configuration file '{CONFIG_FILE}'...")
    run_command(f"k3d cluster create --config {CONFIG_FILE}")


def stop_cluster():
    print(f"Stopping and deleting k3d cluster defined in configuration file '{CONFIG_FILE}'...")
    run_command(f"k3d cluster delete lde-cluster")  # `lde-cluster` must match the cluster name in the config file


def list_clusters():
    container_engine = get_container_engine()
    print(f"Using '{container_engine}' as the container engine.")

    # Configure podman-specific environment if podman is detected
    if container_engine == "podman":
        configure_podman_environment()
    """List all current clusters managed by k3d."""
    print("Listing all current k3d clusters...")
    run_command("k3d cluster list")

def main():
    parser = argparse.ArgumentParser(description="Manage a k3d cluster using a k3d configuration file.")
    parser.add_argument(
        "action",
        choices=["start", "stop", "list"],
        help="Specify the action to perform: 'start' to create/start the cluster or 'stop' to stop/delete the cluster."
    )
    args = parser.parse_args()

    if args.action == "start":
        start_cluster()
    elif args.action == "stop":
        stop_cluster()
    elif args.action == "list":
        list_clusters()


if __name__ == "__main__":
    main()