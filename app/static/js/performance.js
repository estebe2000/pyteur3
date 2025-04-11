document.addEventListener('DOMContentLoaded', function() {
    // Charger les statistiques QCM
    fetch(`/api/student/qcm/stats/${window.current_user_id}`, {
        method: 'GET'
    })
    .then(response => response.json())
    .then(data => {
        console.log("Données API QCM stats:", data);
        
        // Mettre à jour les statistiques globales
        document.getElementById('qcm-avg-score').textContent = data.global.avg_score.toFixed(1) + '%';
        document.getElementById('qcm-total-attempts').textContent = data.global.total_attempts;
        
        // Créer le graphique d'évolution
        const ctxQcmEvolution = document.getElementById('qcm-evolution-chart').getContext('2d');
        new Chart(ctxQcmEvolution, {
            type: 'line',
            data: {
                labels: data.time_evolution.map(item => item.date),
                datasets: [{
                    label: 'Score moyen (%)',
                    data: data.time_evolution.map(item => item.avg_score),
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
    })
    .catch(error => {
        console.error("Erreur lors du chargement des statistiques QCM:", error);
        document.getElementById('qcm-avg-score').textContent = 'N/A';
        document.getElementById('qcm-total-attempts').textContent = '0';
    });

    // Charger les statistiques devoirs
    fetch(`/api/student/homework/stats/${window.current_user_id}`, {
        method: 'GET'
    })
    .then(response => response.json())
    .then(data => {
        console.log("Données API homework stats:", data);
        
        // Mettre à jour les statistiques globales
        document.getElementById('homework-avg-score').textContent = data.global.avg_score.toFixed(1) + '%';
        document.getElementById('homework-completed').textContent = data.global.total_completed;
        document.getElementById('homework-late').textContent = data.global.total_late;
        
        // Créer le graphique d'évolution
        const ctxHomeworkEvolution = document.getElementById('homework-evolution-chart').getContext('2d');
        new Chart(ctxHomeworkEvolution, {
            type: 'line',
            data: {
                labels: data.time_evolution.map(item => item.date),
                datasets: [{
                    label: 'Score moyen (%)',
                    data: data.time_evolution.map(item => item.avg_score),
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
    })
    .catch(error => {
        console.error("Erreur lors du chargement des statistiques devoirs:", error);
        document.getElementById('homework-avg-score').textContent = 'N/A';
        document.getElementById('homework-completed').textContent = '0';
        document.getElementById('homework-late').textContent = '0';
    });

    // Charger l'historique QCM
    fetch(`/api/student/qcm/history/${current_user_id}`, {
        method: 'GET'
    })
    .then(response => response.json())
    .then(data => {
        console.log("Données API QCM history:", data);
        
        // Remplir le tableau QCM
        const tbodyQcm = document.querySelector('#qcm-history-table');
        tbodyQcm.innerHTML = '';
        
        if (data.results.length === 0) {
            tbodyQcm.innerHTML = `<tr><td colspan="5" class="px-4 py-4 text-center text-gray-400">Aucun résultat de QCM disponible</td></tr>`;
        } else {
            data.results.forEach(result => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td class="px-4 py-2">QCM #${result.qcm_id}</td>
                    <td class="px-4 py-2">${result.score}%</td>
                    <td class="px-4 py-2">${result.correct_answers}/${result.total_questions}</td>
                    <td class="px-4 py-2">${new Date(result.created_at).toLocaleDateString()}</td>
                    <td class="px-4 py-2">
                        <button class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-1 px-2 rounded text-xs">
                            Revoir
                        </button>
                    </td>
                `;
                tbodyQcm.appendChild(tr);
            });
        }
    })
    .catch(error => {
        console.error("Erreur lors du chargement de l'historique QCM:", error);
        const tbodyQcm = document.querySelector('#qcm-history-table');
        tbodyQcm.innerHTML = `<tr><td colspan="5" class="px-4 py-4 text-center text-gray-400">Erreur lors du chargement des données</td></tr>`;
    });

    // Charger l'historique devoirs
    fetch(`/api/student/homework/history/${current_user_id}`, {
        method: 'GET'
    })
    .then(response => response.json())
    .then(data => {
        console.log("Données API homework history:", data);
        
        // Remplir le tableau devoirs
        const tbodyHomework = document.querySelector('#homework-history-table');
        tbodyHomework.innerHTML = '';
        
        if (data.results.length === 0) {
            tbodyHomework.innerHTML = `<tr><td colspan="5" class="px-4 py-4 text-center text-gray-400">Aucun devoir disponible</td></tr>`;
        } else {
            data.results.forEach(result => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td class="px-4 py-2">${result.title}</td>
                    <td class="px-4 py-2">${result.subject || 'Non spécifiée'}</td>
                    <td class="px-4 py-2">${result.due_date ? new Date(result.due_date).toLocaleDateString() : 'Non spécifiée'}</td>
                    <td class="px-4 py-2">${result.status}</td>
                    <td class="px-4 py-2">${result.score !== null ? result.score + '%' : 'Non noté'}</td>
                `;
                tbodyHomework.appendChild(tr);
            });
        }
    })
    .catch(error => {
        console.error("Erreur lors du chargement de l'historique devoirs:", error);
        const tbodyHomework = document.querySelector('#homework-history-table');
        tbodyHomework.innerHTML = `<tr><td colspan="5" class="px-4 py-4 text-center text-gray-400">Erreur lors du chargement des données</td></tr>`;
    });

    // Charger les recommandations
    fetch(`/api/student/recommendations/${current_user_id}`, {
        method: 'GET'
    })
    .then(response => response.json())
    .then(data => {
        console.log("Données API recommendations:", data);
        
        // Remplir les recommandations prioritaires
        const priorityRecommendations = document.getElementById('priority-recommendations');
        priorityRecommendations.innerHTML = '';
        
        // Filtrer les recommandations par priorité (4 et 3 sont prioritaires)
        const highPriorityRecs = data.results.filter(rec => rec.priority >= 3);
        
        if (highPriorityRecs.length === 0) {
            priorityRecommendations.innerHTML = `<div class="flex items-center justify-center h-20 text-gray-400"><p>Aucune recommandation prioritaire</p></div>`;
        } else {
            highPriorityRecs.forEach(rec => {
                const div = document.createElement('div');
                div.className = 'bg-yellow-50 border-l-4 border-yellow-400 p-4';
                div.innerHTML = `
                    <div class="flex justify-between">
                        <p class="text-yellow-700">${rec.reason}</p>
                        <button onclick="markRecommendationCompleted(${rec.id})" class="text-sm text-blue-500 hover:text-blue-700">Marquer comme fait</button>
                    </div>
                `;
                priorityRecommendations.appendChild(div);
            });
        }
        
        // Remplir les recommandations QCM
        const qcmRecommendations = document.getElementById('qcm-recommendations');
        qcmRecommendations.innerHTML = '';
        
        const qcmRecs = data.results.filter(rec => rec.recommendation_type === 'qcm');
        
        if (qcmRecs.length === 0) {
            qcmRecommendations.innerHTML = `<div class="flex items-center justify-center h-20 text-gray-400"><p>Aucune recommandation de QCM</p></div>`;
        } else {
            qcmRecs.forEach(rec => {
                const div = document.createElement('div');
                div.className = 'bg-blue-50 border-l-4 border-blue-400 p-4';
                div.innerHTML = `
                    <div class="flex justify-between">
                        <p class="text-blue-700">${rec.reason}</p>
                        <button onclick="markRecommendationCompleted(${rec.id})" class="text-sm text-blue-500 hover:text-blue-700">Marquer comme fait</button>
                    </div>
                `;
                qcmRecommendations.appendChild(div);
            });
        }
        
        // Remplir les recommandations ressources
        const resourceRecommendations = document.getElementById('resource-recommendations');
        resourceRecommendations.innerHTML = '';
        
        const resourceRecs = data.results.filter(rec => rec.recommendation_type === 'resource' || rec.recommendation_type === 'exercise');
        
        if (resourceRecs.length === 0) {
            resourceRecommendations.innerHTML = `<div class="flex items-center justify-center h-20 text-gray-400"><p>Aucune recommandation de ressource</p></div>`;
        } else {
            resourceRecs.forEach(rec => {
                const div = document.createElement('div');
                div.className = 'bg-green-50 border-l-4 border-green-400 p-4';
                div.innerHTML = `
                    <div class="flex justify-between">
                        <p class="text-green-700">${rec.reason}</p>
                        <button onclick="markRecommendationCompleted(${rec.id})" class="text-sm text-green-500 hover:text-green-700">Marquer comme fait</button>
                    </div>
                `;
                resourceRecommendations.appendChild(div);
            });
        }
    })
    .catch(error => {
        console.error("Erreur lors du chargement des recommandations:", error);
        document.getElementById('priority-recommendations').innerHTML = `<div class="flex items-center justify-center h-20 text-gray-400"><p>Erreur lors du chargement des recommandations</p></div>`;
        document.getElementById('qcm-recommendations').innerHTML = `<div class="flex items-center justify-center h-20 text-gray-400"><p>Erreur lors du chargement des recommandations</p></div>`;
        document.getElementById('resource-recommendations').innerHTML = `<div class="flex items-center justify-center h-20 text-gray-400"><p>Erreur lors du chargement des recommandations</p></div>`;
    });

    // Fonction pour marquer une recommandation comme complétée
    window.markRecommendationCompleted = function(recommendationId) {
        fetch(`/api/student/recommendations/mark_completed/${recommendationId}`, {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Recharger les recommandations
                fetch(`/api/student/recommendations/${current_user_id}`, {
                    method: 'GET'
                })
                .then(response => response.json())
                .then(data => {
                    // Mettre à jour les recommandations (code similaire à celui ci-dessus)
                    // ...
                });
            }
        })
        .catch(error => {
            console.error("Erreur lors du marquage de la recommandation:", error);
        });
    };
});
