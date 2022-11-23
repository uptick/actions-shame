const child_process = require('child_process');
const { exit } = require('process');

function cmd(program, args) {
    var child = child_process.spawnSync(program, args, { encoding : 'utf8' });
    console.log(`Process ${program} finished.`);
    if(child.error) {
        console.log("ERROR: ",child.error);
        exit(1)
    }
    console.log("stdout: ",child.stdout);
    console.log("stderr: ",child.stderr);
    console.log("exist code: ",child.status);
}

cmd("bash", ["-c", `cd /home/runner/work/_actions/uptick/actions-shame/; cd *; python dist/src/main.py ${command}`])
