document.addEventListener('DOMContentLoaded', function() {
    console.log("Document chargé, initialisation des statistiques...");
    
    // Récupérer le token CSRF s'il existe
    const csrfToken = document.querySelector('meta[name="csrf-token"]') ? 
                      document.querySelector('meta[name="csrf-token"]').getAttribute('content') : 
                      "";
    
    // ===== SECTION UTILISATEURS =====
    fetch('/api/statistics/users', {
        method: 'GET',
        headers: {
            'X-CSRF-TOKEN': csrfToken
        },
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(data => {
        console.log("Données utilisateurs:", data);
        
        // Graphique répartition par rôle
        const ctxRole = document.getElementById('chart-users-role');
        if (ctxRole) {
            new Chart(ctxRole.getContext('2d'), {
                type: 'pie',
                data: {
                    labels: data.roles.map(r => r.role),
                    datasets: [{
                        data: data.roles.map(r => r.count),
                        backgroundColor: ['#ff6384', '#36a2eb', '#ffce56', '#4bc0c0', '#9966ff']
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: { display: true, text: 'Répartition par rôle' },
                        legend: { position: 'right' }
                    }
                }
            });
        }
        
        // Graphique répartition par besoins particuliers
        const ctxSexe = document.getElementById('chart-users-sexe');
        if (ctxSexe) {
            new Chart(ctxSexe.getContext('2d'), {
                type: 'pie',
                data: {
                    labels: data.besoins.map(b => b.besoins === 'avec' ? 'Avec besoins particuliers' : 'Sans besoins particuliers'),
                    datasets: [{
                        data: data.besoins.map(b => b.count),
                        backgroundColor: ['#ff6384', '#36a2eb']
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: { display: true, text: 'Élèves avec/sans besoins particuliers' },
                        legend: { position: 'right' }
                    }
                }
            });
        }
        
        // Graphique répartition par niveau
        const ctxNiveau = document.getElementById('chart-users-niveau');
        if (ctxNiveau) {
            new Chart(ctxNiveau.getContext('2d'), {
                type: 'bar',
                data: {
                    labels: data.niveaux.map(n => n.niveau || 'Non spécifié'),
                    datasets: [{
                        label: 'Nombre d\'élèves',
                        data: data.niveaux.map(n => n.count),
                        backgroundColor: '#4bc0c0'
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: { display: true, text: 'Répartition par niveau' }
                    }
                }
            });
        }
        
        // Graphique inscriptions par mois
        const ctxInscriptions = document.getElementById('chart-users-inscriptions');
        if (ctxInscriptions) {
            new Chart(ctxInscriptions.getContext('2d'), {
                type: 'line',
                data: {
                    labels: data.inscriptions.map(i => i.mois),
                    datasets: [{
                        label: 'Nouvelles inscriptions',
                        data: data.inscriptions.map(i => i.count),
                        fill: false,
                        borderColor: '#9966ff',
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: { display: true, text: 'Inscriptions par mois' }
                    }
                }
            });
        }
        
        // Tableau des utilisateurs
        const tbodyUsers = document.querySelector('#table-users tbody');
        if (tbodyUsers) {
            tbodyUsers.innerHTML = '';
            
            data.users.forEach(user => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${user.nom}</td>
                    <td>${user.prenom}</td>
                    <td>${user.role}</td>
                    <td>${user.sexe || ''}</td>
                    <td>${user.niveau || ''}</td>
                    <td>${user.date_entree ? new Date(user.date_entree).toLocaleDateString() : ''}</td>
                    <td>${user.date_sortie ? new Date(user.date_sortie).toLocaleDateString() : ''}</td>
                `;
                tbodyUsers.appendChild(tr);
            });
            
            // Initialiser DataTable
            $('#table-users').DataTable();
        }
    })
    .catch(error => {
        console.error("Erreur lors du chargement des statistiques utilisateurs:", error);
    });

    // ===== SECTION CLASSES & GROUPES =====
    fetch('/api/statistics/classes', {
        method: 'GET',
        headers: {
            'X-CSRF-TOKEN': csrfToken
        },
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(data => {
        console.log("Données classes & groupes:", data);
        
        // Graphique des classes
        const ctxClasses = document.getElementById('chart-classes-eleves');
        if (ctxClasses) {
            new Chart(ctxClasses.getContext('2d'), {
                type: 'bar',
                data: {
                    labels: data.classes.map(c => c.nom + ' (' + c.niveau + ')'),
                    datasets: [{
                        label: 'Élèves par classe',
                        data: data.classes.map(c => c.nb_eleves),
                        backgroundColor: '#36a2eb'
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: { display: true, text: 'Nombre d\'élèves par classe' }
                    }
                }
            });
        }

        // Tableau des classes et groupes
        const tbodyClasses = document.querySelector('#table-classes tbody');
        if (tbodyClasses) {
            tbodyClasses.innerHTML = '';
            
            // Ajouter les classes
            data.classes.forEach(c => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${c.nom}</td>
                    <td></td>
                    <td>${c.nb_eleves}</td>
                `;
                tbodyClasses.appendChild(tr);
            });
            
            // Ajouter les groupes
            data.groupes.forEach(g => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${g.classe}</td>
                    <td>${g.nom}</td>
                    <td>${g.nb_eleves}</td>
                `;
                tbodyClasses.appendChild(tr);
            });
            
            // Initialiser DataTable
            $('#table-classes').DataTable();
        }
    })
    .catch(error => {
        console.error("Erreur lors du chargement des statistiques classes & groupes:", error);
    });

    // ===== SECTION EXERCICES & DOCUMENTS =====
    fetch('/api/statistics/exercices', {
        method: 'GET',
        headers: {
            'X-CSRF-TOKEN': csrfToken
        },
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(data => {
        console.log("Données exercices & documents:", data);
        
        // Graphique répartition exercices/documents
        const ctxExercices = document.getElementById('chart-exercices-documents');
        if (ctxExercices) {
            new Chart(ctxExercices.getContext('2d'), {
                type: 'pie',
                data: {
                    labels: data.repartition.map(r => r.type === 'exercise' ? 'Exercices' : 'Documents'),
                    datasets: [{
                        data: data.repartition.map(r => r.count),
                        backgroundColor: ['#ff6384', '#36a2eb']
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: { display: true, text: 'Répartition exercices/documents' },
                        legend: { position: 'right' }
                    }
                }
            });
        }
        
        // Tableau des exercices et documents
        const tbodyExercices = document.querySelector('#table-exercices tbody');
        if (tbodyExercices) {
            tbodyExercices.innerHTML = '';
            
            data.documents.forEach(doc => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${doc.nom}</td>
                    <td>${doc.type === 'exercise' ? 'Exercice' : 'Document'}</td>
                    <td>${doc.createur}</td>
                    <td>${doc.date_creation ? new Date(doc.date_creation).toLocaleDateString() : ''}</td>
                    <td>${doc.assigne_a}</td>
                `;
                tbodyExercices.appendChild(tr);
            });
            
            // Initialiser DataTable
            $('#table-exercices').DataTable();
        }
    })
    .catch(error => {
        console.error("Erreur lors du chargement des statistiques exercices & documents:", error);
    });

    // ===== SECTION MESSAGERIE =====
    fetch('/api/statistics/messages', {
        method: 'GET',
        headers: {
            'X-CSRF-TOKEN': csrfToken
        },
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(data => {
        console.log("Données messagerie:", data);
        
        // Graphique messages lus/non lus
        const ctxMessages = document.getElementById('chart-messages');
        if (ctxMessages) {
            // Préparer les données
            const lus = data.lus.find(l => l.is_read)?.count || 0;
            const nonLus = data.lus.find(l => !l.is_read)?.count || 0;
            
            new Chart(ctxMessages.getContext('2d'), {
                type: 'pie',
                data: {
                    labels: ['Messages lus', 'Messages non lus'],
                    datasets: [{
                        data: [lus, nonLus],
                        backgroundColor: ['#4bc0c0', '#ff6384']
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: { display: true, text: 'Messages lus/non lus' },
                        legend: { position: 'right' }
                    }
                }
            });
        }
        
        // Tableau des messages
        const tbodyMessages = document.querySelector('#table-messages tbody');
        if (tbodyMessages) {
            tbodyMessages.innerHTML = '';
            
            data.messages.forEach(msg => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${msg.expediteur}</td>
                    <td>${msg.destinataire}</td>
                    <td>${msg.contenu}</td>
                    <td>${msg.date ? new Date(msg.date).toLocaleDateString() : ''}</td>
                    <td>${msg.lu ? 'Oui' : 'Non'}</td>
                `;
                tbodyMessages.appendChild(tr);
            });
            
            // Initialiser DataTable
            $('#table-messages').DataTable();
        }
    })
    .catch(error => {
        console.error("Erreur lors du chargement des statistiques messagerie:", error);
    });

    // ===== SECTION TODO LISTS =====
    fetch('/api/statistics/todos', {
        method: 'GET',
        headers: {
            'X-CSRF-TOKEN': csrfToken
        },
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(data => {
        console.log("Données todo lists:", data);
        
        // Graphique tâches terminées/non terminées
        const ctxTodos = document.getElementById('chart-todos');
        if (ctxTodos) {
            // Préparer les données
            const terminees = data.taches_done.find(t => t.done)?.count || 0;
            const nonTerminees = data.taches_done.find(t => !t.done)?.count || 0;
            
            new Chart(ctxTodos.getContext('2d'), {
                type: 'pie',
                data: {
                    labels: ['Tâches terminées', 'Tâches non terminées'],
                    datasets: [{
                        data: [terminees, nonTerminees],
                        backgroundColor: ['#4bc0c0', '#ff6384']
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: { display: true, text: 'Tâches terminées/non terminées' },
                        legend: { position: 'right' }
                    }
                }
            });
        }
        
        // Tableau des tâches
        const tbodyTodos = document.querySelector('#table-todos tbody');
        if (tbodyTodos) {
            tbodyTodos.innerHTML = '';
            
            data.todos.forEach(todo => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${todo.utilisateur}</td>
                    <td>${todo.liste}</td>
                    <td>${todo.tache}</td>
                    <td>${todo.terminee ? 'Oui' : 'Non'}</td>
                `;
                tbodyTodos.appendChild(tr);
            });
            
            // Initialiser DataTable
            $('#table-todos').DataTable();
        }
    })
    .catch(error => {
        console.error("Erreur lors du chargement des statistiques todo lists:", error);
    });

    // ===== SECTION PERFORMANCES DES ÉLÈVES =====
    fetch('/api/statistics/qcm', {
        method: 'GET',
        headers: {
            'X-CSRF-TOKEN': csrfToken
        },
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(data => {
        console.log("Données QCM:", data);
        
        // Graphique des scores QCM
        const ctxScoreRanges = document.getElementById('chart-qcm-scores');
        if (ctxScoreRanges) {
            new Chart(ctxScoreRanges.getContext('2d'), {
                type: 'bar',
                data: {
                    labels: ['0-20%', '20-40%', '40-60%', '60-80%', '80-100%'],
                    datasets: [{
                        label: 'Nombre de tentatives',
                        data: data.score_ranges ? data.score_ranges.map(range => range.count) : [0, 0, 0, 0, 0],
                        backgroundColor: [
                            '#ff6384', '#ffce56', '#ffce56', '#36a2eb', '#4bc0c0'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: { display: true, text: 'Répartition des scores QCM' }
                    }
                }
            });
        }
        
        // Graphique des meilleurs élèves
        const ctxTopStudents = document.getElementById('chart-homework-scores');
        if (ctxTopStudents) {
            new Chart(ctxTopStudents.getContext('2d'), {
                type: 'bar',
                data: {
                    labels: data.top_students ? data.top_students.map(student => `${student.prenom} ${student.nom}`) : [],
                    datasets: [{
                        label: 'Score moyen (%)',
                        data: data.top_students ? data.top_students.map(student => student.avg_score) : [],
                        backgroundColor: '#4bc0c0'
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: { display: true, text: 'Top 5 des élèves (score moyen QCM)' }
                    }
                }
            });
        }
        
        // Tableau des tentatives QCM
        if ($('#table-qcm-performance').length) {
            // Détruire la table existante si elle existe déjà
            if ($.fn.DataTable.isDataTable('#table-qcm-performance')) {
                $('#table-qcm-performance').DataTable().destroy();
            }
            
            // Vider le tableau
            $('#table-qcm-performance tbody').empty();
            
            // Préparer les données pour DataTables
            const tableData = [];
            
            if (data.attempts && data.attempts.length > 0) {
                data.attempts.forEach(attempt => {
                    tableData.push([
                        attempt.student_name,
                        `QCM #${attempt.qcm_id}`,
                        `${attempt.score}%`,
                        `${attempt.correct_answers}/${attempt.total_questions}`,
                        new Date(attempt.created_at).toLocaleDateString()
                    ]);
                });
            }
            
            // Initialiser DataTable avec les données
            $('#table-qcm-performance').DataTable({
                data: tableData,
                language: {
                    url: '//cdn.datatables.net/plug-ins/1.13.4/i18n/fr-FR.json'
                }
            });
            
            // Si aucune donnée, afficher un message
            if (tableData.length === 0) {
                $('#table-qcm-performance tbody').html('<tr><td colspan="5" class="text-center">Aucune donnée disponible</td></tr>');
            }
        }
    })
    .catch(error => {
        console.error("Erreur lors du chargement des statistiques QCM:", error);
    });

    // Charger les données de performance des élèves
    fetch('/api/statistics/users', {
        method: 'GET',
        headers: {
            'X-CSRF-TOKEN': csrfToken
        },
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(data => {
        // Filtrer uniquement les élèves
        const students = data.users.filter(user => user.role === 'eleve');
        
        // Remplir le sélecteur d'élèves
        const studentSelector = document.getElementById('student-selector');
        if (studentSelector) {
            // Vider le sélecteur
            studentSelector.innerHTML = '';
            
            // Ajouter l'option par défaut
            const defaultOption = document.createElement('option');
            defaultOption.value = '';
            defaultOption.textContent = 'Choisir un élève...';
            studentSelector.appendChild(defaultOption);
            
            // Ajouter les élèves
            students.forEach(student => {
                const option = document.createElement('option');
                option.value = String(student.id || '');
                option.textContent = `${student.nom} ${student.prenom}`;
                studentSelector.appendChild(option);
            });
            
            // Ajouter un événement de changement
            studentSelector.addEventListener('change', function() {
                const studentId = this.value;
                
                if (studentId) {
                    // Afficher un message de chargement
                    document.querySelector('#table-qcm-performance tbody').innerHTML = '<tr><td colspan="5" class="text-center">Chargement des données...</td></tr>';
                    document.querySelector('#table-homework-performance tbody').innerHTML = '<tr><td colspan="7" class="text-center">Chargement des données...</td></tr>';
                    
                    // Charger l'historique QCM
                    fetch(`/api/student/qcm/history/${studentId}`, {
                        method: 'GET',
                        headers: {
                            'X-CSRF-TOKEN': csrfToken
                        },
                        credentials: 'same-origin'
                    })
                    .then(response => response.json())
                    .then(data => {
                        // Récupérer l'élève sélectionné
                        const studentName = document.getElementById('student-selector').options[document.getElementById('student-selector').selectedIndex].text;
                        
                        // Préparer les données pour DataTables
                        const tableData = [];
                        
                        if (data.results && data.results.length > 0) {
                            data.results.forEach(result => {
                                tableData.push([
                                    studentName,
                                    `QCM #${result.qcm_id}`,
                                    `${result.score}%`,
                                    `${result.correct_answers}/${result.total_questions}`,
                                    new Date(result.created_at).toLocaleDateString()
                                ]);
                            });
                        }
                        
                        // Rafraîchir DataTable
                        if ($.fn.DataTable.isDataTable('#table-qcm-performance')) {
                            $('#table-qcm-performance').DataTable().destroy();
                        }
                        
                        // Vider le tableau
                        $('#table-qcm-performance tbody').empty();
                        
                        // Initialiser DataTable avec les données
                        $('#table-qcm-performance').DataTable({
                            data: tableData,
                            language: {
                                url: '//cdn.datatables.net/plug-ins/1.13.4/i18n/fr-FR.json'
                            }
                        });
                        
                        // Si aucune donnée, afficher un message
                        if (tableData.length === 0) {
                            $('#table-qcm-performance tbody').html('<tr><td colspan="5" class="text-center">Aucune donnée de QCM disponible pour cet élève</td></tr>');
                        }
                    })
                    .catch(error => {
                        console.error("Erreur lors du chargement de l'historique QCM de l'élève:", error);
                        
                        // En cas d'erreur, afficher un message
                        const tbodyQcm = document.querySelector('#table-qcm-performance tbody');
                        if (tbodyQcm) {
                            tbodyQcm.innerHTML = `<tr><td colspan="5" class="text-center">Erreur lors du chargement des données: ${error.message}</td></tr>`;
                        }
                    });

                    // Charger l'historique devoirs
                    fetch(`/api/student/homework/history/${studentId}`, {
                        method: 'GET',
                        headers: {
                            'X-CSRF-TOKEN': csrfToken
                        },
                        credentials: 'same-origin'
                    })
                    .then(response => response.json())
                    .then(data => {
                        // Récupérer l'élève sélectionné
                        const studentName = document.getElementById('student-selector').options[document.getElementById('student-selector').selectedIndex].text;
                        
                        // Remplir le tableau devoirs
                        const tbodyHomework = document.querySelector('#table-homework-performance tbody');
                        if (tbodyHomework) {
                            tbodyHomework.innerHTML = '';
                            
                            if (data.results && data.results.length > 0) {
                                data.results.forEach(result => {
                                    const tr = document.createElement('tr');
                                    tr.innerHTML = `
                                        <td>${studentName}</td>
                                        <td>${result.title}</td>
                                        <td>${result.subject || 'Non spécifiée'}</td>
                                        <td>${result.score !== null ? result.score + '%' : 'Non noté'}</td>
                                        <td>${result.status}</td>
                                        <td>${result.due_date ? new Date(result.due_date).toLocaleDateString() : 'Non spécifiée'}</td>
                                        <td>${result.completed_at ? new Date(result.completed_at).toLocaleDateString() : 'Non rendu'}</td>
                                    `;
                                    tbodyHomework.appendChild(tr);
                                });
                            } else {
                                const tr = document.createElement('tr');
                                tr.innerHTML = `<td colspan="7" class="text-center">Aucun devoir disponible pour cet élève</td>`;
                                tbodyHomework.appendChild(tr);
                            }
                            
                            // Rafraîchir DataTable
                            if ($.fn.DataTable.isDataTable('#table-homework-performance')) {
                                $('#table-homework-performance').DataTable().destroy();
                            }
                            $('#table-homework-performance').DataTable();
                        }
                    })
                    .catch(error => {
                        console.error("Erreur lors du chargement de l'historique des devoirs de l'élève:", error);
                        
                        // En cas d'erreur, afficher un message
                        const tbodyHomework = document.querySelector('#table-homework-performance tbody');
                        if (tbodyHomework) {
                            tbodyHomework.innerHTML = `<tr><td colspan="7" class="text-center">Erreur lors du chargement des données: ${error.message}</td></tr>`;
                        }
                    });
                } else {
                    // Réinitialiser les tableaux
                    document.querySelector('#table-qcm-performance tbody').innerHTML = '<tr><td colspan="5" class="text-center">Sélectionnez un élève pour afficher ses résultats</td></tr>';
                    document.querySelector('#table-homework-performance tbody').innerHTML = '<tr><td colspan="7" class="text-center">Sélectionnez un élève pour afficher ses résultats</td></tr>';
                }
            });
        }
    })
    .catch(error => {
        console.error("Erreur lors du chargement des utilisateurs:", error);
    });

    // Fonction pour exporter un tableau en CSV
    function exportTableToCSV(tableId, filename) {
        const table = $('#' + tableId).DataTable();
        let csv = '';
        
        // En-têtes
        const headers = [];
        $('#' + tableId + ' thead th').each(function() {
            let data = $(this).text().replace(/"/g, '""');
            headers.push('"' + data + '"');
        });
        csv += headers.join(';') + '\n';
        
        // Données
        table.rows({ search: 'applied' }).every(function() {
            const row = this.data();
            const rowData = [];
            for (let i = 0; i < row.length; i++) {
                let data = row[i].toString().replace(/"/g, '""');
                rowData.push('"' + data + '"');
            }
            csv += rowData.join(';') + '\n';
        });
        
        // Télécharger
        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.setAttribute('href', url);
        link.setAttribute('download', filename);
        link.style.display = 'none';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
    
    // Associer export à chaque bouton
    document.getElementById('export-users-csv').onclick = () => exportTableToCSV('table-users', 'utilisateurs.csv');
    document.getElementById('export-classes-csv').onclick = () => exportTableToCSV('table-classes', 'classes_groupes.csv');
    document.getElementById('export-exercices-csv').onclick = () => exportTableToCSV('table-exercices', 'exercices_documents.csv');
    document.getElementById('export-messages-csv').onclick = () => exportTableToCSV('table-messages', 'messagerie.csv');
    document.getElementById('export-todos-csv').onclick = () => exportTableToCSV('table-todos', 'todos.csv');
    document.getElementById('export-performances-csv').onclick = () => exportTableToCSV('table-qcm-performance', 'performances_eleves.csv');

    // Accordéons
    document.querySelectorAll('.toggle-section').forEach(btn => {
        btn.addEventListener('click', () => {
            const content = btn.closest('.stats-section').querySelector('.section-content');
            content.classList.toggle('collapsed');
            btn.textContent = content.classList.contains('collapsed') ? 'Agrandir' : 'Réduire';
        });
    });
});
