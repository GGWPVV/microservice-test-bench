import os

from managment.tools.core import  create_parser, execute_command, kubectl_operation


REDIS_MANIFEST_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.yaml")

def apply_command(args):
    print(f"Applying with arguments: {args}")
    kubectl_operation("apply", REDIS_MANIFEST_FILE)


def delete_command(args):
    print(f"Deleting with arguments: {args}")
    kubectl_operation("delete", REDIS_MANIFEST_FILE)


def main():
    parser, subparsers = create_parser("Tool with apply and delete commands for Redis.")  # Get both
    subparsers.choices["apply"].set_defaults(func=apply_command)
    subparsers.choices["delete"].set_defaults(func=delete_command)

    args = parser.parse_args()
    execute_command(parser, args)


if __name__ == "__main__":
    main()