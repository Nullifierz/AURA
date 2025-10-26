// hud.js - Dynamic Head Up Display for AURA (Multi-Window Enhanced)

class HUD {
    constructor() {
        this.windows = new Map(); // Store multiple HUD windows: windowId -> window object
        this.nextWindowId = 1;
        this.highestZIndex = 1000; // Track highest z-index for window stacking
        this.minimizedContainer = null; // Container for minimized windows
        
        this.init();
    }

    init() {
        // Create minimized windows container
        this.createMinimizedContainer();
        
        console.log("Multi-Window Dynamic HUD initialized");
    }

    createMinimizedContainer() {
        // Create container for minimized windows (bottom-right)
        this.minimizedContainer = document.createElement('div');
        this.minimizedContainer.id = 'hud-minimized-container';
        this.minimizedContainer.className = 'hud-minimized-container';
        document.body.appendChild(this.minimizedContainer);
    }

    /**
     * Create a new HUD window
     * @param {string} title - Window title
     * @param {Object} data - Window data with sections
     * @param {Object} options - Window options (position, size, etc.)
     * @returns {string} Window ID
     */
    createWindow(title = "AURA HUD", data = null, options = {}) {
        const windowId = `hud-window-${this.nextWindowId++}`;
        
        // Calculate spawn position (top-left or top-right, avoiding center)
        const windowCount = this.windows.size;
        const spawnRight = windowCount % 2 === 0; // Alternate between left and right
        
        // Default options
        const defaultOptions = {
            minWidth: 400,
            maxWidth: 800,
            maxHeight: 600, // Use maxHeight instead of fixed height
            x: spawnRight ? window.innerWidth - 850 : 50, // Right side or left side (adjusted for max width)
            y: 50 + (Math.floor(windowCount / 2) * 30), // Stack vertically
            minHeight: 200
        };
        
        const opts = { ...defaultOptions, ...options };
        
        // Create window element
        const windowElement = document.createElement('div');
        windowElement.id = windowId;
        windowElement.className = 'aura-hud-window';
        windowElement.style.cssText = `
            left: ${opts.x}px;
            top: ${opts.y}px;
            min-width: ${opts.minWidth}px;
            max-width: ${opts.maxWidth}px;
            width: fit-content;
            max-height: ${opts.maxHeight}px;
            z-index: ${++this.highestZIndex};
        `;
        
        windowElement.innerHTML = `
            <div class="hud-header" data-window-id="${windowId}">
                <div class="hud-title">${title}</div>
                <div class="hud-controls">
                    <button class="hud-btn hud-minimize" title="Minimize">
                        <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" fill="currentColor" viewBox="0 0 16 16">
                            <path d="M4 8a.5.5 0 0 1 .5-.5h7a.5.5 0 0 1 0 1h-7A.5.5 0 0 1 4 8z"/>
                        </svg>
                    </button>
                    <button class="hud-btn hud-close" title="Close">
                        <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" fill="currentColor" viewBox="0 0 16 16">
                            <path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"/>
                        </svg>
                    </button>
                </div>
            </div>
            
            <div class="hud-content" id="${windowId}-content">
                <div class="hud-loading"></div>
            </div>
        `;
        
        document.body.appendChild(windowElement);
        
        // Store window data
        const windowData = {
            id: windowId,
            element: windowElement,
            title: title,
            isMinimized: false,
            isDragging: false,
            dragOffset: { x: 0, y: 0 },
            sections: [],
            position: { x: opts.x, y: opts.y },
            size: { width: opts.width, height: opts.height }
        };
        
        this.windows.set(windowId, windowData);
        
        // Setup event listeners for this window
        this.setupWindowEventListeners(windowId);
        
        // Render content if provided
        if (data) {
            this._renderWindowContent(windowId, data);
        }
        
        // Animate in
        this.animateWindowIn(windowId);
        
        return windowId;
    }

