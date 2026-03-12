export class PanelManager {
  constructor() {
    this.panelToggles = document.querySelectorAll('.panel-toggle');
    this.sidePanels = document.querySelectorAll('.side-panels-container .side-panel');
    this.initialize();
  }

  initialize() {
    this.panelToggles.forEach(toggle => {
      toggle.addEventListener('click', () => {
        const panelName = toggle.getAttribute('data-panel');
        const panel = document.getElementById(`${panelName}Panel`);

        if (panel) {
          // Toggle active class
          panel.classList.toggle('active');
          toggle.classList.toggle('active');

          // If a panel is opened, close others
          this.sidePanels.forEach(p => {
            if (p !== panel) {
              p.classList.remove('active');
              const correspondingToggle = document.querySelector(`.panel-toggle[data-panel="${p.id.replace('Panel', '')}"]`);
              if (correspondingToggle) {
                correspondingToggle.classList.remove('active');
              }
            }
          });
        }
      });
    });
  }
}

// Initialize PanelManager on DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {
  new PanelManager();
}); 