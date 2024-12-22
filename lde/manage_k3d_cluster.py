import argparse
import os
import sys
import subprocess
import shutil

CONFIG_FILE = "k3d-default.yaml"  # Path to the k3d configuration file


def get_container_engine():
    if shutil.which("docker"):
        return "docker"
    else:
        print("Docker is not installed. Please install Docker to proceed.")
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
    
    # Check if the cluster already exists
    result = subprocess.run("k3d cluster list lde-cluster", shell=True, capture_output=True, text=True)
    if "lde-cluster" in result.stdout:
        print(f"Cluster 'lde-cluster' already exists. Starting the cluster...")
        run_command("k3d cluster start lde-cluster")
    else:
        print(f"Cluster 'lde-cluster' does not exist. Creating and starting the cluster using configuration file '{CONFIG_FILE}'...")
        run_command(f"k3d cluster create --config {CONFIG_FILE}")
    
    # Wait for the cluster to be ready
    print("Waiting for the cluster to be ready...")
    run_command("kubectl wait --for=condition=Ready nodes --all --timeout=300s")

    # Apply the Kubernetes manifests
    print("Applying Kubernetes manifests for MongoDB, Redis, and PostgreSQL...")
    run_command("kubectl apply -f mongo-deployment.yaml")
    run_command("kubectl apply -f redis-deployment.yaml")
    run_command("kubectl apply -f postgres-deployment.yaml")


def stop_cluster():
    print(f"Stopping k3d cluster 'lde-cluster'...")
    run_command(f"k3d cluster stop lde-cluster")  # `lde-cluster` must match the cluster name in the config file


def delete_cluster():
    print(f"Deleting k3d cluster 'lde-cluster'...")
    run_command(f"k3d cluster delete lde-cluster")  # `lde-cluster` must match the cluster name in the config file


def list_clusters():
    container_engine = get_container_engine()
    print(f"Using '{container_engine}' as the container engine.")
    """List all current clusters managed by k3d."""
    print("Listing all current k3d clusters...")
    run_command("k3d cluster list")

def main():
    parser = argparse.ArgumentParser(description="Manage a k3d cluster using a k3d configuration file.")
    parser.add_argument(
        "action",
        choices=["start", "stop", "list", "delete"],
        help="Specify the action to perform: 'start' to create/start the cluster, 'stop' to stop the cluster, 'list' to list clusters, or 'delete' to delete the cluster."
    )
    args = parser.parse_args()

    if args.action == "start":
        start_cluster()
    elif args.action == "stop":
        stop_cluster()
    elif args.action == "list":
        list_clusters()
    elif args.action == "delete":
        delete_cluster()


if __name__ == "__main__":
    main()