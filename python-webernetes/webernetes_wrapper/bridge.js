import readline from "readline";

const clusters = new Map();
let nextClusterId = 1;

async function main() {
    const webernetesPath = process.env.WEBERNETES_PATH;
    const { Cluster } = await import(webernetesPath);

    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout,
        terminal: false
    });

    rl.on('line', async (line) => {
        if (!line.trim()) return;
        let msg;
        try {
            msg = JSON.parse(line);
        } catch (e) {
            console.error("Failed to parse JSON:", e.message);
            return;
        }
        
        const { id, method, args } = msg;
        try {
            let result;
            if (method === "new_cluster") {
                const cId = String(nextClusterId++);
                clusters.set(cId, new Cluster());
                result = cId;
            } else if (method === "init_cluster") {
                const cluster = clusters.get(args[0]);
                await cluster.init();
                result = "ok";
            } else if (method === "apply_cluster") {
                const cluster = clusters.get(args[0]);
                const res = await cluster.apply(args[1]);
                result = res;
            } else if (method === "fetch_cluster") {
                const cluster = clusters.get(args[0]);
                const resp = await cluster.fetch(args[1]);
                result = { status: resp.status, body: resp.body };
            } else if (method === "close_cluster") {
                const cluster = clusters.get(args[0]);
                if (cluster) {
                    await cluster.close();
                    clusters.delete(args[0]);
                }
                result = "ok";
            } else if (method === "close") {
                result = "ok";
                console.log(JSON.stringify({ id, result }));
                process.exit(0);
            } else {
                throw new Error(`Unknown method ${method}`);
            }
            console.log(JSON.stringify({ id, result }));
        } catch (err) {
            console.log(JSON.stringify({ id, error: err.message || err.toString() }));
        }
    });
}
main().catch(e => {
    console.error(e);
    process.exit(1);
});
