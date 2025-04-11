/**
 * Système de gestion de widgets pour PYTEUR OS
 * Ce fichier contient les classes et fonctions nécessaires pour gérer les widgets sur le bureau
 */

// Gestionnaire de widgets
class WidgetManager {
  constructor() {
    this.widgets = {}; // Classes de widgets disponibles
    this.activeWidgets = []; // Instances de widgets actifs
    this.config = {
      activeWidgets: [],
      positions: {},
      settings: {}
    };
    this.isInitialized = false;
  }
  
  // Charger la configuration depuis le serveur
  async loadConfig() {
    try {
      const response = await fetch('/api/user/preferences', {
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        }
      });
      const data = await response.json();
      
      console.log('Préférences chargées:', data);
      
      // Récupérer la configuration des widgets
      if (data.widgets_config) {
        this.config = data.widgets_config;
        console.log('Configuration des widgets chargée:', this.config);
      }
      
      // Appliquer le fond d'écran
      if (data.background_image) {
        document.body.style.backgroundImage = `url('/static/img/${data.background_image}')`;
        console.log('Fond d\'écran appliqué:', data.background_image);
      }
      
      return true;
    } catch (error) {
      console.error('Erreur lors du chargement des préférences:', error);
      return false;
    }
  }
  
  // Sauvegarder la configuration sur le serveur
  async saveConfig() {
    try {
      const response = await fetch('/api/user/preferences/widgets', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({
          widgets_config: this.config
        })
      });
      
      const data = await response.json();
      return data.success;
    } catch (error) {
      console.error('Erreur lors de la sauvegarde des préférences:', error);
      return false;
    }
  }
  
  // Sauvegarder le fond d'écran
  async saveBackground(backgroundImage) {
    try {
      const response = await fetch('/api/user/preferences/background', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({
          background: backgroundImage
        })
      });
      
      const data = await response.json();
      return data.success;
    } catch (error) {
      console.error('Erreur lors de la sauvegarde du fond d\'écran:', error);
      return false;
    }
  }
  
  // Enregistrer un widget
  registerWidget(id, widgetClass) {
    this.widgets[id] = widgetClass;
  }
  
  // Activer un widget
  async activateWidget(id) {
    if (!this.widgets[id]) {
      console.error(`Widget ${id} non trouvé`);
      return false;
    }
    
    console.log(`Activation du widget ${id}`);
    
    // Créer une instance du widget
    const widget = new this.widgets[id]();
    
    // Ajouter à la liste des widgets actifs
    this.activeWidgets.push({
      id,
      instance: widget
    });
    
    // Mettre à jour la configuration
    if (!this.config.activeWidgets.includes(id)) {
      this.config.activeWidgets.push(id);
    }
    
    // Initialiser et afficher le widget
    widget.init();
    widget.render();
    
    console.log(`Widget ${id} initialisé et rendu`);
    
    // Positionner le widget selon la configuration
    if (this.config.positions && this.config.positions[id]) {
      widget.element.style.left = this.config.positions[id].x;
      widget.element.style.top = this.config.positions[id].y;
      console.log(`Widget ${id} positionné selon la configuration: ${this.config.positions[id].x}, ${this.config.positions[id].y}`);
    } else {
      console.log(`Widget ${id} positionné par défaut`);
    }
    
    // Sauvegarder la configuration
    await this.saveConfig();
    
    return true;
  }
  
  // Désactiver un widget
  async deactivateWidget(id) {
    const index = this.activeWidgets.findIndex(w => w.id === id);
    if (index === -1) return false;
    
    // Détruire l'instance du widget
    this.activeWidgets[index].instance.destroy();
    
    // Retirer de la liste des widgets actifs
    this.activeWidgets.splice(index, 1);
    
    // Mettre à jour la configuration
    const configIndex = this.config.activeWidgets.indexOf(id);
    if (configIndex !== -1) {
      this.config.activeWidgets.splice(configIndex, 1);
    }
    
    // Sauvegarder la configuration
    await this.saveConfig();
    
    return true;
  }
  
  // Initialiser tous les widgets actifs
  async initWidgets() {
    if (this.isInitialized) return;
    
    console.log('Initialisation des widgets...');
    
    // Charger la configuration
    await this.loadConfig();
    
    console.log('Widgets actifs à charger:', this.config.activeWidgets);
    
    // Activer les widgets selon la configuration
    if (this.config.activeWidgets && Array.isArray(this.config.activeWidgets)) {
      for (const id of this.config.activeWidgets) {
        console.log('Activation du widget:', id);
        await this.activateWidget(id);
      }
    } else {
      console.log('Aucun widget actif trouvé dans la configuration');
    }
    
    this.isInitialized = true;
    console.log('Initialisation des widgets terminée');
  }
  
  // Mettre à jour la position d'un widget
  async updateWidgetPosition(id, x, y) {
    if (!this.config.positions) {
      this.config.positions = {};
    }
    
    if (!this.config.positions[id]) {
      this.config.positions[id] = {};
    }
    
    this.config.positions[id].x = x;
    this.config.positions[id].y = y;
    
    // Sauvegarder la configuration
    await this.saveConfig();
  }
  
  // Mettre à jour les paramètres d'un widget
  async updateWidgetSettings(id, settings) {
    if (!this.config.settings) {
      this.config.settings = {};
    }
    
    if (!this.config.settings[id]) {
      this.config.settings[id] = {};
    }
    
    this.config.settings[id] = {
      ...this.config.settings[id],
      ...settings
    };
    
    // Sauvegarder la configuration
    await this.saveConfig();
  }
  
  // Ouvrir le panneau de configuration
  openConfigPanel() {
    // Fermer le panneau s'il est déjà ouvert
    const existingPanel = document.querySelector('.widget-config-panel');
    if (existingPanel) {
      existingPanel.remove();
      return;
    }
    
    // Créer et afficher l'interface de configuration
    const panel = document.createElement('div');
    panel.className = 'widget-config-panel';
    
    // Ajouter un titre
    const title = document.createElement('h2');
    title.textContent = 'Gestionnaire de widgets';
    title.className = 'widget-config-title';
    panel.appendChild(title);
    
    // Ajouter la liste des widgets disponibles
    const widgetList = document.createElement('div');
    widgetList.className = 'widget-list';
    
    Object.keys(this.widgets).forEach(id => {
      const widget = this.widgets[id];
      const isActive = this.activeWidgets.some(w => w.id === id);
      
      const item = document.createElement('div');
      item.className = 'widget-item';
      
      const checkbox = document.createElement('input');
      checkbox.type = 'checkbox';
      checkbox.checked = isActive;
      checkbox.addEventListener('change', () => {
        if (checkbox.checked) {
          this.activateWidget(id);
        } else {
          this.deactivateWidget(id);
        }
      });
      
      const label = document.createElement('label');
      label.textContent = widget.name || id;
      
      item.appendChild(checkbox);
      item.appendChild(label);
      widgetList.appendChild(item);
    });
    
    panel.appendChild(widgetList);
    
    // Ajouter un bouton de fermeture
    const closeButton = document.createElement('button');
    closeButton.textContent = 'Fermer';
    closeButton.className = 'widget-config-close';
    closeButton.addEventListener('click', () => {
      panel.remove();
    });
    
    panel.appendChild(closeButton);
    
    document.body.appendChild(panel);
  }
}

