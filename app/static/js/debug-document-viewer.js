// Script de débogage pour la fenêtre de visualisation de document
console.log("Script de débogage pour la fenêtre de visualisation de document chargé");

// Fonction pour vérifier si la fenêtre existe
function checkDocumentViewerWindow() {
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

// Fonction pour vérifier si les éléments de la fenêtre existent
function checkDocumentViewerElements() {
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

// Fonction pour ouvrir directement la fenêtre de visualisation de document
function debugOpenDocumentViewer() {
    console.log("Tentative d'ouverture de la fenêtre de visualisation de document");
    
    // Vérifier si la fenêtre existe
    if (!checkDocumentViewerWindow()) {
        return;
    }
    
    // Vérifier si les éléments de la fenêtre existent
    if (!checkDocumentViewerElements()) {
        return;
    }
    
    // Mettre à jour le titre
    document.getElementById('documentViewerTitle').textContent = 'Document de test';
    
    // Mettre à jour l'iframe avec l'URL du document
    document.getElementById('documentViewerFrame').src = '/view_document/1';
    
    // Mettre à jour le bouton de téléchargement
    document.getElementById('documentDownloadBtn').onclick = function() {
        window.open('/view_document/1', '_blank');
    };
    
    // Configurer le bouton plein écran
    document.getElementById('documentFullscreenBtn').onclick = function() {
        const iframe = document.getElementById('documentViewerFrame');
        if (iframe) {
            if (iframe.requestFullscreen) {
                iframe.requestFullscreen();
            } else if (iframe.webkitRequestFullscreen) { /* Safari */
                iframe.webkitRequestFullscreen();
            } else if (iframe.msRequestFullscreen) { /* IE11 */
                iframe.msRequestFullscreen();
            }
        }
    };
    
    // Ouvrir la fenêtre
    console.log("Appel de openWindow('documentViewer')");
    
    // Vérifier si la fonction openWindow existe
    if (typeof openWindow !== 'function') {
        console.error("La fonction openWindow n'existe pas!");
        return;
    }
    
    // Ouvrir la fenêtre
    openWindow('documentViewer');
}

// Exécuter la fonction de débogage
debugOpenDocumentViewer();
