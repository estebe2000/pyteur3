// Script de test pour la fenêtre de visualisation de document
console.log("Script de test pour la fenêtre de visualisation de document chargé");

// Fonction pour tester si la fenêtre de visualisation de document fonctionne correctement
function testDocumentViewer() {
    console.log("Test de la fenêtre de visualisation de document");
    
    // Vérifier si la fonction openDocumentViewer existe
    if (typeof openDocumentViewer === 'function') {
        console.log("La fonction openDocumentViewer existe");
        
        // Appeler la fonction openDocumentViewer avec des paramètres de test
        try {
            console.log("Appel de openDocumentViewer");
            openDocumentViewer('/view_document/1', 'Document de test');
            console.log("Fonction openDocumentViewer appelée avec succès");
        } catch (error) {
            console.error("Erreur lors de l'appel de openDocumentViewer:", error);
        }
    } else {
        console.error("La fonction openDocumentViewer n'existe pas");
    }
}

// Fonction pour tester si la fenêtre documentViewer-window existe
function testDocumentViewerWindow() {
    console.log("Test de la fenêtre documentViewer-window");
    
    // Vérifier si la fenêtre existe
    const win = document.getElementById('documentViewer-window');
    console.log("Fenêtre documentViewer-window:", win);
    
    if (!win) {
        console.error("La fenêtre documentViewer-window n'existe pas!");
        
        // Lister toutes les fenêtres disponibles
        console.log("Fenêtres disponibles:");
        document.querySelectorAll('.window').forEach(win => {
            console.log("- ID:", win.id);
        });
        
        return false;
    }
    
    return true;
}

// Fonction pour tester si les éléments de la fenêtre existent
function testDocumentViewerElements() {
    console.log("Test des éléments de la fenêtre documentViewer-window");
    
    const elements = [
        'documentViewerTitle',
        'documentViewerFrame',
        'documentDownloadBtn',
        'documentFullscreenBtn'
    ];
    
    let allExist = true;
    
    elements.forEach(id => {
        const element = document.getElementById(id);
        console.log(`Élément ${id}:`, element);
        
        if (!element) {
            console.error(`L'élément ${id} n'existe pas!`);
            allExist = false;
        }
    });
    
    return allExist;
}

// Fonction pour tester si la fonction openWindow existe
function testOpenWindow() {
    console.log("Test de la fonction openWindow");
    
    // Vérifier si la fonction openWindow existe
    if (typeof openWindow === 'function') {
        console.log("La fonction openWindow existe");
        
        // Appeler la fonction openWindow avec des paramètres de test
        try {
            console.log("Appel de openWindow('documentViewer')");
            openWindow('documentViewer');
            console.log("Fonction openWindow appelée avec succès");
        } catch (error) {
            console.error("Erreur lors de l'appel de openWindow:", error);
        }
    } else {
        console.error("La fonction openWindow n'existe pas");
    }
}

// Fonction pour tester si la fonction postMessage fonctionne correctement
function testPostMessage() {
    console.log("Test de la fonction postMessage");
    
    // Envoyer un message à la fenêtre courante
    try {
        console.log("Envoi d'un message via postMessage");
        window.postMessage({
            type: 'openDocument',
            documentUrl: '/view_document/1',
            documentTitle: 'Document de test'
        }, '*');
        console.log("Message envoyé via postMessage");
    } catch (error) {
        console.error("Erreur lors de l'envoi du message via postMessage:", error);
    }
}

// Fonction pour tester toutes les fonctionnalités
function testAll() {
    console.log("Test de toutes les fonctionnalités");
    
    // Tester si la fenêtre existe
    if (!testDocumentViewerWindow()) {
        console.error("La fenêtre documentViewer-window n'existe pas, impossible de continuer les tests");
        return;
    }
    
    // Tester si les éléments de la fenêtre existent
    if (!testDocumentViewerElements()) {
        console.error("Certains éléments de la fenêtre n'existent pas, impossible de continuer les tests");
        return;
    }
    
    // Tester si la fonction openWindow existe
    testOpenWindow();
    
    // Tester si la fonction openDocumentViewer existe
    testDocumentViewer();
    
    // Tester si la fonction postMessage fonctionne correctement
    testPostMessage();
}

// Exécuter les tests
console.log("Exécution des tests");
testAll();