// Classe de base pour tous les widgets
class Widget {
  constructor(id, name) {
    this.id = id;
    this.name = name;
    this.element = null;
  }
  
  init() {
    // Créer l'élément DOM du widget
    this.element = document.createElement('div');
    this.element.className = `widget widget-${this.id}`;
    this.element.setAttribute('data-widget-id', this.id);
    
    // Ajouter des styles pour s'assurer que le widget est visible
    this.element.style.backgroundColor = 'rgba(255, 255, 255, 0.9)';
    this.element.style.zIndex = '1000';
    this.element.style.width = '250px';
    this.element.style.height = '150px';
    
    // Rendre le widget déplaçable
    this.makeDraggable();
  }
  
  render() {
    // À implémenter dans les classes dérivées
    document.body.appendChild(this.element);
    
    // Positionner le widget par défaut au milieu de l'écran
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;
    
    // Position par défaut : au milieu de l'écran, mais en évitant la barre du haut
    const left = Math.random() * (viewportWidth - 300) + 50;
    const top = Math.random() * (viewportHeight - 300) + 100;
    
    this.element.style.left = `${left}px`;
    this.element.style.top = `${top}px`;
    
    console.log(`Widget ${this.id} rendu à la position: ${left}, ${top}`);
  }
  
  destroy() {
    // Supprimer l'élément DOM
    if (this.element && this.element.parentNode) {
      this.element.parentNode.removeChild(this.element);
    }
  }
  
