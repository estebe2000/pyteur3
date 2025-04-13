document.addEventListener('DOMContentLoaded', function() {
    // Initialisation des éditeurs CodeMirror
    const generationPromptEditor = CodeMirror.fromTextArea(document.getElementById('generationPrompt'), {
        mode: 'javascript',
        theme: 'monokai',
        lineNumbers: true,
        lineWrapping: true
    });

    const evaluationPromptEditor = CodeMirror.fromTextArea(document.getElementById('evaluationPrompt'), {
        mode: 'javascript',
        theme: 'monokai',
        lineNumbers: true,
        lineWrapping: true
    });

    // Récupération des prompts par défaut
    const defaultGenerationPrompt = document.getElementById('default_generation_prompt').textContent;
    const defaultEvaluationPrompt = document.getElementById('default_evaluation_prompt').textContent;
    const defaultHtmlFormatting = document.getElementById('default_html_formatting').textContent;

    // Initialisation des éditeurs avec les valeurs par défaut si elles sont vides
    if (!generationPromptEditor.getValue().trim()) {
        generationPromptEditor.setValue(defaultGenerationPrompt);
    }
    if (!evaluationPromptEditor.getValue().trim()) {
        evaluationPromptEditor.setValue(defaultEvaluationPrompt);
    }

    // Mise à jour des aperçus au chargement
    updateGenerationPreview();
    updateEvaluationPreview();

    // Événements pour les tags de variables
    document.querySelectorAll('.variable-tag').forEach(tag => {
        tag.addEventListener('click', function() {
            const activeTab = document.querySelector('.tab-pane.active');
            const activeEditor = activeTab.id === 'generation' ? generationPromptEditor : evaluationPromptEditor;
            
            // Insérer la variable à la position du curseur
            const cursor = activeEditor.getCursor();
            activeEditor.replaceRange(this.dataset.value, cursor);
            
            // Mettre le focus sur l'éditeur
            activeEditor.focus();
            
            // Mettre à jour l'aperçu
            if (activeTab.id === 'generation') {
                updateGenerationPreview();
            } else {
                updateEvaluationPreview();
            }
        });
    });

    // Événements pour les boutons de sauvegarde
    document.getElementById('saveGenerationPrompt').addEventListener('click', function() {
        savePrompt('generation', generationPromptEditor.getValue());
    });

    document.getElementById('saveEvaluationPrompt').addEventListener('click', function() {
        savePrompt('evaluation', evaluationPromptEditor.getValue());
    });

    // Événements pour les boutons de réinitialisation
    document.getElementById('resetGenerationPrompt').addEventListener('click', function() {
        if (confirm('Êtes-vous sûr de vouloir réinitialiser le prompt de génération ?')) {
            generationPromptEditor.setValue(defaultGenerationPrompt);
            updateGenerationPreview();
        }
    });

    document.getElementById('resetEvaluationPrompt').addEventListener('click', function() {
        if (confirm('Êtes-vous sûr de vouloir réinitialiser le prompt d\'évaluation ?')) {
            evaluationPromptEditor.setValue(defaultEvaluationPrompt);
            updateEvaluationPreview();
        }
    });

    // Événements pour les boutons de test
    document.getElementById('testGenerationPrompt').addEventListener('click', function() {
        testGenerationPrompt(generationPromptEditor.getValue());
    });

    document.getElementById('testEvaluationPrompt').addEventListener('click', function() {
        testEvaluationPrompt(evaluationPromptEditor.getValue());
    });

    // Événements pour la mise à jour des aperçus lors de la modification des prompts
    generationPromptEditor.on('change', updateGenerationPreview);
    evaluationPromptEditor.on('change', updateEvaluationPreview);

    // Fonction pour mettre à jour l'aperçu du prompt de génération
    function updateGenerationPreview() {
        const prompt = generationPromptEditor.getValue();
        const niveau = document.getElementById('testNiveau').value;
        const theme = document.getElementById('testTheme').value;
        const difficulte = document.getElementById('testDifficulte').value;
        const description = document.getElementById('testDescription').value;
        const debutant = document.getElementById('testDebutant').value === 'true';

        // Créer le niveau_python en fonction de debutant
        let niveau_python = "";
        if (debutant) {
            niveau_python = `
IMPORTANT: Cet exercice est destiné à des débutants en Python. 
N'utilise PAS de fonctions, de classes, d'objets ou d'autres concepts avancés dans le squelette de code.
Utilise uniquement des variables, des opérations de base, des conditions (if/else) et des boucles (for/while).
Le code doit être simple et direct, sans abstractions avancées.
`;
        } else {
            niveau_python = `
Cet exercice peut utiliser des fonctions, des classes et d'autres concepts avancés de Python si nécessaire.
`;
        }

        // Remplacer les variables dans le prompt
        let previewText = prompt
            .replace(/\{niveau\}/g, niveau)
            .replace(/\{theme\}/g, theme)
            .replace(/\{difficulte\}/g, difficulte)
            .replace(/\{description\}/g, description)
            .replace(/\{debutant\}/g, debutant.toString())
            .replace(/\{niveau_python\}/g, niveau_python);

        document.getElementById('generationPreview').textContent = previewText;
    }

    // Fonction pour mettre à jour l'aperçu du prompt d'évaluation
    function updateEvaluationPreview() {
        const prompt = evaluationPromptEditor.getValue();
        const code = document.getElementById('testCode').value;
        const enonce = document.getElementById('testEnonce').value;

        // Remplacer les variables dans le prompt
        let previewText = prompt
            .replace(/\{code\}/g, code)
            .replace(/\{enonce\}/g, enonce)
            .replace(/\{HTML_FORMATTING_INSTRUCTIONS\}/g, defaultHtmlFormatting);

        document.getElementById('evaluationPreview').textContent = previewText;
    }

    // Fonction pour sauvegarder un prompt
    function savePrompt(type, content) {
        // Récupérer le jeton CSRF
        const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
        
        fetch('/api/save_prompt', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                type: type,
                content: content
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Prompt enregistré avec succès !');
            } else {
                alert('Erreur lors de l\'enregistrement du prompt : ' + data.error);
            }
        })
        .catch(error => {
            console.error('Erreur:', error);
            alert('Erreur lors de l\'enregistrement du prompt.');
        });
    }

    // Fonction pour tester le prompt de génération
    function testGenerationPrompt(prompt) {
        const niveau = document.getElementById('testNiveau').value;
        const theme = document.getElementById('testTheme').value;
        const difficulte = document.getElementById('testDifficulte').value;
        const description = document.getElementById('testDescription').value;
        const debutant = document.getElementById('testDebutant').value === 'true';

        // Récupérer le jeton CSRF
        const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
        
        // Afficher un message de chargement
        const generationPreview = document.getElementById('generationPreview');
        generationPreview.textContent = 'Génération en cours...';

        fetch('/api/test_prompt', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                type: 'generation',
                prompt: prompt,
                params: {
                    niveau: niveau,
                    theme: theme,
                    difficulte: parseInt(difficulte),
                    description: description,
                    debutant: debutant
                }
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Afficher la réponse dans une nouvelle fenêtre
                const newWindow = window.open('', '_blank');
                newWindow.document.write(`
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>Résultat du test</title>
                        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
                        <style>
                            body { padding: 20px; }
                            pre { white-space: pre-wrap; word-wrap: break-word; }
                            .card { margin-bottom: 20px; }
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <h1>Résultat du test de génération</h1>
                            <div class="card">
                                <div class="card-header">Prompt utilisé</div>
                                <div class="card-body">
                                    <pre>${data.prompt}</pre>
                                </div>
                            </div>
                            <div class="card">
                                <div class="card-header">Réponse de l'IA</div>
                                <div class="card-body">
                                    <div>${data.response}</div>
                                </div>
                            </div>
                        </div>
                    </body>
                    </html>
                `);
                newWindow.document.close();
                
                // Mettre à jour l'aperçu
                generationPreview.textContent = 'Test effectué avec succès. Voir la fenêtre ouverte pour les résultats.';
            } else {
                generationPreview.textContent = 'Erreur lors du test : ' + data.error;
            }
        })
        .catch(error => {
            console.error('Erreur:', error);
            generationPreview.textContent = 'Erreur lors du test.';
        });
    }

    // Fonction pour tester le prompt d'évaluation
    function testEvaluationPrompt(prompt) {
        const code = document.getElementById('testCode').value;
        const enonce = document.getElementById('testEnonce').value;

        // Récupérer le jeton CSRF
        const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
        
        // Afficher un message de chargement
        const evaluationPreview = document.getElementById('evaluationPreview');
        evaluationPreview.textContent = 'Évaluation en cours...';

        fetch('/api/test_prompt', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                type: 'evaluation',
                prompt: prompt,
                params: {
                    code: code,
                    enonce: enonce,
                    HTML_FORMATTING_INSTRUCTIONS: defaultHtmlFormatting
                }
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Afficher la réponse dans une nouvelle fenêtre
                const newWindow = window.open('', '_blank');
                newWindow.document.write(`
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>Résultat du test</title>
                        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
                        <style>
                            body { padding: 20px; }
                            pre { white-space: pre-wrap; word-wrap: break-word; }
                            .card { margin-bottom: 20px; }
                            .text-success { color: #28a745; }
                            .text-danger { color: #dc3545; }
                            .text-info { color: #17a2b8; }
                            .text-primary { color: #007bff; }
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <h1>Résultat du test d'évaluation</h1>
                            <div class="card">
                                <div class="card-header">Prompt utilisé</div>
                                <div class="card-body">
                                    <pre>${data.prompt}</pre>
                                </div>
                            </div>
                            <div class="card">
                                <div class="card-header">Réponse de l'IA</div>
                                <div class="card-body">
                                    ${data.response}
                                </div>
                            </div>
                        </div>
                    </body>
                    </html>
                `);
                newWindow.document.close();
                
                // Mettre à jour l'aperçu
                evaluationPreview.textContent = 'Test effectué avec succès. Voir la fenêtre ouverte pour les résultats.';
            } else {
                evaluationPreview.textContent = 'Erreur lors du test : ' + data.error;
            }
        })
        .catch(error => {
            console.error('Erreur:', error);
            evaluationPreview.textContent = 'Erreur lors du test.';
        });
    }

    // Événements pour la mise à jour des aperçus lors de la modification des champs de test
    document.getElementById('testNiveau').addEventListener('change', updateGenerationPreview);
    document.getElementById('testTheme').addEventListener('input', updateGenerationPreview);
    document.getElementById('testDifficulte').addEventListener('input', updateGenerationPreview);
    document.getElementById('testDescription').addEventListener('input', updateGenerationPreview);
    document.getElementById('testDebutant').addEventListener('change', updateGenerationPreview);
    document.getElementById('testCode').addEventListener('input', updateEvaluationPreview);
    document.getElementById('testEnonce').addEventListener('input', updateEvaluationPreview);
});