    setupWindowEventListeners(windowId) {
        const windowData = this.windows.get(windowId);
        if (!windowData) return;
        
        const windowElement = windowData.element;
        const header = windowElement.querySelector('.hud-header');
        const minimizeBtn = windowElement.querySelector('.hud-minimize');
        const closeBtn = windowElement.querySelector('.hud-close');
        
        // Click header to bring to front
        header.addEventListener('click', (e) => {
            if (!e.target.closest('.hud-btn')) {
                this.bringToFront(windowId);
            }
        });
        
        // Minimize button
        minimizeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.minimizeWindow(windowId);
        });
        
        // Close button
        closeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.closeWindow(windowId);
        });
        
        // Dragging
        header.addEventListener('mousedown', (e) => {
            if (!e.target.closest('.hud-btn')) {
                this.startDrag(windowId, e);
            }
        });
        
        // Global mouse events for dragging
        document.addEventListener('mousemove', (e) => this.drag(windowId, e));
        document.addEventListener('mouseup', () => this.stopDrag(windowId));
    }

    /**
     * Bring window to front (highest z-index)
     */
    bringToFront(windowId) {
        const windowData = this.windows.get(windowId);
        if (!windowData || windowData.isMinimized) return;
        
        windowData.element.style.zIndex = ++this.highestZIndex;
    }

    /**
     * Minimize window to bottom-right container
     */
    minimizeWindow(windowId) {
        const windowData = this.windows.get(windowId);
        if (!windowData || windowData.isMinimized) return;
        
        const windowElement = windowData.element;
        
        // Save current position
        windowData.position = {
            x: parseInt(windowElement.style.left),
            y: parseInt(windowElement.style.top)
        };
        
        // Create minimized representation
        const minimizedItem = document.createElement('div');
        minimizedItem.className = 'hud-minimized-item';
        minimizedItem.dataset.windowId = windowId;
        minimizedItem.innerHTML = `
            <div class="minimized-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                    <path d="M0 2a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V2z"/>
                </svg>
            </div>
            <div class="minimized-title">${windowData.title}</div>
        `;
        
        // Click to restore
        minimizedItem.addEventListener('click', () => this.restoreWindow(windowId));
        
        this.minimizedContainer.appendChild(minimizedItem);
        windowData.minimizedElement = minimizedItem;
        
        // Hide window with animation
        windowElement.style.transition = 'all 0.3s ease-out';
        windowElement.style.opacity = '0';
        windowElement.style.transform = 'scale(0.8)';
        
        setTimeout(() => {
            windowElement.style.display = 'none';
            windowData.isMinimized = true;
        }, 300);
    }

    /**
     * Restore minimized window
     */
    restoreWindow(windowId) {
        const windowData = this.windows.get(windowId);
        if (!windowData || !windowData.isMinimized) return;
        
        const windowElement = windowData.element;
        
        // Remove from minimized container
        if (windowData.minimizedElement) {
            windowData.minimizedElement.remove();
            windowData.minimizedElement = null;
        }
        
        // Restore window
        windowElement.style.display = 'block';
        windowElement.style.left = windowData.position.x + 'px';
        windowElement.style.top = windowData.position.y + 'px';
        
        // Animate in
        setTimeout(() => {
            windowElement.style.transition = 'all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)';
            windowElement.style.opacity = '1';
            windowElement.style.transform = 'scale(1)';
            windowData.isMinimized = false;
            
            // Bring to front
            this.bringToFront(windowId);
        }, 10);
    }

    /**
     * Close window permanently
     */
    closeWindow(windowId) {
        const windowData = this.windows.get(windowId);
        if (!windowData) return;
        
        const windowElement = windowData.element;
        
        // Remove minimized element if exists
        if (windowData.minimizedElement) {
            windowData.minimizedElement.remove();
        }
        
        // Animate out
        windowElement.style.transition = 'all 0.3s ease-out';
        windowElement.style.opacity = '0';
        windowElement.style.transform = 'scale(0.8)';
        
        setTimeout(() => {
            windowElement.remove();
            this.windows.delete(windowId);
        }, 300);
    }

    startDrag(windowId, e) {
        const windowData = this.windows.get(windowId);
        if (!windowData || windowData.isMinimized) return;
        
        windowData.isDragging = true;
        const rect = windowData.element.getBoundingClientRect();
        windowData.dragOffset = {
            x: e.clientX - rect.left,
            y: e.clientY - rect.top
        };
        
        windowData.element.style.transition = 'none';
        document.body.style.userSelect = 'none';
        
        // Bring to front when dragging starts
        this.bringToFront(windowId);
    }

    drag(windowId, e) {
        const windowData = this.windows.get(windowId);
        if (!windowData || !windowData.isDragging) return;
        
        let newLeft = e.clientX - windowData.dragOffset.x;
        let newTop = e.clientY - windowData.dragOffset.y;
        
        // Boundary checks
        const maxLeft = window.innerWidth - windowData.element.offsetWidth;
        const maxTop = window.innerHeight - windowData.element.offsetHeight;
        
        newLeft = Math.max(0, Math.min(newLeft, maxLeft));
        newTop = Math.max(0, Math.min(newTop, maxTop));
        
        windowData.element.style.left = newLeft + 'px';
        windowData.element.style.top = newTop + 'px';
    }

    stopDrag(windowId) {
        const windowData = this.windows.get(windowId);
        if (!windowData) return;
        
        if (windowData.isDragging) {
            windowData.isDragging = false;
            document.body.style.userSelect = '';
        }
    }

    /**
     * Render dynamic content based on JSON structure (internal method)
     * @param {string} windowId - Window ID
     * @param {Object} data - JSON data with sections array
     */
    _renderWindowContent(windowId, data) {
        const windowData = this.windows.get(windowId);
        if (!windowData) return;
        
        const contentContainer = windowData.element.querySelector('.hud-content');
        contentContainer.innerHTML = '';
        
        if (!data.sections || data.sections.length === 0) {
            contentContainer.innerHTML = '<div class="hud-empty">No data to display</div>';
            return;
        }
        
        windowData.sections = data.sections;
        
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
        
        // Don't add section title - it's already in the window header
        
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
     * Animate window in
     */
    animateWindowIn(windowId) {
        const windowData = this.windows.get(windowId);
        if (!windowData) return;
        
        const windowElement = windowData.element;
        windowElement.style.opacity = '0';
        windowElement.style.transform = 'scale(0.9)';
        
        setTimeout(() => {
            windowElement.style.transition = 'all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)';
            windowElement.style.opacity = '1';
            windowElement.style.transform = 'scale(1)';
        }, 10);
    }

    /**
     * Show HUD - For backward compatibility, creates a new window
     * @param {Object} data - Optional data to display
     */
    show(data = null) {
        // Create a new window with data
        const title = this._getTitleFromData(data);
        return this.createWindow(title, data);
    }

    /**
     * Render content - For backward compatibility with ui_main.js
     * Creates a new window for each render call
     */
    renderContent(data) {
        const title = this._getTitleFromData(data);
        return this.createWindow(title, data);
    }

    /**
     * Extract title from data sections
     */
    _getTitleFromData(data) {
        if (!data || !data.sections || data.sections.length === 0) {
            return "AURA HUD";
        }
        
        // Use first section title or derive from type
        const firstSection = data.sections[0];
        if (firstSection.title) {
            return firstSection.title;
        }
        
        // Generate title based on content type
        const typeNames = {
            'weather': 'Weather',
            'calendar': 'Calendar',
            'table': 'To-Do List',
            'search': 'Search Results',
            'keyvalue': 'Information'
        };
        
        for (const [key, name] of Object.entries(typeNames)) {
            if (firstSection.type === 'table' && firstSection.title && firstSection.title.includes('To-Do')) {
                return 'To-Do List';
            }
            if (firstSection.title && firstSection.title.toLowerCase().includes(key)) {
                return name;
            }
        }
        
        return "AURA HUD";
    }

    /**
     * Get all open windows
     */
    getOpenWindows() {
        return Array.from(this.windows.values()).filter(w => !w.isMinimized);
    }

    /**
     * Get all minimized windows
     */
    getMinimizedWindows() {
        return Array.from(this.windows.values()).filter(w => w.isMinimized);
    }

    /**
     * Close all windows
     */
    closeAllWindows() {
        const windowIds = Array.from(this.windows.keys());
        windowIds.forEach(id => this.closeWindow(id));
    }
}

// Initialize HUD when DOM is ready
let auraHUD = null;

function initHUD() {
    auraHUD = new HUD();
    
    // Expose globally
    window.auraHUD = auraHUD;
    
    console.log("Multi-Window HUD module loaded. Access via window.auraHUD");
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initHUD);
} else {
    initHUD();
}

export default HUD;