  makeDraggable() {
    // Implémentation du drag & drop
    let isDragging = false;
    let offsetX, offsetY;
    
    const header = document.createElement('div');
    header.className = 'widget-header';
    header.innerHTML = `
      <div class="widget-title">${this.name}</div>
      <div class="widget-close">&times;</div>
    `;
    
    // Ajouter l'en-tête au widget s'il n'existe pas déjà
    if (!this.element.querySelector('.widget-header')) {
      this.element.prepend(header);
    } else {
      header = this.element.querySelector('.widget-header');
    }
    
    // Gérer la fermeture du widget
    header.querySelector('.widget-close').addEventListener('click', () => {
      window.widgetManager.deactivateWidget(this.id);
    });
    
    header.addEventListener('mousedown', (e) => {
      // Ignorer si on clique sur le bouton de fermeture
      if (e.target.classList.contains('widget-close')) return;
      
      isDragging = true;
      offsetX = e.clientX - this.element.getBoundingClientRect().left;
      offsetY = e.clientY - this.element.getBoundingClientRect().top;
      this.element.style.cursor = 'grabbing';
      
      // Mettre le widget au premier plan
      this.element.style.zIndex = 1000;
    });
    
    document.addEventListener('mousemove', (e) => {
      if (!isDragging) return;
      
      const x = e.clientX - offsetX;
      const y = e.clientY - offsetY;
      
      this.element.style.left = `${x}px`;
      this.element.style.top = `${y}px`;
    });
    
    document.addEventListener('mouseup', () => {
      if (isDragging) {
        isDragging = false;
        this.element.style.cursor = 'default';
        
        // Sauvegarder la position
        const widgetManager = window.widgetManager;
        if (widgetManager) {
          widgetManager.updateWidgetPosition(this.id, this.element.style.left, this.element.style.top);
        }
      }
    });
  }
}

// Widget Horloge
class ClockWidget extends Widget {
  constructor() {
    super('clock', 'Horloge');
    this.interval = null;
  }
  
  init() {
    super.init();
    
    // Créer la structure du widget
    const content = document.createElement('div');
    content.className = 'widget-content';
    content.innerHTML = `
      <div class="clock-time">00:00:00</div>
      <div class="clock-date">01/01/2025</div>
    `;
    
    this.element.appendChild(content);
  }
  
  render() {
    super.render();
    
    // Mettre à jour l'heure toutes les secondes
    this.updateClock();
    this.interval = setInterval(() => this.updateClock(), 1000);
  }
  
  updateClock() {
    const now = new Date();
    
    // Mettre à jour l'heure
    const timeElement = this.element.querySelector('.clock-time');
    timeElement.textContent = now.toLocaleTimeString();
    
    // Mettre à jour la date
    const dateElement = this.element.querySelector('.clock-date');
    dateElement.textContent = now.toLocaleDateString();
  }
  
  destroy() {
    // Arrêter l'intervalle
    if (this.interval) {
      clearInterval(this.interval);
    }
    
    super.destroy();
  }
}

// Widget "Yeux qui suivent la souris"
class EyesWidget extends Widget {
  constructor() {
    super('eyes', 'Yeux animés');
  }
  
  init() {
    super.init();
    
    // Créer la structure du widget
    const content = document.createElement('div');
    content.className = 'widget-content';
    content.innerHTML = `
      <div class="eyes-container">
        <div class="eye">
          <div class="pupil"></div>
        </div>
        <div class="eye">
          <div class="pupil"></div>
        </div>
      </div>
    `;
    
    this.element.appendChild(content);
    
    // Ajouter les styles spécifiques
    const style = document.createElement('style');
    style.textContent = `
      .eyes-container {
        display: flex;
        justify-content: space-around;
        padding: 20px;
      }
      
      .eye {
        width: 80px;
        height: 80px;
        background: white;
        border-radius: 50%;
        position: relative;
        box-shadow: 0 0 0 10px rgba(255,255,255,0.1);
        overflow: hidden;
      }
      
      .pupil {
        width: 30px;
        height: 30px;
        background: #333;
        border-radius: 50%;
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
      }
    `;
    
    // Ajouter le style s'il n'existe pas déjà
    if (!document.getElementById('eyes-widget-style')) {
      style.id = 'eyes-widget-style';
      document.head.appendChild(style);
    }
  }
  
