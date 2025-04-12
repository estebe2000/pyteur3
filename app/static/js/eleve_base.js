// Fonctions de gestion des fenêtres
let zIndexCounter = 1001;
let externalWindows = {}; // Pour stocker les références aux fenêtres externes

function toggleStartMenu() {
    const menu = document.getElementById('startMenu');
    menu.style.display = (menu.style.display === 'block') ? 'none' : 'block';
}

function bringToFront(win) {
    zIndexCounter++;
    if (zIndexCounter >= 9999) zIndexCounter = 1001;
    win.style.zIndex = zIndexCounter;
}

function openWindow(id) {
    console.log("openWindow appelé pour:", id);
    let winId = id + '-window';
    console.log("Recherche de la fenêtre avec ID:", winId);
    const win = document.getElementById(winId);
    
    if(win) {
        console.log("Fenêtre trouvée:", win);
        // Fermer les fenêtres incompatibles si nécessaire
        if (id === 'exercises') {
            closeWindow('exercices_flash');
            closeWindow('qcm_flash');
        } else if (id === 'exercices_flash' || id === 'qcm_flash') {
            closeWindow('exercises');
        }
        
        // Ouvrir la fenêtre demandée
        win.style.display = 'block';
        console.log("Fenêtre affichée");
        bringToFront(win);
        
        // Centrer et dimensionner la fenêtre
        const viewportWidth = window.innerWidth;
        const viewportHeight = window.innerHeight;
        const winWidth = viewportWidth * 0.95;
        const winHeight = viewportHeight * 0.90;
        
        win.style.width = `${winWidth}px`;
        win.style.height = `${winHeight}px`;
        win.style.left = `${(viewportWidth - winWidth) / 2}px`;
        win.style.top = `${(viewportHeight - winHeight) / 2}px`;
        console.log("Fenêtre dimensionnée et positionnée");
    } else {
        console.error('Fenêtre non trouvée:', winId);
        // Lister toutes les fenêtres disponibles
        console.log("Fenêtres disponibles:");
        document.querySelectorAll('.window').forEach(win => {
            console.log("- ID:", win.id);
        });
    }
}

// Fonction pour ouvrir une fenêtre externe
function openExternalWindow(linkId, linkName, linkUrl, linkIcon) {
    // Vérifier si la fenêtre existe déjà
    const winId = 'external-' + linkId + '-window';
    let win = document.getElementById(winId);
    
    if (win) {
        // Si la fenêtre existe déjà, l'afficher et la mettre au premier plan
        win.style.display = 'block';
        bringToFront(win);
    } else {
        // Sinon, créer une nouvelle fenêtre
        const windowDiv = document.createElement('div');
        windowDiv.id = winId;
        windowDiv.className = 'window';
        windowDiv.style.display = 'block';
        
        // Créer l'en-tête de la fenêtre
        const headerDiv = document.createElement('div');
        headerDiv.className = 'window-header';
        
        const titleDiv = document.createElement('div');
        titleDiv.innerHTML = `<i class="fas ${linkIcon}"></i> <span>${linkName}</span>`;
        
        const closeBtn = document.createElement('div');
        closeBtn.className = 'close-btn';
        closeBtn.innerHTML = '<i class="fas fa-times"></i>';
        closeBtn.onclick = function() { closeWindow('external-' + linkId); };
        
        headerDiv.appendChild(titleDiv);
        headerDiv.appendChild(closeBtn);
        
        // Créer le contenu de la fenêtre
        const contentDiv = document.createElement('div');
        contentDiv.className = 'window-content overflow-auto p-0';
        
        // Créer l'iframe
        const iframe = document.createElement('iframe');
        iframe.src = linkUrl;
        iframe.style.width = '100%';
        iframe.style.height = '100%';
        iframe.style.border = 'none';
        iframe.id = 'external-' + linkId + '-iframe';
        
        contentDiv.appendChild(iframe);
        
        // Assembler la fenêtre
        windowDiv.appendChild(headerDiv);
        windowDiv.appendChild(contentDiv);
        
        // Ajouter la fenêtre au document
        document.body.appendChild(windowDiv);
        
        // Rendre la fenêtre déplaçable
        makeWindowDraggable(windowDiv);
        
        // Centrer et dimensionner la fenêtre
        const viewportWidth = window.innerWidth;
        const viewportHeight = window.innerHeight;
        const winWidth = viewportWidth * 0.95;
        const winHeight = viewportHeight * 0.90;
        
        windowDiv.style.width = `${winWidth}px`;
        windowDiv.style.height = `${winHeight}px`;
        windowDiv.style.left = `${(viewportWidth - winWidth) / 2}px`;
        windowDiv.style.top = `${(viewportHeight - winHeight) / 2}px`;
        
        // Mettre la fenêtre au premier plan
        bringToFront(windowDiv);
        
        // Stocker la référence à la fenêtre
        externalWindows[linkId] = windowDiv;
    }
}

