/*
dns lookup patcher
- ns.photonengine.io
- ns.photonengine.cn
*/
const overrideIP = new Uint8Array(4);
overrideIP[0] = 127;
overrideIP[1] = 0;
overrideIP[2] = 0;
overrideIP[3] = 1;

const pth = "needs_photoncpp_address.txt";
let outIP = null;

try {
    outIP = File.readAllText(pth);
} catch (error) {
    outIP = "127.0.0.1";
    File.writeAllText(pth, outIP);
}
console.log("Parsing Nameserver IP: " + outIP);

outIP.trim().split(".").forEach((x, i) => {
    overrideIP[i] = parseInt(x);
});

const domains = [ "ns.photonengine.io", "ns.photonengine.cn" ];

(function () {
    const hookedModules = new Set();
    const hookedMethods = new Set();
    function logMapping(domain, ip, apiName) {
        if (!domain) domain = "UNKNOWN";
        if (!ip) ip = "UNKNOWN";

        console.log(`[${Date.now()}] [${apiName}] ${domain} <--> ${ip}`);
    }

    function parseAddrInfo(addrinfoPtr, domain, apiName) {
        let current = addrinfoPtr;
        while (!current.isNull()) {
            // Offset 4: ai_family (int)
            const ai_family = current.add(4).readInt();
            
            // x64: ai_addr is at offset 32, ai_next is at offset 40
            // x86: ai_addr is at offset 24, ai_next is at offset 28
            const ai_addr = current.add(Process.pointerSize === 8 ? 32 : 24).readPointer();

            if (!ai_addr.isNull()) {
                if (ai_family === 2) { // AF_INET (IPv4)
                    // In sockaddr_in, sin_addr starts exactly at offset 4 (4 bytes long)
                    const ipPtr = ai_addr.add(4);
                    const ipv4 = [
                        ipPtr.readU8(),
                        ipPtr.add(1).readU8(),
                        ipPtr.add(2).readU8(),
                        ipPtr.add(3).readU8()
                    ].join('.');

                    logMapping(domain, ipv4, apiName);
                    
                    console.log(`overriding with custom ip: ${[...overrideIP].map(x => x.toString(10)).join(".")}`);
                    if (domains.includes(domain.toLowerCase())) {
                        ipPtr.writeU8(overrideIP[0]);
                        ipPtr.add(1).writeU8(overrideIP[1]);
                        ipPtr.add(2).writeU8(overrideIP[2]);
                        ipPtr.add(3).writeU8(overrideIP[3]);
                    }
                } else if (ai_family === 23) { // AF_INET6 (IPv6)
                    // In sockaddr_in6, sin6_addr starts exactly at offset 8 (16 bytes long)
                    const ipPtr = ai_addr.add(8);
                    let blocks = [];
                    for (let i = 0; i < 8; i++) {
                        const highByte = ipPtr.add(i * 2).readU8();
                        const lowByte = ipPtr.add(i * 2 + 1).readU8();
                        const word = (highByte << 8) | lowByte;
                        blocks.push(word.toString(16));
                    }
                    const ipv6 = blocks.join(':').replace(/(^|:)0(:0)+(:|$)/, '::');
                    
                    logMapping(domain, ipv6, apiName);
                }
            }
            
            current = current.add(Process.pointerSize === 8 ? 40 : 28).readPointer();
        }
    }


    function hookDNSApis(moduleName) {
        if (hookedModules.has(moduleName.toLowerCase())) return;
        
        const targetModule = Process.findModuleByName(moduleName);
        if (!targetModule) return;

        hookedModules.add(moduleName.toLowerCase());
        console.log(`FridaRuntimePatcher: DNS hooking ${moduleName}...`);

        let getAddrInfoWPtr = null;
        try { getAddrInfoWPtr = targetModule.getExportByName('GetAddrInfoW'); } catch(e){}
        
        if (getAddrInfoWPtr) {
            Interceptor.attach(getAddrInfoWPtr, {
                onEnter: function (args) {
                    this.nodename = args[0].isNull() ? "NULL" : args[0].readUtf16String();
                    this.ppResult = args[3];
                },
                onLeave: function (retval) {
                    if (retval.toInt32() === 0 && this.ppResult && !this.ppResult.isNull()) {
                        parseAddrInfo(this.ppResult.readPointer(), this.nodename, 'GetAddrInfoW');
                    }
                }
            });
        }

        let getaddrinfoPtr = null;
        try { getaddrinfoPtr = targetModule.getExportByName('getaddrinfo'); } catch(e){}
        
        if (getaddrinfoPtr) {
            Interceptor.attach(getaddrinfoPtr, {
                onEnter: function (args) {
                    this.nodename = args[0].isNull() ? "NULL" : args[0].readAnsiString();
                    this.ppResult = args[3];
                },
                onLeave: function (retval) {
                    if (retval.toInt32() === 0 && this.ppResult && !this.ppResult.isNull()) {
                        parseAddrInfo(this.ppResult.readPointer(), this.nodename, 'getaddrinfo');
                    }
                }
            });
        }
    }

    hookDNSApis('ws2_32.dll');
    hookDNSApis('wsock32.dll');

    function hookLoadLibrary(apiName) {
        const kernel32 = Process.findModuleByName('kernel32.dll');
        if (!kernel32) return;

        let ptr = null;
        try { ptr = kernel32.getExportByName(apiName); } catch(e){}
        if (!ptr) return;

        Interceptor.attach(ptr, {
            onEnter: function (args) {
                if (!args[0].isNull()) {
                    this.libName = apiName.endsWith('W') ? args[0].readUtf16String() : args[0].readAnsiString();
                }
            },
            onLeave: function (retval) {
                if (!retval.isNull() && this.libName) {
                    const lowerName = this.libName.toLowerCase();
                    if (lowerName.includes('ws2_32') || lowerName.includes('wsock32')) {
                        Script.nextTick(() => hookDNSApis('ws2_32.dll'));
                    }
                    if (lowerName.includes('gameassembly')) {
                        Script.nextTick(() => hookUnityIL2CPPDNS());
                    }
                }
            }
        });
    }

    hookLoadLibrary('LoadLibraryA');
    hookLoadLibrary('LoadLibraryW');
    hookLoadLibrary('LoadLibraryExA');
    hookLoadLibrary('LoadLibraryExW');
})();
