# python-webernetes

This is a Python wrapper for the [@ngrok/webernetes](https://www.npmjs.com/package/@ngrok/webernetes) JavaScript API.
It allows you to spin up a browser-friendly Kubernetes cluster simulation directly from Python and interact with its API.

## Requirements

- Python 3.6+
- Node.js & npm installed on your system (the wrapper will automatically use npm to pull `@ngrok/webernetes`).

## Installation

You can install this package locally:
```bash
pip install -e .
```

After installation, you can use the CLI tool to run an example:
```bash
webernetes-python example
```

Or you can use it directly in your python code.

## Usage

Here is a simple example showing how to initialize a cluster, apply some resources, and fetch a response from a pod.

```python
from webernetes_wrapper import Cluster

# Initialize the Cluster
cluster = Cluster()

try:
    print("Initializing the cluster...")
    cluster.init()

    # Apply a pod resource
    pod_definition = {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {
            "name": "hello"
        },
        "spec": {
            "containers": [
                {
                    "name": "hello-container",
                    "image": "examples/hello:1.0"
                }
            ]
        }
    }
    
    print("Applying pod definition...")
    cluster.apply([pod_definition])
    
    # You can also fetch from the cluster if your pod exposes an HTTP server
    # response = cluster.fetch("http://hello/")
    # print(response)

finally:
    print("Closing the cluster...")
    cluster.close()
```

## How It Works

1. **Automatic JS Backend Installation**: Upon initialization, the Python module checks if `@ngrok/webernetes` is installed in `~/.webernetes_python`. If not, it uses `npm install` to pull it from the npm registry.
2. **Node.js Bridge**: The python `Cluster` object spawns a lightweight Node.js child process (`bridge.js`).
3. **JSON RPC**: Commands (like `init()`, `apply()`, `fetch()`, `close()`) are sent as JSON-RPC messages via stdin/stdout to the node process, invoking the real JS API.

This design gives you the simplest way to script `webernetes` without having to know or write JavaScript!
