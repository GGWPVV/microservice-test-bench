# LDE (Local Development Environment) Configuration

This folder contains the configuration files and scripts necessary for setting up and managing a **Local Development
Environment (LDE)** using **k3d**. Below is an outline of what this folder contains and its purpose.

## Contents

1. **k3d Configuration Files**  
   These files are used to define and manage k3d (Kubernetes in Docker) clusters. You can customize cluster settings
   such as:
    - Number of nodes
    - Ports and networking
    - Volume mounts
    - Cluster names

2. **Scripts**  
   Various scripts to streamline the setup, maintenance, and teardown of the local development environment. These
   scripts aim to automate common tasks, such as:
    - Creating a k3d cluster
    - Applying Kubernetes manifests
    - Managing resources within the cluster
    - Cleaning up the environment when no longer needed

## Prerequisites

To properly use the files and scripts in this folder, ensure the following are installed on your system:

- [k3d](https://k3d.io): A lightweight wrapper to run Kubernetes clusters in Docker.
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/): Command-line tool for interacting with Kubernetes
  clusters.
- [Docker](https://www.docker.com/): Required for running k3d clusters.

## Usage

### Setting Up the Cluster

1. Review the configuration files to ensure they meet your development needs.
2. Run the provided script to create the cluster:
   ```bash
   ./create-cluster.sh
   ```
3. Verify that the cluster is running:
   ```bash
   kubectl get nodes
   ```

### Managing Resources

Use the included Kubernetes manifests and helper scripts to deploy and manage your development environment within the
cluster.

### Tearing Down the Cluster

When you're done with the local development environment, you can clean up resources and remove the k3d cluster:

   ```bash
   ./delete-cluster.sh
   ```

## Notes

- Modify the included configuration files and scripts as required to suit your specific LDE requirements.
- If you encounter any issues, ensure your dependencies are up-to-date and properly configured.

## References

- [k3d Documentation](https://k3d.io)
- [Kubernetes Documentation](https://kubernetes.io/docs/home/)