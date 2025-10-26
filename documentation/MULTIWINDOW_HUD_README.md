# 🪟 Multi-Window HUD System - AURA

## ✨ Features Implemented

### **Multiple Independent Windows**
- ✅ Create unlimited HUD windows simultaneously
- ✅ Each window displays different tool data (weather, calendar, to-do, search, etc.)
- ✅ Windows cascade automatically on creation (30px offset)
- ✅ Independent window management (close, minimize, drag)

### **Window Management**
- ✅ **Drag to Move**: Click and drag header to reposition windows
- ✅ **Click to Focus**: Click header to bring window to front (highest z-index)
- ✅ **Minimize**: Minimize windows to bottom-right container
- ✅ **Restore**: Click minimized item to restore window
- ✅ **Close**: Close windows individually or all at once
- ✅ **Z-Index Management**: Automatic stacking order management

### **Minimized Window Container**
- ✅ Bottom-right container for minimized windows
- ✅ Shows window title and icon
- ✅ Hover effects with glow
- ✅ Click to restore to original position
- ✅ Slide-in animation when minimizing

### **Visual Enhancements**
- ✅ Glass-morphism design with backdrop blur
- ✅ Cyan glow effects on hover
- ✅ Smooth animations (300ms cubic-bezier)
- ✅ Shadow effects for depth
- ✅ Professional window chrome (header with title + controls)

## 🎨 UI Components

### **Window Structure**
```
┌─────────────────────────────────────┐
│ [Title]              [−] [×]        │ ← Header (draggable)
├─────────────────────────────────────┤
│                                     │
│    HUD Content (scrollable)         │ ← Content area
│                                     │
│                                     │
└─────────────────────────────────────┘
```

### **Minimized Container (Bottom-Right)**
```
                         ┌──────────────┐
                         │ [□] Weather  │
                         ├──────────────┤
                         │ [□] To-Do    │
                         ├──────────────┤
                         │ [□] Calendar │
                         └──────────────┘
```

## 🔧 API Reference

### **Creating Windows**

```javascript
// Create a new window
const windowId = window.auraHUD.createWindow(title, data, options);

// Parameters:
// - title: Window title (string)
// - data: HUD data object with sections array
// - options: {
//     width: 400,    // Window width in pixels
//     height: 500,   // Window height in pixels
//     x: 100,        // Initial X position
//     y: 100,        // Initial Y position
//     minWidth: 300, // Minimum width
//     minHeight: 200 // Minimum height
//   }

// Example:
const todoWindowId = window.auraHUD.createWindow("To-Do List", {
    sections: [
        {
            title: "Task Statistics",
            type: "keyvalue",
            data: { items: [...] }
        },
        {
            title: "Tasks",
            type: "table",
            data: { headers: [...], rows: [...] }
        }
    ]
}, {
    width: 500,
    height: 600,
    x: 150,
    y: 150
});
```

### **Window Management**

```javascript
// Minimize window
window.auraHUD.minimizeWindow(windowId);

// Restore minimized window
window.auraHUD.restoreWindow(windowId);

// Close window
window.auraHUD.closeWindow(windowId);

// Bring window to front
window.auraHUD.bringToFront(windowId);

// Close all windows
window.auraHUD.closeAllWindows();

// Get all open windows
const openWindows = window.auraHUD.getOpenWindows();

// Get all minimized windows
const minimizedWindows = window.auraHUD.getMinimizedWindows();
```

### **Backward Compatibility**

```javascript
// Old single-window method (creates new window automatically)
window.auraHUD.show(data);

// Render content (creates new window)
window.auraHUD.renderContent(data);
```

## 🎯 Usage Examples

### **1. Weather + To-Do + Calendar**
```javascript
// Create weather window
window.auraHUD.createWindow("Weather", weatherData);

// Create to-do window
window.auraHUD.createWindow("To-Do", todoData);

// Create calendar window
window.auraHUD.createWindow("Calendar", calendarData);
```

