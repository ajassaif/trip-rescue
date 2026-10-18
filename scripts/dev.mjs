import { spawn } from "node:child_process";
import { existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const root = dirname(dirname(fileURLToPath(import.meta.url)));
if (existsSync(join(root,".env"))) process.loadEnvFile(join(root,".env"));
const python = process.env.PYTHON_EXECUTABLE || join(root,".venv",process.platform === "win32" ? "Scripts/python.exe" : "bin/python");
if (!existsSync(python)) {
  console.error("Create the Python environment first: python -m venv .venv, then install backend/requirements.lock. See README.md.");
  process.exit(1);
}
const children = [];
let stopping = false;
function stop(code = 0) {
  if (stopping) return;
  stopping = true;
  for (const child of children) child.kill();
  process.exitCode = code;
}
function start(command,args) {
  const child = spawn(command,args,{cwd:root,stdio:"inherit",env:process.env,windowsHide:true});
  children.push(child);
  child.on("error",error=>{console.error(error.message);stop(1);});
  child.on("exit",code=>{if (!stopping) stop(code || 0);});
}
start(python,["-m","uvicorn","backend.app:app","--host","127.0.0.1","--port","8100"]);
start(process.execPath,[join(root,"node_modules/next/dist/bin/next"),"dev","--hostname","127.0.0.1","--port","3100"]);
process.on("SIGINT",()=>stop());
process.on("SIGTERM",()=>stop());
