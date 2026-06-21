import sys
import json
from webernetes_wrapper import Cluster

def main():
    if len(sys.argv) < 2:
        print("Usage: python -m webernetes_wrapper <command> [args...]")
        print("Commands:")
        print("  example    Run a simple pod example")
        sys.exit(1)

    command = sys.argv[1]

    if command == "example":
        cluster = Cluster()
        try:
            print("Initializing the cluster...")
            cluster.init()

            pod_definition = {
                "apiVersion": "v1",
                "kind": "Pod",
                "metadata": {"name": "hello"},
                "spec": {
                    "containers": [{"name": "hello", "image": "examples/hello:1.0"}]
                }
            }
            print("Applying pod definition...")
            res = cluster.apply([pod_definition])
            print("Apply Result:", json.dumps(res, indent=2))
        finally:
            print("Closing the cluster...")
            cluster.close()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
