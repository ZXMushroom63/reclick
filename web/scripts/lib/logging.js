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
async function draw_bg() {
    logs.innerText = "";
    for (let i = 0; i < logs_buffer.length; i++) {
        await sleep(100);
        logs.innerText += logs_buffer[i] + "\n";
    }
}