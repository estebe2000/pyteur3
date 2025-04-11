const labels_js = JSON.parse(document.getElementById('labels_json').textContent);
let data = {};
let selectedNiveau = null;
let selectedTheme = null;
let selectedDifficulte = 0;

async function chargerData() {
    try {
        const response = await fetch('/api/generateur_data');
        data = await response.json();

        const niveauContainer = document.getElementById('niveauContainer');
        niveauContainer.innerHTML = '';

        const ordreNiveaux = ["Troisième", "SNT", "Première", "Terminale"];

        ordreNiveaux.forEach(niveau => {
            if (data[niveau]) {
                const btn = document.createElement('div');
                btn.className = 'btn-choice';
                btn.textContent = niveau;
                btn.dataset.value = niveau;
                btn.addEventListener('click', () => {
                    selectedNiveau = niveau;
                    selectedTheme = null;
                    selectedDifficulte = 0;
                    updateSelection();
                    afficherThemes();
                    updateDescription();
                });
                niveauContainer.appendChild(btn);
            }
        });

        // Ajouter les autres niveaux non listés explicitement
        Object.keys(data).forEach(niveau => {
            if (!ordreNiveaux.includes(niveau)) {
                const btn = document.createElement('div');
                btn.className = 'btn-choice';
                btn.textContent = niveau;
                btn.dataset.value = niveau;
                btn.addEventListener('click', () => {
                    selectedNiveau = niveau;
                    selectedTheme = null;
                    selectedDifficulte = 0;
                    updateSelection();
                    afficherThemes();
                    updateDescription();
                });
                niveauContainer.appendChild(btn);
            }
        });
    } catch (error) {
        console.error('Erreur chargement données:', error);
    }
}

function afficherThemes() {
    const themeContainer = document.getElementById('themeContainer');
    themeContainer.innerHTML = '';
    if (!selectedNiveau || !data[selectedNiveau]) return;

    data[selectedNiveau].forEach(themeObj => {
        const btn = document.createElement('div');
        btn.className = 'btn-choice';
        btn.textContent = themeObj.thème;
        btn.dataset.value = themeObj.thème;
        btn.addEventListener('click', () => {
            selectedTheme = themeObj.thème;
            selectedDifficulte = 0;
            updateSelection();
            updateDescription();
        });
        themeContainer.appendChild(btn);
    });
}

function updateSelection() {
    document.querySelectorAll('#niveauContainer .btn-choice').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.value === selectedNiveau);
    });
    document.querySelectorAll('#themeContainer .btn-choice').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.value === selectedTheme);
    });
    document.querySelectorAll('.star').forEach(star => {
        const val = parseInt(star.dataset.value);
        if (val <= selectedDifficulte) {
            star.classList.add('selected');
        } else {
            star.classList.remove('selected');
        }
    });
}

function updateDescription() {
    const descriptionExercice = document.getElementById('descriptionExercice');
    const genererBtn = document.getElementById('genererBtn');

    if (selectedNiveau && selectedTheme && selectedDifficulte && data[selectedNiveau]) {
        const themeObj = data[selectedNiveau].find(t => t.thème === selectedTheme);
        if (themeObj) {
            const nivObj = themeObj.niveaux.find(n => n.niveau === selectedDifficulte);
            if (nivObj) {
                descriptionExercice.textContent = nivObj.description;
                genererBtn.disabled = false;
                genererBtn.classList.remove('bg-gray-400');
                genererBtn.classList.add('bg-blue-600', 'hover:bg-blue-700');
                return;
            }
        }
    }
    descriptionExercice.textContent = document.getElementById('select_all_fields_text').textContent;
    genererBtn.disabled = true;
    genererBtn.classList.remove('bg-blue-600', 'hover:bg-blue-700');
    genererBtn.classList.add('bg-gray-400');
}

