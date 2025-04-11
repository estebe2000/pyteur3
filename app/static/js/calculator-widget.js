// Widget Calculatrice
class CalculatorWidget extends Widget {
  constructor() {
    super('calculator', 'Calculatrice');
    this.currentValue = '';
    this.previousValue = '';
    this.operation = null;
    this.shouldResetDisplay = false;
    this.errorState = false;
  }
  
  init() {
    super.init();
    
    // Créer la structure du widget
    const content = document.createElement('div');
    content.className = 'widget-content';
    content.innerHTML = `
      <div class="calculator-container">
        <div class="calculator-display-container">
          <div class="calculator-operation"></div>
          <div class="calculator-display">0</div>
        </div>
        <div class="calculator-buttons">
          <button class="calculator-btn calculator-btn-clear">C</button>
          <button class="calculator-btn calculator-btn-backspace">⌫</button>
          <button class="calculator-btn calculator-btn-op" data-op="%">%</button>
          <button class="calculator-btn calculator-btn-op" data-op="/">÷</button>
          
          <button class="calculator-btn calculator-btn-num" data-num="7">7</button>
          <button class="calculator-btn calculator-btn-num" data-num="8">8</button>
          <button class="calculator-btn calculator-btn-num" data-num="9">9</button>
          <button class="calculator-btn calculator-btn-op" data-op="*">×</button>
          
          <button class="calculator-btn calculator-btn-num" data-num="4">4</button>
          <button class="calculator-btn calculator-btn-num" data-num="5">5</button>
          <button class="calculator-btn calculator-btn-num" data-num="6">6</button>
          <button class="calculator-btn calculator-btn-op" data-op="-">−</button>
          
          <button class="calculator-btn calculator-btn-num" data-num="1">1</button>
          <button class="calculator-btn calculator-btn-num" data-num="2">2</button>
          <button class="calculator-btn calculator-btn-num" data-num="3">3</button>
          <button class="calculator-btn calculator-btn-op" data-op="+">+</button>
          
          <button class="calculator-btn calculator-btn-num" data-num="0">0</button>
          <button class="calculator-btn calculator-btn-num" data-num=".">.</button>
          <button class="calculator-btn calculator-btn-equals" data-op="=">=</button>
        </div>
      </div>
    `;
    
    this.element.appendChild(content);
    
    // Ajouter les styles spécifiques
    const style = document.createElement('style');
    style.textContent = `
      .calculator-container {
        padding: 10px;
      }
      
      .calculator-display-container {
        background: #f3f4f6;
        padding: 10px 15px;
        margin-bottom: 10px;
        border-radius: 4px;
        overflow: hidden;
      }
      
      .calculator-operation {
        text-align: right;
        font-size: 0.9rem;
        color: #6b7280;
        height: 1.2rem;
        margin-bottom: 5px;
      }
      
      .calculator-display {
        text-align: right;
        font-size: 1.5rem;
        white-space: nowrap;
        text-overflow: ellipsis;
        overflow: hidden;
      }
      
      .calculator-error {
        color: #ef4444;
      }
      
      .calculator-buttons {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 8px;
      }
      
      .calculator-btn {
        padding: 12px;
        border: none;
        border-radius: 4px;
        font-size: 1.2rem;
        cursor: pointer;
        background: #f3f4f6;
        transition: all 0.2s;
      }
      
      .calculator-btn:hover {
        background: #e5e7eb;
      }
      
      .calculator-btn:active {
        transform: scale(0.95);
      }
      
      .calculator-btn-op {
        background: #4f46e5;
        color: white;
      }
      
      .calculator-btn-op:hover {
        background: #7c3aed;
      }
      
      .calculator-btn-equals {
        background: #10b981;
        color: white;
        grid-column: span 2;
      }
      
      .calculator-btn-equals:hover {
        background: #059669;
      }
      
      .calculator-btn-clear, .calculator-btn-backspace {
        background: #ef4444;
        color: white;
      }
      
      .calculator-btn-clear:hover, .calculator-btn-backspace:hover {
        background: #dc2626;
      }
    `;
    
    // Ajouter le style s'il n'existe pas déjà
    if (!document.getElementById('calculator-widget-style')) {
      style.id = 'calculator-widget-style';
      document.head.appendChild(style);
    }
    
    // Ajouter les événements
    const numButtons = this.element.querySelectorAll('.calculator-btn-num');
    const opButtons = this.element.querySelectorAll('.calculator-btn-op');
    const equalsButton = this.element.querySelector('.calculator-btn-equals');
    const clearButton = this.element.querySelector('.calculator-btn-clear');
    const backspaceButton = this.element.querySelector('.calculator-btn-backspace');
    
    numButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        const num = btn.dataset.num;
        this.appendNumber(num);
      });
    });
    
    opButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        const op = btn.dataset.op;
        this.setOperation(op);
      });
    });
    
    equalsButton.addEventListener('click', () => {
      this.calculate();
    });
    
    clearButton.addEventListener('click', () => {
      this.clear();
    });
    
    backspaceButton.addEventListener('click', () => {
      this.backspace();
    });
    
    // Ajouter la prise en charge du clavier
    document.addEventListener('keydown', (e) => {
      if (!this.element.isConnected) return;
      
      if (e.key >= '0' && e.key <= '9' || e.key === '.') {
        this.appendNumber(e.key);
      } else if (e.key === '+' || e.key === '-' || e.key === '*' || e.key === '/' || e.key === '%') {
        this.setOperation(e.key);
      } else if (e.key === 'Enter' || e.key === '=') {
        this.calculate();
      } else if (e.key === 'Escape') {
        this.clear();
      } else if (e.key === 'Backspace') {
        this.backspace();
      }
    });
  }
  
  render() {
    super.render();
    this.updateDisplay();
  }
  
  appendNumber(number) {
    // Si on est en état d'erreur, effacer d'abord
    if (this.errorState) {
      this.clear();
    }
    
    // Si on doit réinitialiser l'affichage après une opération
    if (this.shouldResetDisplay) {
      this.currentValue = '';
      this.shouldResetDisplay = false;
    }
    
    // Éviter d'ajouter plusieurs points décimaux
    if (number === '.' && this.currentValue.includes('.')) return;
    
    // Remplacer le 0 initial
    if (this.currentValue === '0' && number !== '.') {
      this.currentValue = number;
    } else {
      this.currentValue += number;
    }
    
    this.updateDisplay();
  }
  
  setOperation(operation) {
    // Si on est en état d'erreur, effacer d'abord
    if (this.errorState) {
      this.clear();
      return;
    }
    
    // Si aucune valeur n'est entrée, ne rien faire
    // Sauf si c'est un moins (pour les nombres négatifs)
    if (this.currentValue === '' && this.previousValue === '') {
      if (operation === '-') {
        this.currentValue = '-';
        this.updateDisplay();
      }
      return;
    }
    
    // Si on a déjà une opération en cours, calculer d'abord
    if (this.previousValue !== '' && this.currentValue !== '') {
      this.calculate();
    }
    
    this.operation = operation;
    
    // Si aucune valeur courante, changer simplement l'opération
    if (this.currentValue === '') {
      this.updateDisplay();
      return;
    }
    
    this.previousValue = this.currentValue;
    this.currentValue = '';
    this.shouldResetDisplay = false;
    
    this.updateDisplay();
  }
  
  calculate() {
    let computation;
    const prev = parseFloat(this.previousValue);
    const current = parseFloat(this.currentValue || this.previousValue);
    
    if (isNaN(prev)) return;
    
    try {
      switch (this.operation) {
        case '+':
          computation = prev + current;
          break;
        case '-':
          computation = prev - current;
          break;
        case '*':
          computation = prev * current;
          break;
        case '/':
          if (current === 0) {
            throw new Error('Division par zéro');
          }
          computation = prev / current;
          break;
        case '%':
          if (current === 0) {
            throw new Error('Modulo par zéro');
          }
          computation = prev % current;
          break;
        default:
          return;
      }
      
      // Limiter le nombre de décimales pour éviter les problèmes d'affichage
      if (computation.toString().includes('.')) {
        const decimalPart = computation.toString().split('.')[1];
        if (decimalPart && decimalPart.length > 10) {
          computation = parseFloat(computation.toFixed(10));
        }
      }
      
      this.currentValue = computation.toString();
      this.previousValue = '';
      this.shouldResetDisplay = true;
      this.errorState = false;
      
    } catch (error) {
      this.currentValue = error.message || 'Erreur';
      this.errorState = true;
    }
    
    this.operation = null;
    this.updateDisplay();
  }
  
  clear() {
    this.currentValue = '';
    this.previousValue = '';
    this.operation = null;
    this.shouldResetDisplay = false;
    this.errorState = false;
    
    this.updateDisplay();
  }
  
  backspace() {
    this.currentValue = this.currentValue.slice(0, -1);
    
    this.updateDisplay();
  }
  
  updateDisplay() {
    const displayEl = this.element.querySelector('.calculator-display');
    const operationEl = this.element.querySelector('.calculator-operation');
    
    // Afficher la valeur actuelle ou précédente
    if (this.currentValue === '') {
      displayEl.textContent = this.previousValue || '0';
    } else {
      displayEl.textContent = this.currentValue;
    }
    
    // Afficher l'opération en cours
    if (this.operation && this.previousValue) {
      let opSymbol = this.operation;
      switch (this.operation) {
        case '*': opSymbol = '×'; break;
        case '/': opSymbol = '÷'; break;
        case '-': opSymbol = '−'; break;
      }
      operationEl.textContent = `${this.previousValue} ${opSymbol}`;
    } else {
      operationEl.textContent = '';
    }
    
    // Appliquer le style d'erreur si nécessaire
    if (this.errorState) {
      displayEl.classList.add('calculator-error');
    } else {
      displayEl.classList.remove('calculator-error');
    }
  }
  
  destroy() {
    super.destroy();
  }
}

// Ajouter le widget calculatrice au gestionnaire de widgets
document.addEventListener('DOMContentLoaded', () => {
  // Attendre que le gestionnaire de widgets soit initialisé
  const checkWidgetManager = setInterval(() => {
    if (window.widgetManager) {
      clearInterval(checkWidgetManager);
      
      // Enregistrer le widget calculatrice
      window.widgetManager.registerWidget('calculator', CalculatorWidget);
      console.log('Widget calculatrice enregistré');
    }
  }, 100);
});