  render() {
    super.render();
    
    // Ajouter l'événement pour suivre la souris
    this.handleMouseMove = this.handleMouseMove.bind(this);
    document.addEventListener('mousemove', this.handleMouseMove);
  }
  
  handleMouseMove(e) {
    const pupils = this.element.querySelectorAll('.pupil');
    const eyes = this.element.querySelectorAll('.eye');
    
    eyes.forEach((eye, index) => {
      // Calculer la position de l'œil
      const eyeRect = eye.getBoundingClientRect();
      const eyeCenterX = eyeRect.left + eyeRect.width / 2;
      const eyeCenterY = eyeRect.top + eyeRect.height / 2;
      
      // Calculer l'angle entre la souris et l'œil
      const angle = Math.atan2(e.clientY - eyeCenterY, e.clientX - eyeCenterX);
      
      // Calculer la distance maximale que la pupille peut parcourir
      const maxDistance = eyeRect.width / 4;
      
      // Calculer la nouvelle position de la pupille
      const pupilX = Math.cos(angle) * maxDistance;
      const pupilY = Math.sin(angle) * maxDistance;
      
      // Appliquer la transformation
      pupils[index].style.transform = `translate(calc(-50% + ${pupilX}px), calc(-50% + ${pupilY}px))`;
    });
  }
  
  destroy() {
    // Supprimer l'événement de suivi de la souris
    document.removeEventListener('mousemove', this.handleMouseMove);
    
    super.destroy();
  }
}

// Widget Météo
class WeatherWidget extends Widget {
  constructor() {
    super('weather', 'Météo');
    this.apiKey = ''; // Clé API OpenWeatherMap (à remplacer par une vraie clé)
    this.city = 'Paris'; // Ville par défaut
    this.weatherData = null;
  }
  