// Fonction pour rendre une fenêtre déplaçable
function makeWindowDraggable(windowElement) {
    const header = windowElement.querySelector('.window-header');
    let dragOffsetX = 0;
    let dragOffsetY = 0;
    let windowIsDragging = false;

    header.addEventListener('mousedown', function(e) {
        windowIsDragging = true;
        dragOffsetX = e.clientX - windowElement.offsetLeft;
        dragOffsetY = e.clientY - windowElement.offsetTop;
        bringToFront(windowElement);
});


    document.addEventListener('mousemove', function(e) {
        if (!windowIsDragging) return;
        windowElement.style.left = (e.clientX - dragOffsetX) + 'px';
        windowElement.style.top = (e.clientY - dragOffsetY) + 'px';
    });

    document.addEventListener('mouseup', function() {
        windowIsDragging = false;
    });
}

function closeWindow(id) {
    const win = document.getElementById(id + '-window');
    if(win) {
        win.style.display = 'none';
    }
}

// Fonction pour changer l'image de fond et sauvegarder la préférence
async function changeBackground(imageName) {
    document.body.style.backgroundImage = `url('/static/img/${imageName}')`;
    
    // Sauvegarder la préférence
    if (window.widgetManager) {
        await window.widgetManager.saveBackground(imageName);
    }
}

// Fonction pour basculer entre les thèmes clair et sombre
function toggleDarkTheme(isDark) {
    if (isDark) {
        document.body.classList.add('dark-theme');
        localStorage.setItem('darkTheme', 'true');
    } else {
        document.body.classList.remove('dark-theme');
        localStorage.setItem('darkTheme', 'false');
    }
    
    // Propager le changement de thème aux iframes
    document.querySelectorAll('iframe').forEach(iframe => {
        try {
            const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
            if (isDark) {
                iframeDoc.body.classList.add('dark-theme');
            } else {
                iframeDoc.body.classList.remove('dark-theme');
            }
        } catch (e) {
            // Ignorer les erreurs de sécurité cross-origin
            console.log('Impossible de propager le thème à une iframe (probablement cross-origin)');
        }
    });
}

// Fonction pour afficher/masquer le profil dans le tableau de bord
function showProfileInDashboard() {
    const profileSection = document.getElementById('dashboard-profile-section');
    if (profileSection) {
        // Si la section est déjà visible, la masquer
        if (profileSection.style.display === 'block') {
            profileSection.style.display = 'none';
        } else {
            // Sinon, l'afficher
            profileSection.style.display = 'block';
            
            // Faire défiler jusqu'à la section de profil
            profileSection.scrollIntoView({ behavior: 'smooth' });
        }
    }
}

// Fonction pour marquer un devoir comme fait/non fait via AJAX
function toggleHomework(homeworkId, isChecked) {
    const form = document.getElementById('homework-form-' + homeworkId);
    
    // Utiliser Fetch API pour soumettre le formulaire en AJAX
    fetch(form.action, {
        method: 'POST',
        body: new FormData(form),
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Erreur réseau');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Mettre à jour l'interface utilisateur
            const checkbox = form.querySelector('input[type="checkbox"]');
            checkbox.checked = isChecked;
        } else {
            console.error('Erreur lors de la mise à jour du devoir');
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        // En cas d'erreur, revenir à l'état précédent
        const checkbox = form.querySelector('input[type="checkbox"]');
        checkbox.checked = !isChecked;
    });
}

