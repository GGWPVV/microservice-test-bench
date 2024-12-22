# LDE (Local Development Environment) Configuration

This folder contains the configuration files and scripts necessary for setting up and managing a **Local Development Environment (LDE)** using **k3d**. Below is an outline of what this folder contains.

## Contents

1. **k3d Configuration File**
   - `k3d_cluster_config.yml`: Defines and manages the k3d cluster. Customize cluster settings such as:
      - Number of nodes (servers and agents)
      - Ports mapping for host and cluster
      - Volume mounts
      - Cluster name and runtime options

2. **Python Management Script**
   - `manage_k3d_cluster.py`: A Python-based script to streamline the setup, maintenance, and teardown of the cluster.  
     Features:
      - **Start the cluster**: Create and launch the k3d cluster using the `k3d_cluster_config.yml` file.
      - **Stop the cluster**: Stop the running k3d cluster.
      - **Delete the cluster**: Delete the k3d cluster.
      - **List clusters**: List all existing k3d clusters.

## Prerequisites

To use the files and script in this folder, ensure that the following tools are installed on your system:

- [k3d](https://k3d.io): A lightweight wrapper to run Kubernetes clusters in Docker.
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/): Command-line tool for interacting with Kubernetes clusters.
- [Docker](https://www.docker.com/): Required for running k3d clusters.
- [Python 3.6+](https://www.python.org/): Required to execute the management script.

## Usage

### Listing Clusters

To list all existing clusters:
```bash
python manage_k3d_cluster.py list
```
This command will display the names and details of all k3d clusters currently available on the system.


### Setting Up the Cluster

1. Review and, if necessary, modify the cluster configuration in `k3d_cluster_config.yml`:
   - Adjust the number of server or agent nodes.
   - Customize node ports and volume definitions.
   - Extend runtime options as required.

2. Use the Python script to create or manage the cluster:

   Run the following command to **start** the cluster.
   ```bash
   python manage_k3d_cluster.py start
   ```

3. Verify that the cluster is running:
   ```bash
   kubectl get nodes
   ```

### Stopping the Cluster

To stop the cluster:
```bash
python manage_k3d_cluster.py stop
```

### Deleting the Cluster

To delete the cluster:
```bash
python manage_k3d_cluster.py delete
```

### Configuration Details

The cluster is started based on the content of the `k3d_cluster_config.yml` file. This includes:
- Cluster Name: `lde-cluster`
- Server and Agent Nodes:
   - 1 server node
   - 2 agent nodes
- Port Mappings:
   - **8080 on host → 80 in cluster**
   - **8443 on host → 443 in cluster**
- Volume Mounts:
   - Mounts a Docker volume `my-local-volume` to `/data` within the cluster.
- Disabled Components:
   - **Service Load Balancer** (`--disable=servicelb` for server nodes).

### Notes

- The Python script automatically uses the `k3d_cluster_config.yml` configuration file. Ensure it is in the same directory as the script.
- Modify `k3d_cluster_config.yml` as needed to fit your local development setup requirements.
- Use `kubectl` to manage resources within the cluster once it’s running.

## References

- [k3d Documentation](https://k3d.io)
- [Kubernetes Documentation](https://kubernetes.io/docs/home/)