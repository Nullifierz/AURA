// hud.js - Dynamic Head Up Display for AURA

class HUD {
    constructor() {
        this.hudContainer = null;
        this.isVisible = false;
        this.isDragging = false;
        this.dragOffset = { x: 0, y: 0 };
        this.sections = []; // Store dynamic sections
        
        this.init();
    }

    init() {
        // Create HUD structure
        this.createHUD();
        this.setupEventListeners();
        
        console.log("Dynamic HUD initialized");
    }

    createHUD() {
        // Create HUD container
        this.hudContainer = document.createElement('div');
        this.hudContainer.id = 'aura-hud';
        this.hudContainer.className = 'aura-hud hidden';
        
        this.hudContainer.innerHTML = `
            <div class="hud-header" id="hud-header">
                <div class="hud-controls">
                    <button class="hud-btn hud-close" id="hud-close" title="Close">
                        <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" fill="currentColor" viewBox="0 0 16 16">
                            <path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"/>
                        </svg>
                    </button>
                </div>
            </div>
            
            <div class="hud-content" id="hud-content">
                <div class="hud-loading"></div>
            </div>
        `;
        
        document.body.appendChild(this.hudContainer);
        
        // Create toggle button
        this.toggleBtn = document.createElement('button');
        this.toggleBtn.id = 'toggle-hud-btn';
        this.toggleBtn.className = 'hud-toggle-btn';
        this.toggleBtn.textContent = 'HUD';
        document.body.appendChild(this.toggleBtn);
    }

    setupEventListeners() {
        // Toggle button
        this.toggleBtn.addEventListener('click', () => this.toggle());
        
        // Close button
        const closeBtn = document.getElementById('hud-close');
        closeBtn.addEventListener('click', () => this.hide());
        
        // Dragging
        const header = document.getElementById('hud-header');
        header.addEventListener('mousedown', (e) => this.startDrag(e));
        document.addEventListener('mousemove', (e) => this.drag(e));
        document.addEventListener('mouseup', () => this.stopDrag());
    }

