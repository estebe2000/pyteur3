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
});