async function genererExercice() {
    const niveau = selectedNiveau;
    const theme = selectedTheme;
    const difficulte = selectedDifficulte;
    const description = document.getElementById('descriptionExercice').textContent;

    const resultatIA = document.getElementById('resultatIA');
    const promptAffiche = document.getElementById('promptAffiche');

    // Désactiver les boutons pendant la génération
    const actionButtons = ['downloadNotebookBtn', 'downloadScriptBtn', 'ouvrirConsoleBtn', 'ouvrirNotebookBtn'];
    actionButtons.forEach(id => {
        const btn = document.getElementById(id);
        btn.disabled = true;
        btn.classList.remove('bg-blue-600', 'hover:bg-blue-700');
        btn.classList.add('bg-gray-400');
    });

    resultatIA.textContent = document.getElementById('generating_text').textContent;
    promptAffiche.textContent = document.getElementById('building_prompt_text').textContent;

    try {
        // Récupérer la valeur debutant depuis le JSON pédagogique
        let debutant = false;
        if (data[niveau]) {
            const themeObj = data[niveau].find(t => t.thème === theme);
            if (themeObj && themeObj.niveaux) {
                const niveauObj = themeObj.niveaux.find(n => n.niveau === difficulte);
                if (niveauObj && typeof niveauObj.debutant !== 'undefined') {
                    debutant = niveauObj.debutant;
                }
            }
        }

        // Récupérer le jeton CSRF
        const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
        
        const responsePrompt = await fetch('/api/generer_exercice', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                niveau: niveau,
                theme: theme,
                difficulte: difficulte,
                description: description,
                debutant: debutant
            })
        });
        
        if (!responsePrompt.ok) {
            const contentType = responsePrompt.headers.get("content-type");
            if (contentType && contentType.indexOf("application/json") !== -1) {
                // Si c'est du JSON, on peut le parser
                const errorData = await responsePrompt.json();
                promptAffiche.textContent = document.getElementById('error_generating_prompt_text').textContent + " " + (errorData.error || responsePrompt.statusText);
            } else {
                // Si ce n'est pas du JSON, on affiche juste le statut
                promptAffiche.textContent = document.getElementById('error_generating_prompt_text').textContent + " " + responsePrompt.status + " " + responsePrompt.statusText;
            }
            resultatIA.textContent = "";
            return;
        }
        
        const dataPrompt = await responsePrompt.json();

        if (dataPrompt.error) {
            promptAffiche.textContent = document.getElementById('error_generating_prompt_text').textContent + " " + dataPrompt.error;
            resultatIA.textContent = "";
            return;
        }

        promptAffiche.textContent = dataPrompt.prompt || document.getElementById('prompt_unavailable_text').textContent;
        resultatIA.textContent = dataPrompt.response || document.getElementById('response_unavailable_text').textContent;

        // Réactiver les boutons après génération
        actionButtons.forEach(id => {
            const btn = document.getElementById(id);
            btn.disabled = false;
            btn.classList.remove('bg-gray-400');
            btn.classList.add('bg-blue-600', 'hover:bg-blue-700');
        });
    } catch (error) {
        promptAffiche.textContent = "";
        resultatIA.textContent = document.getElementById('request_error_text').textContent + " " + error;
    }
}

function togglePrompt() {
    const promptPre = document.getElementById('promptAffiche');
    const toggleBtn = document.getElementById('togglePromptBtn');
    if (promptPre.style.display === 'none') {
        promptPre.style.display = 'block';
        toggleBtn.textContent = labels_js['hide_prompt'];
    } else {
        promptPre.style.display = 'none';
        toggleBtn.textContent = labels_js['show_prompt'];
    }
}

function toggleResultat() {
    const pre = document.getElementById('resultatIA');
    const btn = document.getElementById('toggleResultatBtn');
    if (pre.style.display === 'none') {
        pre.style.display = 'block';
        btn.textContent = labels_js['hide_generated_exercise'];
    } else {
        pre.style.display = 'none';
        btn.textContent = labels_js['show_generated_exercise'];
    }
}

async function downloadNotebook() {
    const code = document.getElementById('resultatIA').textContent;
    const notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": code.split('\n').map(function(line) { return line + '\n'; })
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.8"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 2
    };

    try {
        // Récupérer le jeton CSRF
        const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
        
        // Envoi automatique du notebook au serveur
        const response = await fetch('/api/upload_notebook', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(notebook)
        });
        
        const data = await response.json();
        
        if (!response.ok || data.error) {
            console.error('Erreur upload notebook:', data.error || 'Erreur serveur');
        }
        
        // Téléchargement local du notebook
        const blob = new Blob([JSON.stringify(notebook, null, 2)], {type: "application/json"});
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = "exercice.ipynb";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
    } catch (err) {
        console.error('Erreur upload notebook:', err);
    }
}

