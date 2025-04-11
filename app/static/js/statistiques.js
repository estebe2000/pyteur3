document.addEventListener('DOMContentLoaded', function() {
    const csrfToken = "{{ csrf_token() }}";

    // Charger stats Classes & Groupes
    fetch('/api/statistics/classes', {
        method: 'GET',
        headers: {
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log("Données API /api/statistics/classes :", data);

        const ctxClasses = document.getElementById('chart-classes-eleves').getContext('2d');
        new Chart(ctxClasses, {
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


        const tbodyClasses = document.querySelector('#table-classes tbody');
        tbodyClasses.innerHTML = '';

        data.classes.forEach(c => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${c.nom}</td>
                <td></td>
                <td>${c.nb_eleves}</td>
            `;
            tbodyClasses.appendChild(tr);
});

// Fonction export CSV
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

  // Toutes les données, même non visibles
  table.rows({ search: 'applied' }).every(function() {
    const row = this.data();
    const rowData = [];
    for (let i = 0; i < row.length; i++) {
      let data = row[i].toString().replace(/"/g, '""');
      rowData.push('"' + data + '"');
    }
    csv += rowData.join(';') + '\n';
  });

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

        data.groupes.forEach(g => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${g.classe}</td>
                <td>${g.nom}</td>
                <td>${g.nb_eleves}</td>
            `;
            tbodyClasses.appendChild(tr);
        });

        $('#table-classes').DataTable();
    });

    // Charger stats Exercices & Documents
    fetch('/api/statistics/exercices', {
        method: 'GET',
        headers: {
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log("Données API /api/statistics/exercices :", data);

        const ctxExercices = document.getElementById('chart-exercices-documents').getContext('2d');
        new Chart(ctxExercices, {
            type: 'pie',
            data: {
                labels: data.repartition.map(r => r.type),
                datasets: [{
                    data: data.repartition.map(r => r.count),
                    backgroundColor: ['#36a2eb', '#ff6384']
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'bottom' },
                    title: { display: true, text: 'Répartition Exercices / Documents' }
                }
            }
        });

        const tbodyExercices = document.querySelector('#table-exercices tbody');
        tbodyExercices.innerHTML = '';

        data.documents.forEach(d => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${d.nom}</td>
                <td>${d.type}</td>
                <td>${d.createur}</td>
                <td>${d.date_creation}</td>
                <td>${d.assigne_a}</td>
            `;
            tbodyExercices.appendChild(tr);
        });

        $('#table-exercices').DataTable();
    });

    // Charger stats Messagerie
    fetch('/api/statistics/messages', {
        method: 'GET',
        headers: {
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log("Données API /api/statistics/messages :", data);

        const ctxMessages = document.getElementById('chart-messages').getContext('2d');
        new Chart(ctxMessages, {
            type: 'pie',
            data: {
                labels: data.lus.map(l => l.is_read ? 'Lu' : 'Non lu'),
                datasets: [{
                    data: data.lus.map(l => l.count),
                    backgroundColor: ['#36a2eb', '#ff6384']
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'bottom' },
                    title: { display: true, text: 'Messages lus / non lus' }
                }
            }
        });

        const tbodyMessages = document.querySelector('#table-messages tbody');
        tbodyMessages.innerHTML = '';

        data.messages.forEach(m => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${m.expediteur}</td>
                <td>${m.destinataire}</td>
                <td>${m.contenu}</td>
                <td>${m.date}</td>
                <td>${m.lu ? 'Oui' : 'Non'}</td>
            `;
            tbodyMessages.appendChild(tr);
        });

        $('#table-messages').DataTable();
    });

    // Charger stats ToDo Lists
    fetch('/api/statistics/todos', {
        method: 'GET',
        headers: {
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log("Données API /api/statistics/todos :", data);

        const ctxTodos = document.getElementById('chart-todos').getContext('2d');
        new Chart(ctxTodos, {
            type: 'pie',
            data: {
                labels: data.taches_done.map(t => t.done ? 'Terminée' : 'Non terminée'),
                datasets: [{
                    data: data.taches_done.map(t => t.count),
                    backgroundColor: ['#36a2eb', '#ff6384']
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'bottom' },
                    title: { display: true, text: 'Tâches terminées / non terminées' }
                }
            }
        });

        const tbodyTodos = document.querySelector('#table-todos tbody');
        tbodyTodos.innerHTML = '';

        data.todos.forEach(t => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${t.utilisateur}</td>
                <td>${t.liste}</td>
                <td>${t.tache}</td>
                <td>${t.terminee ? 'Oui' : 'Non'}</td>
            `;
            tbodyTodos.appendChild(tr);
        });

        $('#table-todos').DataTable();
    });

    // Charger stats utilisateurs
    fetch('/api/statistics/users', {
        method: 'GET',
        headers: {
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log("Données API /api/statistics/users :", data);

        const tbody = document.querySelector('#table-users tbody');
        tbody.innerHTML = '';
        if(data.users){
            data.users.forEach(u => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${u.nom}</td>
                    <td>${u.prenom}</td>
                    <td>${u.role}</td>
                    <td>${u.sexe}</td>
                    <td>${u.niveau}</td>
                    <td>${u.date_entree || ''}</td>
                    <td>${u.date_sortie || ''}</td>
                `;
                tbody.appendChild(tr);
            });
        }
        $('#table-users').DataTable();

        const ctxRole = document.getElementById('chart-users-role').getContext('2d');
        new Chart(ctxRole, {
            type: 'pie',
            data: {
                labels: data.roles.map(r => r.role),
                datasets: [{
                    data: data.roles.map(r => r.count),
                    backgroundColor: ['#36a2eb', '#ff6384', '#ffce56', '#4bc0c0']
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'bottom' },
                    title: { display: true, text: 'Répartition par rôle' }
                }
            }
        });

        const ctxSexe = document.getElementById('chart-users-sexe').getContext('2d');
        new Chart(ctxSexe, {
            type: 'pie',
            data: {
                labels: data.sexes.map(s => s.sexe || 'Non renseigné'),
                datasets: [{
                    data: data.sexes.map(s => s.count),
                    backgroundColor: ['#36a2eb', '#ff6384', '#ffce56']
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'bottom' },
                    title: { display: true, text: 'Répartition par sexe' }
                }
            }
        });

        const ctxNiveau = document.getElementById('chart-users-niveau').getContext('2d');
        new Chart(ctxNiveau, {
            type: 'bar',
            data: {
                labels: data.niveaux.map(n => n.niveau),
                datasets: [{
                    label: 'Nombre d\'élèves',
                    data: data.niveaux.map(n => n.count),
                    backgroundColor: '#36a2eb'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: { display: true, text: 'Répartition par niveau scolaire' }
                }
            }
        });

        const ctxInscriptions = document.getElementById('chart-users-inscriptions').getContext('2d');
        new Chart(ctxInscriptions, {
            type: 'line',
            data: {
                labels: data.inscriptions.map(i => i.mois),
                datasets: [{
                    label: 'Inscriptions',
                    data: data.inscriptions.map(i => i.count),
                    fill: false,
                    borderColor: '#4bc0c0',
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
    });

    // Charger les données de performance des élèves
    // 1. Récupérer la liste des élèves pour le sélecteur
    fetch('/api/statistics/users', {
        method: 'GET',
        headers: {
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => response.json())
    .then(data => {
        // Filtrer uniquement les élèves
        const students = data.users.filter(user => user.role === 'eleve');
        
        // Remplir le sélecteur d'élèves
        const studentSelector = document.getElementById('student-selector');
        students.forEach(student => {
            const option = document.createElement('option');
            option.value = student.id;
            option.textContent = `${student.nom} ${student.prenom}`;
            studentSelector.appendChild(option);
        });

        // Initialiser les graphiques de performance avec des données vides
        initPerformanceCharts();
        
        // Ajouter un événement de changement au sélecteur d'élèves
        studentSelector.addEventListener('change', function() {
            const studentId = this.value;
            if (studentId) {
                loadStudentPerformance(studentId);
            } else {
                // Réinitialiser les graphiques si aucun élève n'est sélectionné
                initPerformanceCharts();
                clearPerformanceTables();
            }
        });
    });

    // Fonction pour initialiser les graphiques de performance
    function initPerformanceCharts() {
        // Graphique des scores QCM
        const ctxQcmScores = document.getElementById('chart-qcm-scores').getContext('2d');
        if (window.qcmScoresChart) {
            window.qcmScoresChart.destroy();
        }
        window.qcmScoresChart = new Chart(ctxQcmScores, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Score moyen QCM (%)',
                    data: [],
                    fill: false,
                    borderColor: '#4bc0c0',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: { display: true, text: 'Évolution des scores QCM' }
                }
            }
        });

        // Graphique des scores devoirs
        const ctxHomeworkScores = document.getElementById('chart-homework-scores').getContext('2d');
        if (window.homeworkScoresChart) {
            window.homeworkScoresChart.destroy();
        }
        window.homeworkScoresChart = new Chart(ctxHomeworkScores, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Score moyen devoirs (%)',
                    data: [],
                    fill: false,
                    borderColor: '#ff6384',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: { display: true, text: 'Évolution des scores devoirs' }
                }
            }
        });
    }

    // Fonction pour vider les tableaux de performance
    function clearPerformanceTables() {
        document.querySelector('#table-qcm-performance tbody').innerHTML = '';
        document.querySelector('#table-homework-performance tbody').innerHTML = '';
        
        // Initialiser les DataTables si ce n'est pas déjà fait
        if (!$.fn.DataTable.isDataTable('#table-qcm-performance')) {
            $('#table-qcm-performance').DataTable();
        } else {
            $('#table-qcm-performance').DataTable().clear().draw();
        }
        
        if (!$.fn.DataTable.isDataTable('#table-homework-performance')) {
            $('#table-homework-performance').DataTable();
        } else {
            $('#table-homework-performance').DataTable().clear().draw();
        }
    }

    // Fonction pour charger les données de performance d'un élève
    function loadStudentPerformance(studentId) {
        // Charger les statistiques QCM
        fetch(`/api/student/qcm/stats/${studentId}`, {
            method: 'GET',
            headers: {
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => response.json())
        .then(data => {
            console.log("Données API QCM stats:", data);
            
            // Mettre à jour le graphique d'évolution QCM
            if (window.qcmScoresChart) {
                window.qcmScoresChart.data.labels = data.time_evolution.map(item => item.date);
                window.qcmScoresChart.data.datasets[0].data = data.time_evolution.map(item => item.avg_score);
                window.qcmScoresChart.update();
            }
        });

        // Charger l'historique QCM
        fetch(`/api/student/qcm/history/${studentId}`, {
            method: 'GET',
            headers: {
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => response.json())
        .then(data => {
            console.log("Données API QCM history:", data);
            
            // Récupérer l'élève sélectionné
            const studentName = document.getElementById('student-selector').options[document.getElementById('student-selector').selectedIndex].text;
            
            // Remplir le tableau QCM
            const tbodyQcm = document.querySelector('#table-qcm-performance tbody');
            tbodyQcm.innerHTML = '';
            
            data.results.forEach(result => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${studentName}</td>
                    <td>QCM #${result.qcm_id}</td>
                    <td>${result.score}%</td>
                    <td>${result.correct_answers}/${result.total_questions}</td>
                    <td>${new Date(result.created_at).toLocaleDateString()}</td>
                `;
                tbodyQcm.appendChild(tr);
            });
            
            // Rafraîchir DataTable
            if ($.fn.DataTable.isDataTable('#table-qcm-performance')) {
                $('#table-qcm-performance').DataTable().destroy();
            }
            $('#table-qcm-performance').DataTable();
        });

        // Charger les statistiques devoirs
        fetch(`/api/student/homework/stats/${studentId}`, {
            method: 'GET',
            headers: {
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => response.json())
        .then(data => {
            console.log("Données API homework stats:", data);
            
            // Mettre à jour le graphique d'évolution devoirs
            if (window.homeworkScoresChart) {
                window.homeworkScoresChart.data.labels = data.time_evolution.map(item => item.date);
                window.homeworkScoresChart.data.datasets[0].data = data.time_evolution.map(item => item.avg_score);
                window.homeworkScoresChart.update();
            }
        });

        // Charger l'historique devoirs
        fetch(`/api/student/homework/history/${studentId}`, {
            method: 'GET',
            headers: {
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => response.json())
        .then(data => {
            console.log("Données API homework history:", data);
            
            // Récupérer l'élève sélectionné
            const studentName = document.getElementById('student-selector').options[document.getElementById('student-selector').selectedIndex].text;
            
            // Remplir le tableau devoirs
            const tbodyHomework = document.querySelector('#table-homework-performance tbody');
            tbodyHomework.innerHTML = '';
            
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
            
            // Rafraîchir DataTable
            if ($.fn.DataTable.isDataTable('#table-homework-performance')) {
                $('#table-homework-performance').DataTable().destroy();
            }
            $('#table-homework-performance').DataTable();
        });
    }
});