### **2. Minimize/Restore Workflow**
```javascript
// Create window
const id = window.auraHUD.createWindow("Tasks", data);

// Minimize when not needed
window.auraHUD.minimizeWindow(id);

// User clicks minimized item → automatically restores
```

### **3. Auto-Generated Titles**
```javascript
// System automatically extracts title from data
window.auraHUD.renderContent({
    sections: [
        { title: "Weather - Tokyo", type: "keyvalue", ... }
    ]
});
// Creates window titled "Weather"
```

## 🎨 Customization

### **Window Positions**
```javascript
// Manual positioning
window.auraHUD.createWindow("Custom", data, {
    x: 500,    // Right side
    y: 100,    // Top
    width: 350,
    height: 450
});

// Auto-cascade (default)
// Automatically offsets by 30px for each new window
```

### **Styling**
All styles in `frontend/css/style.css`:
- `.aura-hud-window` - Main window container
- `.hud-header` - Window header (draggable)
- `.hud-title` - Window title text
- `.hud-btn` - Control buttons (minimize, close)
- `.hud-minimized-container` - Minimized windows container
- `.hud-minimized-item` - Individual minimized item

## 🔄 Integration with AURA

### **Automatic Window Creation**
When AURA AI calls tools (weather, calendar, to-do, search), the backend returns `hud_sections`. The frontend automatically creates a new window:

```javascript
// In ui_main.js
if (data.hud_sections && data.hud_sections.length > 0) {
    window.auraHUD.renderContent({ sections: data.hud_sections });
}
```

### **Smart Title Detection**
System automatically generates appropriate titles:
- Weather data → "Weather"
- Calendar data → "Calendar"
- To-Do data → "To-Do List"
- Search data → "Search Results"
- Generic → "AURA HUD"

## 🧪 Testing

### **Test Page**
Open `frontend/test_multiwindow.html` in browser

### **Test Functions**
```javascript
// Individual windows
testWeatherWindow();
testTodoWindow();
testCalendarWindow();
testSearchWindow();

// Multiple at once
testMultiple();  // Creates 3 windows

// Cleanup
closeAll();      // Closes all windows
```

### **Manual Testing Checklist**
- [x] Create multiple windows
- [x] Drag windows to different positions
- [x] Click header to bring to front
- [x] Minimize window (moves to bottom-right)
- [x] Click minimized item to restore
- [x] Close individual windows
- [x] Close all windows at once
- [x] Verify z-index stacking works correctly
- [x] Test scrolling in window content
- [x] Verify animations are smooth

## 🚀 Performance

- **Lightweight**: Each window is a simple DOM element
- **Efficient**: Only active windows consume resources
- **No Conflicts**: Each window is completely independent
- **Z-Index Management**: Automatic stacking without manual tracking
- **Memory**: Windows properly cleaned up on close

## 📊 Window Lifecycle

```
Creation → Show (animated) → Active
   ↓
Minimize → Stored in bottom-right → Click → Restore → Active
   ↓
Close → Animated out → Removed from DOM → Cleanup
```

## 🎯 Key Improvements Over Single Window

| Feature | Old (Single) | New (Multi-Window) |
|---------|-------------|-------------------|
| Windows | 1 (replaced) | Unlimited (independent) |
| History | Lost on new tool | Preserved in windows |
| Organization | N/A | Minimize unused windows |
| Focus | Always visible | Click to bring to front |
| Workflow | Linear | Parallel (compare data) |
| UX | Basic | Professional multi-window |

## 🔮 Future Enhancements (Optional)

- [ ] Window resizing (drag borders)
- [ ] Snap to edges/corners
- [ ] Window grouping/tabs
- [ ] Save window positions
- [ ] Keyboard shortcuts (Alt+Tab to cycle)
- [ ] Window thumbnails on minimize
- [ ] Maximize/fullscreen mode
- [ ] Window transparency slider
- [ ] Custom window themes per type

---

**🎊 Multi-Window HUD System Complete!**

Test it now: Open `frontend/test_multiwindow.html` or use AURA with multiple tool queries!