  init() {
    super.init();
    
    // Créer la structure du widget
    const content = document.createElement('div');
    content.className = 'widget-content';
    content.innerHTML = `
      <div class="weather-container">
        <div class="weather-header">
          <input type="text" class="weather-city-input" placeholder="Entrez une ville" value="${this.city}">
          <button class="weather-search-btn"><i class="fas fa-search"></i></button>
        </div>
        <div class="weather-loading">Chargement...</div>
        <div class="weather-error" style="display: none;">Impossible de charger les données météo</div>
        <div class="weather-content" style="display: none;">
          <div class="weather-city">Paris, FR</div>
          <div class="weather-temp">--°C</div>
          <div class="weather-desc">--</div>
          <div class="weather-details">
            <div class="weather-detail">
              <i class="fas fa-tint"></i>
              <span class="weather-humidity">--%</span>
            </div>
            <div class="weather-detail">
              <i class="fas fa-wind"></i>
              <span class="weather-wind">-- km/h</span>
            </div>
          </div>
        </div>
      </div>
    `;
    
    this.element.appendChild(content);
    
    // Ajouter les styles spécifiques
    const style = document.createElement('style');
    style.textContent = `
      .weather-container {
        padding: 10px;
      }
      
      .weather-header {
        display: flex;
        margin-bottom: 15px;
      }
      
      .weather-city-input {
        flex: 1;
        padding: 8px;
        border: 1px solid #ddd;
        border-radius: 4px 0 0 4px;
        font-family: inherit;
      }
      
      .weather-search-btn {
        padding: 8px 12px;
        background: #4f46e5;
        color: white;
        border: none;
        border-radius: 0 4px 4px 0;
        cursor: pointer;
      }
      
      .weather-search-btn:hover {
        background: #7c3aed;
      }
      
      .weather-loading, .weather-error {
        text-align: center;
        padding: 20px 0;
        color: #666;
      }
      
      .weather-error {
        color: #ef4444;
      }
      
      .weather-city {
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 10px;
        text-align: center;
      }
      
      .weather-temp {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 5px;
      }
      
      .weather-desc {
        text-align: center;
        margin-bottom: 15px;
        color: #666;
        text-transform: capitalize;
      }
      
      .weather-details {
        display: flex;
        justify-content: space-around;
        margin-top: 15px;
      }
      
      .weather-detail {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 5px;
      }
      
      .weather-detail i {
        font-size: 1.2rem;
        color: #4f46e5;
      }
    `;
    
    // Ajouter le style s'il n'existe pas déjà
    if (!document.getElementById('weather-widget-style')) {
      style.id = 'weather-widget-style';
      document.head.appendChild(style);
    }
    
    // Ajouter les événements
    const searchBtn = this.element.querySelector('.weather-search-btn');
    const cityInput = this.element.querySelector('.weather-city-input');
    
    searchBtn.addEventListener('click', () => {
      this.city = cityInput.value.trim();
      this.fetchWeatherData();
    });
    
    cityInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        this.city = cityInput.value.trim();
        this.fetchWeatherData();
      }
    });
  }
  
  render() {
    super.render();
    
    // Charger les données météo
    this.fetchWeatherData();
  }
  
  async fetchWeatherData() {
    if (!this.city) return;
    
    const loadingEl = this.element.querySelector('.weather-loading');
    const errorEl = this.element.querySelector('.weather-error');
    const contentEl = this.element.querySelector('.weather-content');
    
    // Afficher le chargement
    loadingEl.style.display = 'block';
    errorEl.style.display = 'none';
    contentEl.style.display = 'none';
    
    try {
      // Simuler les données météo (à remplacer par un vrai appel API)
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Données simulées
      const weatherData = {
        name: this.city,
        country: 'FR',
        temp: Math.round(10 + Math.random() * 20),
        description: ['ensoleillé', 'nuageux', 'pluvieux', 'orageux'][Math.floor(Math.random() * 4)],
        humidity: Math.round(40 + Math.random() * 40),
        wind: Math.round(5 + Math.random() * 25)
      };
      
      this.weatherData = weatherData;
      this.updateWeatherUI();
      
      // Masquer le chargement et afficher le contenu
      loadingEl.style.display = 'none';
      contentEl.style.display = 'block';
    } catch (error) {
      console.error('Erreur lors du chargement des données météo:', error);
      
      // Masquer le chargement et afficher l'erreur
      loadingEl.style.display = 'none';
      errorEl.style.display = 'block';
    }
  }
  
  updateWeatherUI() {
    if (!this.weatherData) return;
    
    const cityEl = this.element.querySelector('.weather-city');
    const tempEl = this.element.querySelector('.weather-temp');
    const descEl = this.element.querySelector('.weather-desc');
    const humidityEl = this.element.querySelector('.weather-humidity');
    const windEl = this.element.querySelector('.weather-wind');
    
    cityEl.textContent = `${this.weatherData.name}, ${this.weatherData.country}`;
    tempEl.textContent = `${this.weatherData.temp}°C`;
    descEl.textContent = this.weatherData.description;
    humidityEl.textContent = `${this.weatherData.humidity}%`;
    windEl.textContent = `${this.weatherData.wind} km/h`;
  }
  
  destroy() {
    super.destroy();
  }
}

// Widget Notes
class NotesWidget extends Widget {
  constructor() {
    super('notes', 'Bloc-notes');
    this.notes = localStorage.getItem('widget-notes') || '';
  }
  
