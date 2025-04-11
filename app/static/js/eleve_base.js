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
    let winId = id + '-window';
    const win = document.getElementById(winId);
    
    if(win) {
        // Fermer les fenêtres incompatibles si nécessaire
        if (id === 'exercises') {
            closeWindow('exercices_flash');
            closeWindow('qcm_flash');
        } else if (id === 'exercices_flash' || id === 'qcm_flash') {
            closeWindow('exercises');
        }
        
        // Ouvrir la fenêtre demandée
        win.style.display = 'block';
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
    } else {
        console.error('Fenêtre non trouvée:', winId);
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

// Fonction pour changer l'image de fond
function changeBackground(imageName) {
    document.body.style.backgroundImage = `url('/static/img/${imageName}')`;
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
            contentElement.innerHTML = data.content;
            infoElement.textContent = "Mis à jour le " + data.updated_at + " par " + data.created_by;
        })
        .catch(function(error) {
            console.error('Erreur lors du chargement du message de bienvenue:', error);
            contentElement.innerHTML = '<p>Bienvenue sur votre espace élève Pyteur!</p>';
            infoElement.textContent = '';
        });
}

// Gestion du déplacement des fenêtres
window.addEventListener('DOMContentLoaded', () => {
    // Vérifier si l'utilisateur a choisi d'ouvrir automatiquement le tableau de bord
    const autoStartDashboard = localStorage.getItem('autoStartDashboard');
    // Si aucune préférence n'est définie ou si la préférence est true, ouvrir le tableau de bord
    if (autoStartDashboard === null || autoStartDashboard === 'true') {
        openWindow('dashboard');
    }
    
    // Restaurer le thème préféré de l'utilisateur
    const darkTheme = localStorage.getItem('darkTheme') === 'true';
    document.getElementById('themeToggle').checked = darkTheme;
    toggleDarkTheme(darkTheme);
    
    // Fermer le menu démarrer quand on clique sur un élément
    document.querySelectorAll('.start-menu .menu-item').forEach(item => {
        item.addEventListener('click', () => {
            document.getElementById('startMenu').style.display = 'none';
        });
    });
    
    // Charger le message de bienvenue
    loadWelcomeMessage();

    // Horloge
    function updateDateTime() {
        const now = new Date();
        const timeElement = document.getElementById('time');
        const dateElement = document.getElementById('date');
        timeElement.textContent = now.toLocaleTimeString();
        dateElement.textContent = now.toLocaleDateString();
    }
    setInterval(updateDateTime, 1000);
    updateDateTime();

    // Rendre toutes les fenêtres déplaçables
        document.querySelectorAll('.window').forEach(windowElement => {
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
        });
});
