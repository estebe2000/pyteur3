// Script de débogage pour les widgets
document.addEventListener('DOMContentLoaded', function() {
    console.log('Script de débogage des widgets chargé');
    
    // Créer un widget de test directement
    setTimeout(function() {
        createDebugWidget();
    }, 2000); // Attendre 2 secondes pour s'assurer que la page est complètement chargée
});

function createDebugWidget() {
    console.log('Création du widget de débogage');
    
    // Créer l'élément du widget
    const widget = document.createElement('div');
    widget.className = 'widget debug-widget';
    widget.style.position = 'absolute';
    widget.style.width = '300px';
    widget.style.height = '200px';
    widget.style.backgroundColor = 'rgba(255, 255, 255, 0.9)';
    widget.style.borderRadius = '8px';
    widget.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.2)';
    widget.style.zIndex = '9999';
    widget.style.left = '100px';
    widget.style.top = '100px';
    widget.style.display = 'block';
    widget.style.overflow = 'hidden';
    
    // Créer l'en-tête du widget
    const header = document.createElement('div');
    header.style.background = 'linear-gradient(90deg, #4f46e5, #7c3aed)';
    header.style.color = 'white';
    header.style.padding = '8px 12px';
    header.style.display = 'flex';
    header.style.justifyContent = 'space-between';
    header.style.alignItems = 'center';
    header.innerHTML = '<div>Widget de débogage</div><div style="cursor:pointer;">×</div>';
    widget.appendChild(header);
    
    // Créer le contenu du widget
    const content = document.createElement('div');
    content.style.padding = '15px';
    content.innerHTML = `
        <h3 style="margin-top:0;">Test d'affichage</h3>
        <p>Si vous voyez ce widget, cela signifie que l'affichage des widgets fonctionne correctement.</p>
        <p>Heure actuelle: ${new Date().toLocaleTimeString()}</p>
        <button id="debug-widget-btn" style="padding:8px 12px; background:#4f46e5; color:white; border:none; border-radius:4px; cursor:pointer;">Tester</button>
    `;
    widget.appendChild(content);
    
    // Ajouter le widget au document
    document.body.appendChild(widget);
    console.log('Widget de débogage ajouté au document');
    
    // Rendre le widget déplaçable
    makeWidgetDraggable(widget, header);
    
    // Ajouter un événement au bouton
    const button = document.getElementById('debug-widget-btn');
    if (button) {
        button.addEventListener('click', function() {
            alert('Le widget fonctionne !');
        });
    }
    
    // Gérer la fermeture du widget
    const closeBtn = header.querySelector('div:last-child');
    closeBtn.addEventListener('click', function() {
        widget.remove();
    });
}

function makeWidgetDraggable(widget, header) {
    let isDragging = false;
    let offsetX, offsetY;
    
    header.addEventListener('mousedown', function(e) {
        isDragging = true;
        offsetX = e.clientX - widget.getBoundingClientRect().left;
        offsetY = e.clientY - widget.getBoundingClientRect().top;
        widget.style.cursor = 'grabbing';
    });
    
    document.addEventListener('mousemove', function(e) {
        if (!isDragging) return;
        
        const x = e.clientX - offsetX;
        const y = e.clientY - offsetY;
        
        widget.style.left = `${x}px`;
        widget.style.top = `${y}px`;
    });
    
    document.addEventListener('mouseup', function() {
        isDragging = false;
        widget.style.cursor = 'default';
    });
}