// Fonction pour charger le message de bienvenue
function loadWelcomeMessage() {
    // Vérifier si les éléments existent
    const contentElement = document.getElementById('welcome-message-content');
    const infoElement = document.getElementById('welcome-message-info');
    
    if (!contentElement || !infoElement) {
        return; // Sortir si les éléments n'existent pas
    }
    
    // Charger le message de bienvenue
    fetch('/welcome/get_latest')
        .then(function(response) {
            return response.json();
        })
        .then(function(data) {
            // Formater le contenu (similaire à la fonction updatePreview dans welcome_editor.js)
            let html = data.content;
            
            // Remplacer les liens markdown
            html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');
            
            // Remplacer le markdown basique
            html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
            html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
            html = html.replace(/`(.*?)`/g, '<code>$1</code>');
            
            // Remplacer les titres
            html = html.replace(/^# (.*?)$/gm, '<h1>$1</h1>');
            html = html.replace(/^## (.*?)$/gm, '<h2>$1</h2>');
            html = html.replace(/^### (.*?)$/gm, '<h3>$1</h3>');
            
            // Remplacer les listes
            html = html.replace(/^- (.*?)$/gm, '<li>$1</li>');
            html = html.replace(/(<li>.*?<\/li>)+/g, '<ul>$&</ul>');
            
            // Remplacer les sauts de ligne
            html = html.replace(/\n/g, '<br>');
            
            // Appliquer le contenu formaté
            contentElement.innerHTML = html;
            infoElement.textContent = "Mis à jour le " + data.updated_at + " par " + data.created_by;
            
            // Ajouter des styles pour améliorer l'apparence
            contentElement.style.padding = '10px';
            contentElement.style.lineHeight = '1.5';
            
            // Styles pour les éléments spécifiques
            const headings = contentElement.querySelectorAll('h1, h2, h3');
            headings.forEach(heading => {
                heading.style.marginBottom = '10px';
                heading.style.fontWeight = 'bold';
            });
            
            const lists = contentElement.querySelectorAll('ul');
            lists.forEach(list => {
                list.style.marginLeft = '20px';
                list.style.marginBottom = '10px';
            });
        })
        .catch(function(error) {
            console.error('Erreur lors du chargement du message de bienvenue:', error);
            contentElement.innerHTML = '<p>Bienvenue sur votre espace élève Pyteur!</p>';
            infoElement.textContent = '';
        });
}

// Fonction pour ouvrir le panneau de configuration des widgets
function openWidgetsPanel() {
    if (window.widgetManager) {
        window.widgetManager.openConfigPanel();
    } else {
        console.error('Gestionnaire de widgets non initialisé');
    }
}

// --- Gestion du sous-menu "Liens externes" ---
function setupExternalLinksMenu() {
    const externalLinksMenuItem = document.getElementById('external-links-menu-item');
    if (externalLinksMenuItem) {
        // Gestion ouverture/fermeture au clic
        externalLinksMenuItem.addEventListener('click', function (e) {
            e.stopPropagation();
            // Fermer les autres sous-menus si besoin
            document.querySelectorAll('.menu-item-has-submenu.open').forEach(item => {
                if (item !== externalLinksMenuItem) item.classList.remove('open', 'open-up');
            });

            // Toggle open
            externalLinksMenuItem.classList.toggle('open');

            // Détecter si c'est le dernier item visible du menu
            const menuItems = Array.from(externalLinksMenuItem.parentNode.querySelectorAll('.menu-item, .menu-item-has-submenu'));
            const visibleMenuItems = menuItems.filter(item => item.offsetParent !== null);
            const isLast = visibleMenuItems[visibleMenuItems.length - 1] === externalLinksMenuItem;

            if (isLast) {
                externalLinksMenuItem.classList.add('open-up');
            } else {
                externalLinksMenuItem.classList.remove('open-up');
            }
        });

        // Fermer le sous-menu si on clique ailleurs
        document.addEventListener('click', function () {
            externalLinksMenuItem.classList.remove('open', 'open-up');
        });

        // Empêcher la fermeture si on clique dans le sous-menu
        const submenu = document.getElementById('external-links-submenu');
        if (submenu) {
            submenu.addEventListener('click', function (e) {
                e.stopPropagation();
            });
        }
    }
}

// Système de notifications
function showNotification(title, message, type = 'info') {
    // Créer l'élément de notification
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-header">
            <div class="notification-title">${title}</div>
            <div class="notification-close">&times;</div>
        </div>
        <div class="notification-body">${message}</div>
    `;
    
    // Ajouter au conteneur de notifications (le créer s'il n'existe pas)
    let container = document.getElementById('notifications-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'notifications-container';
        document.body.appendChild(container);
    }
    
    container.appendChild(notification);
    
    // Gérer la fermeture
    const closeBtn = notification.querySelector('.notification-close');
    closeBtn.addEventListener('click', () => {
        notification.classList.add('notification-hiding');
        setTimeout(() => {
            notification.remove();
        }, 300);
    });
    
    // Fermer automatiquement après 5 secondes
    setTimeout(() => {
        if (notification.parentNode) {
            notification.classList.add('notification-hiding');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 300);
        }
    }, 5000);
}

// Fonctions pour minimiser et maximiser les fenêtres
function minimizeWindow(id) {
    console.log("minimizeWindow appelé pour:", id);
    // Pour l'instant, on se contente de fermer la fenêtre
    closeWindow(id);
}

function maximizeWindow(id) {
    console.log("maximizeWindow appelé pour:", id);
    const win = document.getElementById(id + '-window');
    if(win) {
        // Mettre la fenêtre en plein écran
        win.style.width = '100%';
        win.style.height = '100%';
        win.style.left = '0';
        win.style.top = '0';
        bringToFront(win);
    }
}

// Fonction pour ouvrir un document dans la fenêtre
function openDocumentViewer(documentUrl, documentTitle) {
    console.log("openDocumentViewer appelé avec:", documentUrl, documentTitle);
    
    // Vérifier si la fenêtre existe
    const win = document.getElementById('documentViewer-window');
    console.log("Fenêtre documentViewer-window:", win);
    
    if (!win) {
        console.error("La fenêtre documentViewer-window n'existe pas!");
        return;
    }
    
    // Mettre à jour le titre
    const titleElement = document.getElementById('documentViewerTitle');
    if (titleElement) {
        titleElement.textContent = documentTitle || 'Visualiseur de document';
    } else {
        console.error("L'élément documentViewerTitle n'existe pas!");
    }
    
    // Mettre à jour l'iframe avec l'URL du document
    const frameElement = document.getElementById('documentViewerFrame');
    if (frameElement) {
        frameElement.src = documentUrl;
    } else {
        console.error("L'élément documentViewerFrame n'existe pas!");
    }
    
    // Mettre à jour le bouton de téléchargement
    const downloadBtn = document.getElementById('documentDownloadBtn');
    if (downloadBtn) {
        downloadBtn.onclick = function() {
            window.open(documentUrl, '_blank');
        };
    } else {
        console.error("L'élément documentDownloadBtn n'existe pas!");
    }
    
    // Configurer le bouton plein écran
    const fullscreenBtn = document.getElementById('documentFullscreenBtn');
    if (fullscreenBtn) {
        fullscreenBtn.onclick = function() {
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
    } else {
        console.error("L'élément documentFullscreenBtn n'existe pas!");
    }
    
    // Ouvrir la fenêtre
    console.log("Appel de openWindow('documentViewer')");
    openWindow('documentViewer');
}

// Écouteur d'événements pour les messages postMessage
window.addEventListener('message', function(event) {
    console.log("Message reçu:", event.data);
    console.log("Source du message:", event.source);
    console.log("Origine du message:", event.origin);
    
    // Vérifier si le message est du type attendu
    if (event.data && event.data.type === 'openDocument') {
        console.log("Message openDocument reçu, appel de openDocumentViewer");
        console.log("URL du document:", event.data.documentUrl);
        console.log("Titre du document:", event.data.documentTitle);
        
        try {
            // Appeler la fonction openDocumentViewer avec les paramètres reçus
            openDocumentViewer(event.data.documentUrl, event.data.documentTitle);
            console.log("Fonction openDocumentViewer appelée avec succès");
        } catch (error) {
            console.error("Erreur lors de l'appel de openDocumentViewer:", error);
        }
    } else {
        console.log("Message non reconnu ou de type incorrect");
    }
});

// Initialisation au chargement de la page
window.addEventListener('DOMContentLoaded', () => {
    // Vérifier si l'utilisateur a choisi d'ouvrir automatiquement le tableau de bord
    const autoStartDashboard = localStorage.getItem('autoStartDashboard');
    // Si aucune préférence n'est définie ou si la préférence est true, ouvrir le tableau de bord
    if (autoStartDashboard === null || autoStartDashboard === 'true') {
        openWindow('dashboard');
    }
    
    // Restaurer le thème préféré de l'utilisateur
    const darkTheme = localStorage.getItem('darkTheme') === 'true';
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.checked = darkTheme;
        toggleDarkTheme(darkTheme);
        
        // Rendre visible le toggle de thème
        const themeToggleContainer = document.querySelector('.theme-toggle');
        if (themeToggleContainer) {
            themeToggleContainer.style.display = 'flex';
        }
    }
    
    // Fermer le menu démarrer quand on clique sur un élément
    document.querySelectorAll('.start-menu .menu-item').forEach(item => {
        item.addEventListener('click', () => {
            document.getElementById('startMenu').style.display = 'none';
        });
    });
    
    // Initialisation des particules pour le logo PYTEUR
    if (typeof particlesJS !== 'undefined') {
        particlesJS('particles-js', {
            "particles": {
                "number": {
                    "value": 100,
                    "density": {
                        "enable": true,
                        "value_area": 800
                    }
                },
                "color": {
                    "value": ["#ff00ff", "#00ffff", "#ffff00"]
                },
                "shape": {
                    "type": "circle",
                    "stroke": {
                        "width": 0,
                        "color": "#000000"
                    }
                },
                "opacity": {
                    "value": 0.8,
                    "random": true,
                    "anim": {
                        "enable": true,
                        "speed": 1,
                        "opacity_min": 0.1,
                        "sync": false
                    }
                },
                "size": {
                    "value": 3,
                    "random": true,
                    "anim": {
                        "enable": true,
                        "speed": 4,
                        "size_min": 0.3,
                        "sync": false
                    }
                },
                "line_linked": {
                    "enable": true,
                    "distance": 150,
                    "color": "#ff00ff",
                    "opacity": 0.4,
                    "width": 1
                },
                "move": {
                    "enable": true,
                    "speed": 2,
                    "direction": "none",
                    "random": true,
                    "straight": false,
                    "out_mode": "out",
                    "bounce": false,
                    "attract": {
                        "enable": true,
                        "rotateX": 600,
                        "rotateY": 1200
                    }
                }
            },
            "interactivity": {
                "detect_on": "canvas",
                "events": {
                    "onhover": {
                        "enable": true,
                        "mode": "repulse"
                    },
                    "onclick": {
                        "enable": true,
                        "mode": "push"
                    },
                    "resize": true
                },
                "modes": {
                    "repulse": {
                        "distance": 100,
                        "duration": 0.4
                    },
                    "push": {
                        "particles_nb": 4
                    }
                }
            },
            "retina_detect": true
        });
    }

    // Animation des lettres PYTEUR
    const pyteurText = document.getElementById('pyteur-text');
    if (pyteurText && typeof gsap !== 'undefined') {
        const letters = pyteurText.querySelectorAll('.letter');
        
        pyteurText.addEventListener('mouseenter', function() {
            letters.forEach((letter, index) => {
                // Animation de déconstruction
                gsap.to(letter, {
                    duration: 0.5,
                    x: (Math.random() - 0.5) * 100,
                    y: (Math.random() - 0.5) * 100,
                    rotation: (Math.random() - 0.5) * 360,
                    opacity: 0,
                    ease: "power2.out",
                    delay: index * 0.1
                });
                
                // Animation de reconstruction
                gsap.to(letter, {
                    duration: 0.3,
                    x: 0,
                    y: 0,
                    rotation: 0,
                    opacity: 1,
                    ease: "power2.in",
                    delay: index * 0.1 + 0.5
                });
            });
            
            // Effet de couleur aléatoire
            const colors = ['#ff00ff', '#00ffff', '#ffff00', '#ff0000', '#00ff00', '#0000ff'];
            letters.forEach(letter => {
                const randomColor = colors[Math.floor(Math.random() * colors.length)];
                gsap.to(letter, {
                    duration: 0.3,
                    color: randomColor,
                    delay: 0.8
                });
            });
        });

        // Effet de glitch aléatoire
        setInterval(() => {
            if (Math.random() > 0.7) {
                pyteurText.style.animation = 'glitch 0.3s';
                setTimeout(() => {
                    pyteurText.style.animation = 'glitch 2s infinite alternate';
                }, 300);
            }
        }, 3000);
    }
    
    // Charger le message de bienvenue
    loadWelcomeMessage();

    // Horloge
    function updateDateTime() {
        const now = new Date();
        const timeElement = document.getElementById('time');
        const dateElement = document.getElementById('date');
        if (timeElement && dateElement) {
            timeElement.textContent = now.toLocaleTimeString();
            dateElement.textContent = now.toLocaleDateString();
        }
    }
    setInterval(updateDateTime, 1000);
    updateDateTime();
    
    // Initialiser le menu des liens externes
    setupExternalLinksMenu();
    
    // Rendre toutes les fenêtres déplaçables
    document.querySelectorAll('.window').forEach(windowElement => {
        makeWindowDraggable(windowElement);
    });
    
    // Ajouter une notification de bienvenue
    setTimeout(() => {
        showNotification('Bienvenue sur PYTEUR OS', 'Votre environnement de travail est prêt !', 'success');
    }, 1000);
});