    /**
     * Load HUD data from backend or accept data directly
     * @param {Object|string} dataOrType - Either data object with sections or location string
     */
    async loadData(dataOrType = null) {
        const contentContainer = document.getElementById('hud-content');
        
        // If dataOrType is an object with sections, render directly
        if (dataOrType && typeof dataOrType === 'object' && dataOrType.sections) {
            console.log("Rendering HUD data directly:", dataOrType);
            this.renderContent(dataOrType);
            return;
        }
        
        // Otherwise, fetch from backend
        try {
            // Show loading state
            contentContainer.innerHTML = '<div class="hud-loading">Loading data...</div>';
            
            // Build URL with optional location parameter
            let url = 'http://localhost:8000/hud-data';
            if (dataOrType && typeof dataOrType === 'string') {
                url += `?location=${dataOrType}`;
            }
            
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error('Failed to fetch HUD data');
            }
            
            const data = await response.json();
            
            // Render the dynamic content
            this.renderContent(data);
            
        } catch (error) {
            console.error('Error loading HUD data:', error);
            contentContainer.innerHTML = `
                <div class="hud-error">
                    <div class="error-icon">⚠️</div>
                    <div class="error-text">Failed to load HUD data</div>
                </div>
            `;
        }
    }

    /**
     * Render dynamic content based on JSON structure
     * @param {Object} data - JSON data with sections array
     */
    renderContent(data) {
        const contentContainer = document.getElementById('hud-content');
        contentContainer.innerHTML = '';
        
        if (!data.sections || data.sections.length === 0) {
            contentContainer.innerHTML = '<div class="hud-empty">No data to display</div>';
            return;
        }
        
        this.sections = data.sections;
        
        // Sort sections: images first, then rest
        const sortedSections = [...data.sections].sort((a, b) => {
            const priority = { 'image': 0, 'keyvalue': 1, 'table': 2, 'text': 3, 'list': 4, 'chart': 5 };
            const aPriority = priority[a.type] !== undefined ? priority[a.type] : 99;
            const bPriority = priority[b.type] !== undefined ? priority[b.type] : 99;
            return aPriority - bPriority;
        });
        
        sortedSections.forEach((section, index) => {
            const sectionElement = this.createSection(section, index);
            contentContainer.appendChild(sectionElement);
        });
    }

    /**
     * Create a section element based on type
     * @param {Object} section - Section configuration
     * @param {number} index - Section index
     */
    createSection(section, index) {
        const sectionDiv = document.createElement('div');
        sectionDiv.className = `hud-section hud-section-${section.type}`;
        sectionDiv.id = `hud-section-${index}`;
        
        // For image sections, add special styling
        if (section.type === 'image') {
            sectionDiv.classList.add('hud-section-featured');
        }
        
        // Add title if provided
        if (section.title) {
            const titleDiv = document.createElement('div');
            titleDiv.className = 'hud-section-title';
            titleDiv.textContent = section.title.toUpperCase();
            sectionDiv.appendChild(titleDiv);
        }
        
        // Create content based on type
        const contentDiv = document.createElement('div');
        contentDiv.className = 'hud-pipeline';
        
        switch (section.type) {
            case 'text':
                contentDiv.appendChild(this.createTextContent(section.data));
                break;
            case 'keyvalue':
                contentDiv.appendChild(this.createKeyValueContent(section.data));
                break;
            case 'image':
                contentDiv.appendChild(this.createImageContent(section.data));
                break;
            case 'video':
                contentDiv.appendChild(this.createVideoContent(section.data));
                break;
            case 'youtube':
                contentDiv.appendChild(this.createYoutubeContent(section.data));
                break;
            case 'chart':
                contentDiv.appendChild(this.createChartContent(section.data, index));
                break;
            case 'list':
                contentDiv.appendChild(this.createListContent(section.data));
                break;
            case 'table':
                contentDiv.appendChild(this.createTableContent(section.data));
                break;
            case 'html':
                contentDiv.innerHTML = section.data.content;
                break;
            default:
                contentDiv.textContent = 'Unsupported content type';
        }
        
        sectionDiv.appendChild(contentDiv);
        return sectionDiv;
    }

    createTextContent(data) {
        const div = document.createElement('div');
        div.className = 'hud-text-content';
        div.textContent = data.text || data.content || '';
        return div;
    }

    createKeyValueContent(data) {
        const container = document.createElement('div');
        container.className = 'hud-keyvalue-container';
        
        const items = data.items || [];
        items.forEach(item => {
            const itemDiv = document.createElement('div');
            itemDiv.className = 'hud-keyvalue-item';
            
            const label = document.createElement('span');
            label.className = 'hud-keyvalue-label';
            label.textContent = item.key + ':';
            
            const value = document.createElement('span');
            value.className = 'hud-keyvalue-value';
            value.textContent = item.value;
            
            itemDiv.appendChild(label);
            itemDiv.appendChild(value);
            container.appendChild(itemDiv);
        });
        
        return container;
    }

    createImageContent(data) {
        const img = document.createElement('img');
        img.className = 'hud-image';
        img.src = data.url || data.src;
        img.alt = data.alt || 'HUD Image';
        
        if (data.caption) {
            const container = document.createElement('div');
            container.className = 'hud-image-container';
            
            const caption = document.createElement('div');
            caption.className = 'hud-image-caption';
            caption.textContent = data.caption;
            
            container.appendChild(img);
            container.appendChild(caption);
            return container;
        }
        
        return img;
    }

    createVideoContent(data) {
        const video = document.createElement('video');
        video.className = 'hud-video';
        video.src = data.url || data.src;
        video.controls = data.controls !== false;
        video.autoplay = data.autoplay || false;
        video.loop = data.loop || false;
        video.muted = data.muted || false;
        
        return video;
    }

    createYoutubeContent(data) {
        const iframe = document.createElement('iframe');
        iframe.className = 'hud-youtube';
        
        // Extract video ID from URL if needed
        let videoId = data.videoId || data.id;
        if (!videoId && data.url) {
            const match = data.url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&]+)/);
            videoId = match ? match[1] : null;
        }
        
        if (videoId) {
            iframe.src = `https://www.youtube.com/embed/${videoId}`;
            iframe.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture';
            iframe.allowFullscreen = true;
        } else {
            iframe.textContent = 'Invalid YouTube URL';
        }
        
        return iframe;
    }

    createChartContent(data, index) {
        const canvas = document.createElement('canvas');
        canvas.id = `hud-chart-${index}`;
        canvas.className = 'hud-chart';
        
        // Load Chart.js if not already loaded
        if (typeof Chart === 'undefined') {
            const script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js';
            script.onload = () => this.renderChart(canvas, data);
            document.head.appendChild(script);
        } else {
            setTimeout(() => this.renderChart(canvas, data), 0);
        }
        
        return canvas;
    }

    renderChart(canvas, data) {
        if (typeof Chart === 'undefined') return;
        
        new Chart(canvas, {
            type: data.chartType || 'line',
            data: data.chartData || {},
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        labels: {
                            color: '#0ff'
                        }
                    }
                },
                scales: {
                    y: {
                        ticks: { color: '#0ff' },
                        grid: { color: 'rgba(0, 255, 255, 0.1)' }
                    },
                    x: {
                        ticks: { color: '#0ff' },
                        grid: { color: 'rgba(0, 255, 255, 0.1)' }
                    }
                },
                ...data.options
            }
        });
    }

    createListContent(data) {
        const ul = document.createElement('ul');
        ul.className = 'hud-list';
        
        const items = data.items || [];
        items.forEach(item => {
            const li = document.createElement('li');
            li.className = 'hud-list-item';
            
            if (typeof item === 'object') {
                // Create title/label
                const titleSpan = document.createElement('strong');
                titleSpan.textContent = (item.label || item.title) + ': ';
                li.appendChild(titleSpan);
                
                // Create value/text
                const valueSpan = document.createElement('span');
                valueSpan.textContent = item.value || item.text || '';
                li.appendChild(valueSpan);
                
                // Add URL link if available
                if (item.url) {
                    const linkDiv = document.createElement('div');
                    linkDiv.className = 'hud-list-link';
                    const link = document.createElement('a');
                    link.href = item.url;
                    link.target = '_blank';
                    link.rel = 'noopener noreferrer';
                    link.textContent = item.url;
                    linkDiv.appendChild(link);
                    li.appendChild(linkDiv);
                }
            } else {
                li.textContent = item;
            }
            
            ul.appendChild(li);
        });
        
        return ul;
    }

    createTableContent(data) {
        const table = document.createElement('table');
        table.className = 'hud-table';
        
        // Create table header
        if (data.headers && data.headers.length > 0) {
            const thead = document.createElement('thead');
            const headerRow = document.createElement('tr');
            
            data.headers.forEach(header => {
                const th = document.createElement('th');
                th.className = 'hud-table-header';
                th.textContent = header;
                headerRow.appendChild(th);
            });
            
            thead.appendChild(headerRow);
            table.appendChild(thead);
        }
        
        // Create table body
        const tbody = document.createElement('tbody');
        const rows = data.rows || [];
        
        rows.forEach((row, index) => {
            const tr = document.createElement('tr');
            tr.className = 'hud-table-row';
            
            // Check if this row should be highlighted (next event)
            let isHighlighted = false;
            
            // If row is an object, use headers to get values in order
            if (typeof row === 'object' && !Array.isArray(row)) {
                // Check for highlight flag
                if (row._highlight === true) {
                    isHighlighted = true;
                    tr.classList.add('hud-table-row-highlight');
                }
                
                data.headers.forEach(header => {
                    const td = document.createElement('td');
                    td.className = 'hud-table-cell';
                    td.textContent = row[header] || '';
                    tr.appendChild(td);
                });
            } 
            // If row is an array, just use the values
            else if (Array.isArray(row)) {
                row.forEach(cell => {
                    const td = document.createElement('td');
                    td.className = 'hud-table-cell';
                    td.textContent = cell;
                    tr.appendChild(td);
                });
            }
            
            tbody.appendChild(tr);
        });
        
        table.appendChild(tbody);
        return table;
    }

    /**
     * Update a specific section with new data
     * @param {number} index - Section index
     * @param {Object} newData - New section data
     */
    updateSection(index, newData) {
        const sectionElement = document.getElementById(`hud-section-${index}`);
        if (!sectionElement) return;
        
        const newSection = this.createSection(newData, index);
        sectionElement.replaceWith(newSection);
        this.sections[index] = newData;
    }

    show() {
        if (!this.isVisible) {
            this.hudContainer.classList.remove('hidden');
            this.animateIn();
            this.isVisible = true;
        }
    }

    hide() {
        if (this.isVisible) {
            this.animateOut();
            setTimeout(() => {
                this.hudContainer.classList.add('hidden');
            }, 300);
            this.isVisible = false;
        }
    }

    toggle() {
        if (this.isVisible) {
            this.hide();
        } else {
            this.show();
        }
    }

    animateIn() {
        this.hudContainer.style.opacity = '0';
        this.hudContainer.style.transform = 'scale(0.95) translateY(-20px)';
        
        setTimeout(() => {
            this.hudContainer.style.transition = 'all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)';
            this.hudContainer.style.opacity = '1';
            this.hudContainer.style.transform = 'scale(1) translateY(0)';
        }, 10);
    }

    animateOut() {
        this.hudContainer.style.transition = 'all 0.3s ease-out';
        this.hudContainer.style.opacity = '0';
        this.hudContainer.style.transform = 'scale(0.95) translateY(-20px)';
    }

    startDrag(e) {
        if (e.target.closest('.hud-close')) return;
        
        this.isDragging = true;
        const rect = this.hudContainer.getBoundingClientRect();
        this.dragOffset.x = e.clientX - rect.left;
        this.dragOffset.y = e.clientY - rect.top;
        
        this.hudContainer.style.transition = 'none';
        document.body.style.userSelect = 'none';
    }

    drag(e) {
        if (!this.isDragging) return;
        
        let newLeft = e.clientX - this.dragOffset.x;
        let newTop = e.clientY - this.dragOffset.y;
        
        // Boundary checks
        const maxLeft = window.innerWidth - this.hudContainer.offsetWidth;
        const maxTop = window.innerHeight - this.hudContainer.offsetHeight;
        
        newLeft = Math.max(0, Math.min(newLeft, maxLeft));
        newTop = Math.max(0, Math.min(newTop, maxTop));
        
        this.hudContainer.style.left = newLeft + 'px';
        this.hudContainer.style.top = newTop + 'px';
    }

    stopDrag() {
        if (this.isDragging) {
            this.isDragging = false;
            document.body.style.userSelect = '';
        }
    }

    updateSystemStatus(status) {
        const audioStatus = document.getElementById('audio-status');
        const vizStatus = document.getElementById('viz-status');
        const connStatus = document.getElementById('connection-status');
        
        if (status.audio) audioStatus.textContent = status.audio;
        if (status.visualizer) vizStatus.textContent = status.visualizer;
        if (status.connection) connStatus.textContent = status.connection;
    }
}

// Initialize HUD when DOM is ready
let auraHUD = null;

function initHUD() {
    auraHUD = new HUD();
    
    // Expose globally
    window.auraHUD = auraHUD;
    
    console.log("HUD module loaded. Access via window.auraHUD");
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initHUD);
} else {
    initHUD();
}

export default HUD;