async function ouvrirConsole() {
    const raw = document.getElementById('resultatIA').textContent;

    let transformed = '';
    const codeBlockRegex = /```(?:python)?\n([\s\S]*?)```/g;
    let lastIndex = 0;
    let match;

    while ((match = codeBlockRegex.exec(raw)) !== null) {
        // Partie avant le bloc de code => commenter
        const before = raw.slice(lastIndex, match.index);
        before.split('\n').forEach(line => {
            transformed += '# ' + line + '\n';
        });

        // Bloc de code => supprimer indentation commune
        const codeBlock = match[1];
        const lines = codeBlock.split('\n');
        const indentLengths = lines
            .filter(line => line.trim() !== '')
            .map(line => line.match(/^(\s*)/)[1].length);
        const minIndent = indentLengths.length > 0 ? Math.min(...indentLengths) : 0;

        lines.forEach(line => {
            transformed += line.slice(minIndent) + '\n';
        });

        lastIndex = codeBlockRegex.lastIndex;
    }

    // Partie après le dernier bloc
    const after = raw.slice(lastIndex);
    after.split('\n').forEach(line => {
        transformed += '# ' + line + '\n';
    });

    try {
        // Récupérer le jeton CSRF
        const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
        
        // Stocker le script sur le serveur
        const response = await fetch('/api/store_temp_script', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ script: transformed })
        });
        
        const data = await response.json();
        
        if (data.error) {
            console.error("Erreur lors du stockage du script:", data.error);
            return;
        }
        
        // Utiliser l'ID du script dans l'URL
        const scriptId = data.id;
        const basthonUrl = document.getElementById('basthon_console_url').textContent + "?kernel=python&scriptId=" + scriptId;
        window.open(basthonUrl, '_blank');
    } catch (error) {
        console.error("Erreur lors de la communication avec le serveur:", error);
    }
}

function downloadScript() {
    const raw = document.getElementById('resultatIA').textContent;

    let transformed = '';
    const codeBlockRegex = /```(?:python)?\n([\s\S]*?)```/g;
    let lastIndex = 0;
    let match;

    while ((match = codeBlockRegex.exec(raw)) !== null) {
        const before = raw.slice(lastIndex, match.index);
        before.split('\n').forEach(line => {
            transformed += '# ' + line + '\n';
        });

        transformed += match[1] + '\n';

        lastIndex = codeBlockRegex.lastIndex;
    }

    const after = raw.slice(lastIndex);
    after.split('\n').forEach(line => {
        transformed += '# ' + line + '\n';
    });

    const blob = new Blob([transformed], {type: "text/x-python"});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = "exercice.py";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

async function ouvrirNotebook() {
    const code = document.getElementById('resultatIA').textContent;
    const notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": code.split('\n').map(function(line) { return line + '\n'; })
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.8"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 2
    };

    try {
        // Récupérer le jeton CSRF
        const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
        
        // Stocker le notebook sur le serveur
        const response = await fetch('/api/upload_notebook', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(notebook)
        });
        
        const data = await response.json();
        
        if (data.error) {
            console.error("Erreur lors du stockage du notebook:", data.error);
            return;
        }
        
        // Utiliser l'ID du notebook dans l'URL
        const notebookId = data.id;
        const notebookLocalUrl = document.getElementById('basthon_notebook_url').textContent + "?notebookId=" + notebookId;
        window.open(notebookLocalUrl, '_blank');
    } catch (error) {
        console.error("Erreur lors de la communication avec le serveur:", error);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    chargerData();

    document.querySelectorAll('.star').forEach(star => {
        star.addEventListener('click', () => {
            selectedDifficulte = parseInt(star.dataset.value);

            document.querySelectorAll('.star').forEach(s => {
                if (parseInt(s.dataset.value) <= selectedDifficulte) {
                    s.classList.add('selected');
                } else {
                    s.classList.remove('selected');
                }
            });

            updateDescription();
        });
    });

    document.getElementById('genererBtn').addEventListener('click', genererExercice);
    document.getElementById('togglePromptBtn').addEventListener('click', togglePrompt);
    document.getElementById('toggleResultatBtn').addEventListener('click', toggleResultat);
    document.getElementById('downloadNotebookBtn').addEventListener('click', downloadNotebook);
    document.getElementById('downloadScriptBtn').addEventListener('click', downloadScript);
    document.getElementById('ouvrirConsoleBtn').addEventListener('click', ouvrirConsole);
    document.getElementById('ouvrirNotebookBtn').addEventListener('click', ouvrirNotebook);
});
