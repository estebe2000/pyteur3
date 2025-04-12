// Fonctions pour l'éditeur de texte enrichi du message de bienvenue

// Fonction pour formater le texte
function formatText(type, targetId = 'content') {
    const textarea = document.getElementById(targetId);
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = textarea.value.substring(start, end);
    let formattedText = '';
    
    switch(type) {
        case 'bold':
            formattedText = `**${selectedText}**`;
            break;
        case 'italic':
            formattedText = `*${selectedText}*`;
            break;
        case 'list':
            formattedText = `\n- ${selectedText.split('\n').join('\n- ')}`;
            break;
        case 'heading':
            formattedText = `# ${selectedText}`;
            break;
        case 'link':
            const url = prompt('Entrez l\'URL:', 'https://');
            if (url) {
                formattedText = `[${selectedText || 'Lien'}](${url})`;
            } else {
                return; // Annulé
            }
            break;
        default:
            formattedText = selectedText;
    }
    
    textarea.value = 
        textarea.value.substring(0, start) + 
        formattedText + 
        textarea.value.substring(end);
    
    // Replacer le curseur après le texte formaté
    textarea.focus();
    textarea.selectionStart = start + formattedText.length;
    textarea.selectionEnd = start + formattedText.length;
    
    // Mettre à jour l'aperçu
    updatePreview();
}

// Fonction pour afficher le sélecteur de couleur
function showColorPicker(targetId = 'content') {
    const colors = [
        '#ff0000', '#ff7f00', '#ffff00', '#00ff00', 
        '#0000ff', '#4b0082', '#9400d3', '#000000'
    ];
    
    // Créer un div pour le sélecteur de couleur
    let colorPicker = document.getElementById('colorPicker');
    if (!colorPicker) {
        colorPicker = document.createElement('div');
        colorPicker.id = 'colorPicker';
        colorPicker.className = 'color-picker';
        colorPicker.style.position = 'absolute';
        colorPicker.style.display = 'flex';
        colorPicker.style.flexWrap = 'wrap';
        colorPicker.style.width = '160px';
        colorPicker.style.padding = '5px';
        colorPicker.style.backgroundColor = '#fff';
        colorPicker.style.border = '1px solid #ccc';
        colorPicker.style.borderRadius = '4px';
        colorPicker.style.boxShadow = '0 2px 5px rgba(0,0,0,0.2)';
        colorPicker.style.zIndex = '1000';
        
        // Ajouter les couleurs
        colors.forEach(color => {
            const colorBtn = document.createElement('div');
            colorBtn.style.width = '30px';
            colorBtn.style.height = '30px';
            colorBtn.style.margin = '5px';
            colorBtn.style.backgroundColor = color;
            colorBtn.style.cursor = 'pointer';
            colorBtn.style.borderRadius = '4px';
            colorBtn.onclick = function() {
                applyColor(color, targetId);
                colorPicker.style.display = 'none';
            };
            colorPicker.appendChild(colorBtn);
        });
        
        document.body.appendChild(colorPicker);
    } else {
        colorPicker.style.display = 'flex';
    }
    
    // Positionner le sélecteur de couleur
    const button = event.target.closest('button');
    const rect = button.getBoundingClientRect();
    colorPicker.style.top = (rect.bottom + window.scrollY) + 'px';
    colorPicker.style.left = (rect.left + window.scrollX) + 'px';
    
    // Fermer le sélecteur de couleur si on clique ailleurs
    document.addEventListener('click', function closeColorPicker(e) {
        if (!colorPicker.contains(e.target) && e.target !== button) {
            colorPicker.style.display = 'none';
            document.removeEventListener('click', closeColorPicker);
        }
    });
}

// Fonction pour appliquer une couleur au texte
function applyColor(color, targetId) {
    const textarea = document.getElementById(targetId);
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = textarea.value.substring(start, end);
    
    const formattedText = `<span style="color:${color}">${selectedText}</span>`;
    
    textarea.value = 
        textarea.value.substring(0, start) + 
        formattedText + 
        textarea.value.substring(end);
    
    // Replacer le curseur après le texte formaté
    textarea.focus();
    textarea.selectionStart = start + formattedText.length;
    textarea.selectionEnd = start + formattedText.length;
    
    // Mettre à jour l'aperçu
    updatePreview();
}

// Fonction pour mettre à jour l'aperçu
function updatePreview() {
    const content = document.getElementById('content').value;
    const preview = document.getElementById('preview');
    
    if (preview) {
        // Convertir le markdown en HTML
        let html = content;
        
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
        
        preview.innerHTML = html;
    }
}

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    // Mettre à jour l'aperçu au chargement
    updatePreview();
    
    // Mettre à jour l'aperçu lors de la saisie
    const contentTextarea = document.getElementById('content');
    if (contentTextarea) {
        contentTextarea.addEventListener('input', updatePreview);
    }
});
