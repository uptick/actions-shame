const child_process = require('child_process');

function cmd(program, args) {
    var child = child_process.spawnSync(program, args, { encoding : 'utf8' });
    console.log(`Process ${program} finished.`);
    if(child.error) {
        console.log("ERROR: ",child.error);
    }
    console.log("stdout: ",child.stdout);
    console.log("stderr: ",child.stderr);
    console.log("exist code: ",child.status);
}

cmd("bash", ["-c", "env"])
cmd("bash", ["-c", "find ."])
