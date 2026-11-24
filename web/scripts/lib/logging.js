const logs_buffer = ["RECLICK v4"];
const logs = document.querySelector("#devlogs");
function log_to_console(x) {
    logs_buffer.push(x);
    if (logs_buffer.length > 40) {
        logs_buffer.splice(0, 1);
    }
    logs.innerText = "";
    draw_bg();
    console.log(x);
}
let concurrent_logdraws = 0;
async function draw_bg() {
    concurrent_logdraws++;
    logs.innerText = "";
    for (let i = 0; i < logs_buffer.length; i++) {
        await sleep(100);
        if (concurrent_logdraws > 1) {
            concurrent_logdraws--;
            return;
        }
        logs.innerText += logs_buffer[i] + "\n";
    }
    concurrent_logdraws--;
}