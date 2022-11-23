const child_process = require('child_process');
const core = require('@actions/core');
const github = require('@actions/github');

  // `who-to-greet` input defined in action metadata file
const command= core.getInput('command');
console.log(`Command: ${command}`)


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

cmd("ls", ["$(pwd)"])
cmd("ls", ["."])
cmd("ls", ["dist"])
cmd("find", ["."])