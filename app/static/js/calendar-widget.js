// Widget Calendrier
class CalendarWidget extends Widget {
  constructor() {
    super('calendar', 'Calendrier');
    this.currentDate = new Date();
    this.events = [];
    this.selectedDate = null;
  }
  
  init() {
    super.init();
    
    // Créer la structure du widget
    const content = document.createElement('div');
    content.className = 'widget-content';
    content.innerHTML = `
      <div class="calendar-container">
        <div class="calendar-header">
          <div class="calendar-title"></div>
          <div class="calendar-nav">
            <button class="calendar-nav-btn calendar-prev-month"><i class="fas fa-chevron-left"></i></button>
            <button class="calendar-nav-btn calendar-next-month"><i class="fas fa-chevron-right"></i></button>
          </div>
        </div>
        <div class="calendar-grid">
          <div class="calendar-day-name">Lun</div>
          <div class="calendar-day-name">Mar</div>
          <div class="calendar-day-name">Mer</div>
          <div class="calendar-day-name">Jeu</div>
          <div class="calendar-day-name">Ven</div>
          <div class="calendar-day-name">Sam</div>
          <div class="calendar-day-name">Dim</div>
          <!-- Les jours seront générés dynamiquement -->
        </div>
        <div class="calendar-events">
          <!-- Les événements seront générés dynamiquement -->
        </div>
      </div>
    `;
    
    this.element.appendChild(content);
    
    // Ajouter les événements
    const prevMonthBtn = this.element.querySelector('.calendar-prev-month');
    const nextMonthBtn = this.element.querySelector('.calendar-next-month');
    
    prevMonthBtn.addEventListener('click', () => {
      this.currentDate.setMonth(this.currentDate.getMonth() - 1);
      this.renderCalendar();
    });
    
    nextMonthBtn.addEventListener('click', () => {
      this.currentDate.setMonth(this.currentDate.getMonth() + 1);
      this.renderCalendar();
    });
    
    // Charger les événements (simulés pour l'exemple)
    this.loadEvents();
  }
  
  render() {
    super.render();
    this.renderCalendar();
  }
  