  init() {
    super.init();
    
    // Créer la structure du widget
    const content = document.createElement('div');
    content.className = 'widget-content';
    content.innerHTML = `
      <textarea class="notes-textarea" placeholder="Écrivez vos notes ici...">${this.notes}</textarea>
      <div class="notes-footer">
        <button class="notes-save-btn">Enregistrer</button>
        <button class="notes-clear-btn">Effacer</button>
      </div>
    `;
    
    this.element.appendChild(content);
    
    // Ajouter les styles spécifiques
    const style = document.createElement('style');
    style.textContent = `
      .notes-textarea {
        width: 100%;
        height: 200px;
        padding: 10px;
        border: 1px solid #ddd;
        border-radius: 4px;
        resize: none;
        font-family: inherit;
        margin-bottom: 10px;
      }
      
      .notes-footer {
        display: flex;
        justify-content: space-between;
      }
      
      .notes-save-btn, .notes-clear-btn {
        padding: 8px 12px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-family: inherit;
      }
      
      .notes-save-btn {
        background: #4f46e5;
        color: white;
      }
      
      .notes-save-btn:hover {
        background: #7c3aed;
      }
      
      .notes-clear-btn {
        background: #f3f4f6;
        color: #374151;
      }
      
      .notes-clear-btn:hover {
        background: #e5e7eb;
      }
    `;
    
    // Ajouter le style s'il n'existe pas déjà
    if (!document.getElementById('notes-widget-style')) {
      style.id = 'notes-widget-style';
      document.head.appendChild(style);
    }
    
    // Ajouter les événements
    const textarea = this.element.querySelector('.notes-textarea');
    const saveBtn = this.element.querySelector('.notes-save-btn');
    const clearBtn = this.element.querySelector('.notes-clear-btn');
    
    saveBtn.addEventListener('click', () => {
      this.notes = textarea.value;
      localStorage.setItem('widget-notes', this.notes);
      alert('Notes enregistrées !');
    });
    
    clearBtn.addEventListener('click', () => {
      if (confirm('Êtes-vous sûr de vouloir effacer toutes vos notes ?')) {
        textarea.value = '';
        this.notes = '';
        localStorage.setItem('widget-notes', '');
      }
    });
  }
  
  render() {
    super.render();
  }
  
  destroy() {
    super.destroy();
  }
}

// Widget Devoirs
class HomeworkWidget extends Widget {
  constructor() {
    super('homework', 'Devoirs');
    this.homeworks = JSON.parse(localStorage.getItem('widget-homeworks') || '[]');
  }
  
  init() {
    super.init();
    
    // Créer la structure du widget
    const content = document.createElement('div');
    content.className = 'widget-content';
    content.innerHTML = `
      <div class="homework-container">
        <div class="homework-header">
          <h3>Mes devoirs</h3>
          <button class="homework-add-btn"><i class="fas fa-plus"></i></button>
        </div>
        <div class="homework-list"></div>
        <div class="homework-form" style="display: none;">
          <input type="text" class="homework-title-input" placeholder="Titre du devoir">
          <input type="date" class="homework-date-input">
          <select class="homework-subject-input">
            <option value="">-- Matière --</option>
            <option value="Mathématiques">Mathématiques</option>
            <option value="Français">Français</option>
            <option value="Histoire-Géo">Histoire-Géo</option>
            <option value="Anglais">Anglais</option>
            <option value="Physique-Chimie">Physique-Chimie</option>
            <option value="SVT">SVT</option>
            <option value="NSI">NSI</option>
          </select>
          <div class="homework-form-buttons">
            <button class="homework-save-btn">Ajouter</button>
            <button class="homework-cancel-btn">Annuler</button>
          </div>
        </div>
      </div>
    `;
    
    this.element.appendChild(content);
    
    // Ajouter les styles et les événements (code omis pour brièveté)
  }
  
  render() {
    super.render();
    this.renderHomeworkList();
  }
  
  renderHomeworkList() {
    // Afficher la liste des devoirs (code omis pour brièveté)
  }
  
  destroy() {
    super.destroy();
  }
}

// Initialiser le gestionnaire de widgets
document.addEventListener('DOMContentLoaded', () => {
  // Créer l'instance du gestionnaire de widgets
  window.widgetManager = new WidgetManager();
  
  // Enregistrer les widgets disponibles
  window.widgetManager.registerWidget('clock', ClockWidget);
  window.widgetManager.registerWidget('eyes', EyesWidget);
  window.widgetManager.registerWidget('weather', WeatherWidget);
  window.widgetManager.registerWidget('notes', NotesWidget);
  window.widgetManager.registerWidget('homework', HomeworkWidget);
  window.widgetManager.registerWidget('calculator', CalculatorWidget);
  
  // Initialiser les widgets actifs
  window.widgetManager.initWidgets();
  
  console.log('Gestionnaire de widgets initialisé');
});
