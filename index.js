var child_process = require('child_process');
const cmd = "shame"

var child = child_process.spawnSync("python3", ["src/main.py", cmd], { encoding : 'utf8' });
console.log("Process finished.");
if(child.error) {
    console.log("ERROR: ",child.error);
}
console.log("stdout: ",child.stdout);
console.log("stderr: ",child.stderr);
console.log("exist code: ",child.status);