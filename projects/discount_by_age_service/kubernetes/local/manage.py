import os
import argparse
import subprocess

MANIFEST_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.yaml")

def kubectl_operation(action, manifest_file):
    cmd = ["kubectl", action, "-f", manifest_file]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"Success: {result.stdout}")
    else:
        print(f"Error: {result.stderr}")

def apply_command(args):
    print(f"Applying manifest {MANIFEST_FILE} ...")
    kubectl_operation("apply", MANIFEST_FILE)

def delete_command(args):
    print(f"Deleting manifest {MANIFEST_FILE} ...")
    kubectl_operation("delete", MANIFEST_FILE)

def main():
    parser = argparse.ArgumentParser(description="Manage discount_by_age Kubernetes manifests")
    subparsers = parser.add_subparsers(title="commands", dest="command")

    apply_parser = subparsers.add_parser("apply", help="Apply the Kubernetes manifest")
    apply_parser.set_defaults(func=apply_command)

    delete_parser = subparsers.add_parser("delete", help="Delete the Kubernetes resources")
    delete_parser.set_defaults(func=delete_command)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
