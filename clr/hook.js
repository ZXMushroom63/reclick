const TARGET_MODULE = "clr.dll";
let hookDeployed = false;

function hook(clrModule) {
    if (hookDeployed) return;
    hookDeployed = true;

    console.log("clr.dll was found");
    const targets = ["StrongNameSignatureVerification", "StrongNameSignatureVerificationEx"];

    targets.forEach(target => {
        const funcPtr = clrModule.getExportByName(target);
        if (funcPtr) {
            Interceptor.attach(funcPtr, {
                onEnter(args) {
                    this.pfWasVerified = args[2];
                },
                onLeave(retval) {
                    console.log(`shimmed verification!!`);
                    retval.replace(ptr(1));

                    if (this.pfWasVerified && !this.pfWasVerified.isNull()) {
                        this.pfWasVerified.writeU8(1);
                    }
                }
            });
            console.log(`bypass is bypassing`);
        }
    });
}

const immediateCheck = Process.findModuleByName(TARGET_MODULE);
if (immediateCheck) {
    hook(immediateCheck);
} else {
    const kernel32 = Process.getModuleByName("kernel32.dll");
    var loadLibraryExW = kernel32.findExportByName("LoadLibraryExW");
    if (loadLibraryExW && !loadLibraryExW.isNull()) {
        Interceptor.attach(loadLibraryExW, {
            onEnter(args) {
                if (!args[0].isNull()) {
                    this.libPath = args[0].readUtf16String();
                }
            },
            onLeave(retval) {
                if (this.libPath) {
                    const lowerPath = this.libPath.toLowerCase();

                    if (lowerPath.indexOf("clr") !== -1) {
                        const loadedMod = Process.findModuleByName(TARGET_MODULE);
                        if (loadedMod) {
                            hook(loadedMod);
                        }
                    }
                }
            }
        });
    } else {
        console.log("[-] Could not find LoadLibraryExW?");
    }
}