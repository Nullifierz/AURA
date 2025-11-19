// ui_main.js - Connects backend to frontend and feeds audio to visualizer

const API_URL = 'http://localhost:8000';

let currentAudioSource = null;
let isPlaying = false;

// Get the audio context from THREE.js AudioListener
function getAudioContext() {
    if (window.auraVisualizer && window.auraVisualizer.audioListener) {
        const ctx = window.auraVisualizer.audioListener.context;
        console.log("Using THREE.js AudioContext:", ctx.state);
        
        // Resume if suspended
        if (ctx.state === 'suspended') {
            ctx.resume().then(() => {
                console.log("AudioContext resumed");
            });
        }
        
        return ctx;
    } else {
        console.error("THREE.js AudioListener not found!");
        return null;
    }
}

// Function to send query to backend and play audio
async function sendQuery(query) {
    if (!query || query.trim() === '') {
        console.warn("Empty query");
        return;
    }

    try {
        console.log("Sending query:", query);
        
        // Set to processing state
        if (window.auraVisualizer && window.auraVisualizer.setState) {
            window.auraVisualizer.setState('processing');
        }
        
        const response = await fetch(`${API_URL}/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: query })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log("Received response:", data.response);
        
        // Update HUD if sections are available - creates a new window automatically
        if (data.hud_sections && data.hud_sections.length > 0) {
            if (window.auraHUD) {
                console.log("Creating new HUD window with tool data:", data.hud_sections);
                window.auraHUD.renderContent({ sections: data.hud_sections });
            }
        }
        
        // Play the audio with synced text animation
        if (data.base64_audio) {
            await playBase64Audio(data.base64_audio, data.response);
        }
        
        return data;
    } catch (error) {
        console.error("Error sending query:", error);
        // Return to idle on error
        if (window.auraVisualizer && window.auraVisualizer.setState) {
            window.auraVisualizer.setState('idle');
        }
        throw error;
    }
}

// Function to animate text like subtitles
function animateText(element, text, duration) {
    return new Promise((resolve) => {
        element.textContent = '';
        const chars = text.split('');
        const charDelay = duration / chars.length;
        
        let index = 0;
        const interval = setInterval(() => {
            if (index < chars.length) {
                element.textContent += chars[index];
                index++;
            } else {
                clearInterval(interval);
                resolve();
            }
        }, charDelay);
        
        // Store interval for cleanup if needed
        element._textAnimationInterval = interval;
    });
}

// Function to decode and play base64 audio through the visualizer
async function playBase64Audio(base64Audio, responseText = '') {
    try {
        // Get the THREE.js audio context
        const ctx = getAudioContext();
        if (!ctx) {
            throw new Error("Audio context not available. Make sure AudioVisualyser.js loaded first.");
        }
        
        // Stop any currently playing audio
        if (currentAudioSource) {
            try {
                currentAudioSource.stop();
            } catch (e) {
                console.log("No audio to stop");
            }
            currentAudioSource = null;
        }
        
        // Decode base64 to binary
        const binaryString = atob(base64Audio);
        const bytes = new Uint8Array(binaryString.length);
        for (let i = 0; i < binaryString.length; i++) {
            bytes[i] = binaryString.charCodeAt(i);
        }
        
        console.log("Decoded audio bytes:", bytes.length);
        
        // Decode audio data
        const audioBuffer = await ctx.decodeAudioData(bytes.buffer);
        console.log("Audio decoded successfully. Duration:", audioBuffer.duration, "seconds");
        
        // Create audio source
        const source = ctx.createBufferSource();
        source.buffer = audioBuffer;
        
        // Create gain node for volume control
        const gainNode = ctx.createGain();
        gainNode.gain.value = 0.3; // Set volume to 30% (0.0 to 1.0)
        
        // Connect to the THREE.js visualizer if available
        if (window.auraVisualizer && window.auraVisualizer.soundForAnalysis) {
            const threeAudio = window.auraVisualizer.soundForAnalysis;
            
            // Connect: source -> gain -> visualizer
            source.connect(gainNode);
            gainNode.connect(threeAudio.getOutput());
            
            // Also connect to destination so we can hear it
            gainNode.connect(ctx.destination);
            
            console.log("Audio connected to visualizer and speakers at 30% volume");
        } else {
            // Fallback: just connect to speakers
            source.connect(gainNode);
            gainNode.connect(ctx.destination);
            console.log("Audio connected to speakers only at 30% volume");
        }
        
        // Set to speaking state
        if (window.auraVisualizer && window.auraVisualizer.setState) {
            window.auraVisualizer.setState('speaking');
        }
        
        // Start text animation synced with audio
        const responseDiv = document.getElementById('response');
        if (responseDiv && responseText) {
            // Convert duration to milliseconds
            animateText(responseDiv, responseText, audioBuffer.duration * 700);
        }
        
        // Play the audio
        isPlaying = true;
        source.start(0);
        currentAudioSource = source;
        
        // Handle when audio ends
        source.onended = () => {
            console.log("Audio playback finished");
            isPlaying = false;
            currentAudioSource = null;
            
            // Ensure full text is displayed
            if (responseDiv && responseText) {
                responseDiv.textContent = responseText;
            }
            
            // Return to idle state
            if (window.auraVisualizer && window.auraVisualizer.setState) {
                window.auraVisualizer.setState('idle');
            }
        };
        
        console.log("Audio playback started");
        
    } catch (error) {
        console.error("Error playing audio:", error);
        isPlaying = false;
        throw error;
    }
}

// UI Event Handlers
function setupUI() {
    const queryInput = document.getElementById('queryInput');
    const sendBtn = document.getElementById('sendBtn');
    const responseDiv = document.getElementById('response');
    
    if (!queryInput || !sendBtn || !responseDiv) {
        console.warn("UI elements not found");
        return;
    }
    
    async function handleSend() {
        const query = queryInput.value.trim();
        
        if (!query) {
            responseDiv.textContent = "Please enter a query";
            return;
        }
        
        try {
            sendBtn.disabled = true;
            responseDiv.textContent = ''; // Clear previous response
            
            // Resume audio context on first interaction
            const ctx = getAudioContext();
            if (ctx && ctx.state === 'suspended') {
                await ctx.resume();
            }
            
            await sendQuery(query);
            // Response text will be animated by playBase64Audio
            
            // Clear input
            queryInput.value = '';
            
        } catch (error) {
            responseDiv.textContent = `Error: ${error.message}`;
        } finally {
            sendBtn.disabled = false;
        }
    }
    
    // Send on button click
    sendBtn.addEventListener('click', handleSend);
    
    // Send on Enter key
    queryInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleSend();
        }
    });
    console.log("UI initialized");
}

// Initialize UI when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupUI);
} else {
    setupUI();
}

// Expose functions globally for testing
window.auraAPI = {
    sendQuery,
    playBase64Audio,
    getAudioContext,
    getStatus: () => ({
        isPlaying,
        audioContextState: getAudioContext() ? getAudioContext().state : 'not initialized',
        visualizerReady: !!(window.auraVisualizer && window.auraVisualizer.soundForAnalysis)
    })
};

console.log("ui_main.js loaded. API available at window.auraAPI");
console.log("Try: window.auraAPI.sendQuery('Hello AURA')");

// --- WebSocket Integration ---
let socket = null;

function connectWebSocket() {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    // Assuming backend is on localhost:8000
    const wsUrl = `ws://localhost:8000/ws`;
    
    console.log(`Connecting to WebSocket: ${wsUrl}`);
    socket = new WebSocket(wsUrl);

    socket.onopen = function(e) {
        console.log("[WebSocket] Connection established");
    };

    socket.onmessage = function(event) {
        try {
            const data = JSON.parse(event.data);
            console.log("[WebSocket] Message received:", data);
            handleWebSocketMessage(data);
        } catch (e) {
            console.error("[WebSocket] Error parsing message:", e);
        }
    };

    socket.onclose = function(event) {
        if (event.wasClean) {
            console.log(`[WebSocket] Connection closed cleanly, code=${event.code} reason=${event.reason}`);
        } else {
            console.log('[WebSocket] Connection died');
            // Try to reconnect after 5 seconds
            setTimeout(connectWebSocket, 5000);
        }
    };

    socket.onerror = function(error) {
        console.error(`[WebSocket] Error: ${error.message}`);
    };
}

function handleWebSocketMessage(data) {
    // Handle different message types
    switch (data.type) {
        case 'voice_response':
            // Handle voice response (HUD + Text)
            if (data.hud_sections && data.hud_sections.length > 0) {
                if (window.auraHUD) {
                    console.log("Creating new HUD window from voice command:", data.hud_sections);
                    window.auraHUD.renderContent({ sections: data.hud_sections });
                }
            }
            
            // Play audio if available
            if (data.base64_audio) {
                console.log("Received audio from voice command, playing...");
                playBase64Audio(data.base64_audio, data.response);
            } else {
                // Fallback if no audio: just show text
                const responseDiv = document.getElementById('response');
                if (responseDiv && data.response) {
                    responseDiv.innerText = data.response;
                }
            }
            break;
            
        case 'state_change':
            // Update visualizer state
            if (window.auraVisualizer && window.auraVisualizer.setState) {
                // Map backend states to visualizer states
                // backend: listening, processing, speaking, idle
                // visualizer: idle, listening, processing, speaking
                window.auraVisualizer.setState(data.state);
            }
            
            if (data.state === 'listening' && data.wake_word) {
                console.log(`Wake word detected: ${data.wake_word}`);
            }
            break;
            
        case 'error':
            console.error("Backend error:", data.message);
            if (window.auraVisualizer && window.auraVisualizer.setState) {
                window.auraVisualizer.setState('idle');
            }
            break;
            
        default:
            console.log("Unknown message type:", data.type);
    }
}

// Initialize WebSocket connection
connectWebSocket();