  renderCalendar() {
    // Mettre à jour le titre du calendrier
    const titleEl = this.element.querySelector('.calendar-title');
    const monthNames = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'];
    titleEl.textContent = `${monthNames[this.currentDate.getMonth()]} ${this.currentDate.getFullYear()}`;
    
    // Générer les jours du calendrier
    const gridEl = this.element.querySelector('.calendar-grid');
    
    // Supprimer les jours existants
    const existingDays = gridEl.querySelectorAll('.calendar-day:not(.calendar-day-name)');
    existingDays.forEach(day => day.remove());
    
    // Obtenir le premier jour du mois
    const firstDay = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth(), 1);
    // Obtenir le dernier jour du mois
    const lastDay = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth() + 1, 0);
    
    // Obtenir le jour de la semaine du premier jour (0 = dimanche, 1 = lundi, etc.)
    let firstDayOfWeek = firstDay.getDay();
    // Convertir pour que lundi soit le premier jour (0 = lundi, 6 = dimanche)
    firstDayOfWeek = firstDayOfWeek === 0 ? 6 : firstDayOfWeek - 1;
    
    // Ajouter les jours du mois précédent
    const prevMonth = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth(), 0);
    for (let i = firstDayOfWeek - 1; i >= 0; i--) {
      const day = document.createElement('div');
      day.className = 'calendar-day other-month';
      day.textContent = prevMonth.getDate() - i;
      gridEl.appendChild(day);
    }
    
    // Ajouter les jours du mois actuel
    const today = new Date();
    for (let i = 1; i <= lastDay.getDate(); i++) {
      const day = document.createElement('div');
      day.className = 'calendar-day';
      day.textContent = i;
      
      // Vérifier si c'est aujourd'hui
      if (
        today.getDate() === i &&
        today.getMonth() === this.currentDate.getMonth() &&
        today.getFullYear() === this.currentDate.getFullYear()
      ) {
        day.classList.add('today');
      }
      
      // Vérifier si ce jour a des événements
      const hasEvents = this.events.some(event => {
        const eventDate = new Date(event.date);
        return (
          eventDate.getDate() === i &&
          eventDate.getMonth() === this.currentDate.getMonth() &&
          eventDate.getFullYear() === this.currentDate.getFullYear()
        );
      });
      
      if (hasEvents) {
        day.classList.add('has-event');
      }
      
      // Ajouter l'événement de clic
      day.addEventListener('click', () => {
        // Désélectionner le jour précédemment sélectionné
        const selectedDay = gridEl.querySelector('.calendar-day.selected');
        if (selectedDay) {
          selectedDay.classList.remove('selected');
        }
        
        // Sélectionner le nouveau jour
        day.classList.add('selected');
        
        // Mettre à jour la date sélectionnée
        this.selectedDate = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth(), i);
        
        // Afficher les événements pour ce jour
        this.renderEvents();
      });
      
      gridEl.appendChild(day);
    }
    
    // Ajouter les jours du mois suivant pour compléter la grille
    const daysAdded = firstDayOfWeek + lastDay.getDate();
    const remainingDays = 7 - (daysAdded % 7);
    if (remainingDays < 7) {
      for (let i = 1; i <= remainingDays; i++) {
        const day = document.createElement('div');
        day.className = 'calendar-day other-month';
        day.textContent = i;
        gridEl.appendChild(day);
      }
    }
    
    // Afficher les événements pour la date sélectionnée
    this.renderEvents();
  }
  
  loadEvents() {
    // Simuler des événements pour l'exemple
    const now = new Date();
    const year = now.getFullYear();
    const month = now.getMonth();
    
    this.events = [
      {
        id: 1,
        title: 'Devoir de mathématiques',
        date: new Date(year, month, 5),
        time: '14:00',
        color: '#4f46e5'
      },
      {
        id: 2,
        title: 'Contrôle de physique',
        date: new Date(year, month, 12),
        time: '10:00',
        color: '#ef4444'
      },
      {
        id: 3,
        title: 'Projet NSI à rendre',
        date: new Date(year, month, 20),
        time: '16:30',
        color: '#10b981'
      },
      {
        id: 4,
        title: 'Sortie scolaire',
        date: new Date(year, month, 25),
        time: '08:30',
        color: '#f59e0b'
      }
    ];
    
    // Sélectionner la date du jour par défaut
    this.selectedDate = new Date(year, month, now.getDate());
  }
  
  renderEvents() {
    const eventsContainer = this.element.querySelector('.calendar-events');
    eventsContainer.innerHTML = '';
    
    if (!this.selectedDate) return;
    
    // Filtrer les événements pour la date sélectionnée
    const dayEvents = this.events.filter(event => {
      const eventDate = new Date(event.date);
      return (
        eventDate.getDate() === this.selectedDate.getDate() &&
        eventDate.getMonth() === this.selectedDate.getMonth() &&
        eventDate.getFullYear() === this.selectedDate.getFullYear()
      );
    });
    
    // Afficher les événements
    if (dayEvents.length === 0) {
      const noEvents = document.createElement('div');
      noEvents.className = 'calendar-no-events';
      noEvents.textContent = 'Aucun événement pour cette date';
      eventsContainer.appendChild(noEvents);
    } else {
      dayEvents.forEach(event => {
        const eventEl = document.createElement('div');
        eventEl.className = 'calendar-event';
        eventEl.innerHTML = `
          <div class="calendar-event-dot" style="background-color: ${event.color}"></div>
          <div class="calendar-event-content">
            <span class="calendar-event-time">${event.time}</span>
            ${event.title}
          </div>
        `;
        eventsContainer.appendChild(eventEl);
      });
    }
  }
  
  destroy() {
    super.destroy();
  }
}

// Enregistrer le widget de calendrier
document.addEventListener('DOMContentLoaded', () => {
  // Attendre que le gestionnaire de widgets soit initialisé
  const checkWidgetManager = setInterval(() => {
    if (window.widgetManager) {
      clearInterval(checkWidgetManager);
      
      // Enregistrer le widget calendrier
      window.widgetManager.registerWidget('calendar', CalendarWidget);
      console.log('Widget calendrier enregistré');
    }
  }, 100);
});
