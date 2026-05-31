Java.perform(function () {

    function callPassword() {
        console.log("[*] Recherche d'une instance active de MainActivity...");

        Java.choose("com.pwnsec.firestorm.MainActivity", {

            onMatch: function (instance) {
                console.log("[+] Instance MainActivity trouvée : " + instance);

                try {
                    var password = instance.Password();
                    console.log("[+] Firebase Password : " + password);
                } catch (e) {
                    console.log("[-] Erreur lors de l'appel de Password() : " + e);
                }
            },

            onComplete: function () {
                console.log("[*] Recherche terminée.");
            }
        });
    }

    console.log("[*] Script Frida chargé.");
    console.log("[*] Attente de 3 secondes avant l'appel de Password()...");

    setTimeout(callPassword, 3000);
});