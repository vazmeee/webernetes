import os
import subprocess
import tempfile
import sys
import json
import threading
import uuid

def ensure_js_package():
    cache_dir = os.path.expanduser("~/.webernetes_python")
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    
    package_json = os.path.join(cache_dir, "package.json")
    if not os.path.exists(package_json):
        with open(package_json, "w") as f:
            json.dump({"name": "webernetes-python-bridge", "version": "1.0.0"}, f)
    
    node_modules = os.path.join(cache_dir, "node_modules", "@ngrok", "webernetes")
    if not os.path.exists(node_modules):
        print("Installing @ngrok/webernetes from npm...")
        # Capture stderr to handle potential installation failures
        result = subprocess.run(
            ["npm", "install", "@ngrok/webernetes", "tsx"], 
            cwd=cache_dir, 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode != 0:
            print(f"Failed to install @ngrok/webernetes: {result.stderr}", file=sys.stderr)
            raise RuntimeError("Failed to install JS dependencies")
        
    bridge_dest = os.path.join(cache_dir, "bridge.js")
    if not os.path.exists(bridge_dest):
        bridge_src = os.path.join(os.path.dirname(__file__), "bridge.js")
        with open(bridge_src, "r") as src, open(bridge_dest, "w") as dst:
            dst.write(src.read())

    return cache_dir

class Bridge:
    _instance = None
    _lock = threading.Lock()
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def __init__(self):
        cache_dir = ensure_js_package()
        bridge_script = os.path.join(cache_dir, "bridge.js")
        env = os.environ.copy()
        
        webernetes_src = os.path.join(cache_dir, "node_modules", "@ngrok", "webernetes", "src", "index.ts")
        env["WEBERNETES_PATH"] = "file://" + webernetes_src
        
        tsx_path = os.path.join(cache_dir, "node_modules", ".bin", "tsx")
        
        self.process = subprocess.Popen(
            [tsx_path, bridge_script],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env
        )
        self.responses = {}
        self.cond = threading.Condition()
        self.reader_thread = threading.Thread(target=self._read_stdout, daemon=True)
        self.reader_thread.start()
        
        self.stderr_thread = threading.Thread(target=self._read_stderr, daemon=True)
        self.stderr_thread.start()

    def _read_stderr(self):
        for line in self.process.stderr:
            # Check for DEBUG environment variable to show stderr
            if os.environ.get("WEBERNETES_DEBUG"):
                print("Node stderr:", line.strip(), file=sys.stderr)

    def _read_stdout(self):
        for line in self.process.stdout:
            try:
                msg = json.loads(line)
                with self.cond:
                    self.responses[msg['id']] = msg
                    self.cond.notify_all()
            except json.JSONDecodeError:
                pass

    def call(self, method, *args):
        msg_id = str(uuid.uuid4())
        msg = json.dumps({"id": msg_id, "method": method, "args": list(args)})
        self.process.stdin.write(msg + "\n")
        self.process.stdin.flush()
        
        with self.cond:
            # Wait for response
            while msg_id not in self.responses:
                self.cond.wait()
            resp = self.responses.pop(msg_id)
            if "error" in resp:
                raise Exception(resp["error"])
            return resp.get("result")

    def close(self):
        self.call("close")
        self.process.stdin.close()
        self.process.wait()

class Cluster:
    def __init__(self):
        self.bridge = Bridge.get_instance()
        self.cluster_id = self.bridge.call("new_cluster")

    def init(self):
        return self.bridge.call("init_cluster", self.cluster_id)

    def apply(self, resources):
        return self.bridge.call("apply_cluster", self.cluster_id, resources)

    def fetch(self, url):
        return self.bridge.call("fetch_cluster", self.cluster_id, url)

    def close(self):
        return self.bridge.call("close_cluster", self.cluster_id)
