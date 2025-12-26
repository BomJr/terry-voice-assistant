// ═══════════════════════════════════════════════════════════
// TERRY WEB UI - JavaScript
// Real-time interactive interface
// ═══════════════════════════════════════════════════════════

class TerryUI {
    constructor() {
        this.ws = null;
        this.history = [];
        this.chatMessages = [];
        this.isRecording = false;

        this.init();
    }

    // ═══════════════════════════════════════════════════════════
    // INITIALIZATION
    // ═══════════════════════════════════════════════════════════

    init() {
        this.setupEventListeners();
        this.setupWebSocket();
        this.loadStats();
        this.loadSettings();
        this.startStatusCheck();
    }

    setupEventListeners() {
        // Theme toggle
        document.getElementById('themeToggle').addEventListener('click', () => {
            this.toggleTheme();
        });

        document.getElementById('darkModeToggle').addEventListener('change', (e) => {
            if (e.target.checked) {
                document.body.classList.add('dark-theme');
                localStorage.setItem('theme', 'dark');
            } else {
                document.body.classList.remove('dark-theme');
                localStorage.setItem('theme', 'light');
            }
        });

        // Silent mode toggle
        document.getElementById('silentToggle').addEventListener('click', () => {
            this.toggleSilentMode();
        });

        document.getElementById('silentModeToggle').addEventListener('change', () => {
            this.toggleSilentMode();
        });

        // Voice button
        document.getElementById('voiceBtn').addEventListener('click', () => {
            this.toggleVoiceRecording();
        });

        // Command input
        document.getElementById('sendBtn').addEventListener('click', () => {
            this.sendCommand();
        });

        document.getElementById('commandInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendCommand();
            }
        });

        // Tabs
        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                this.switchTab(e.target.closest('.tab').dataset.tab);
            });
        });

        // Notes
        document.getElementById('addNoteBtn').addEventListener('click', () => {
            this.showNoteModal();
        });

        document.getElementById('closeNoteModal').addEventListener('click', () => {
            this.hideNoteModal();
        });

        document.getElementById('cancelNote').addEventListener('click', () => {
            this.hideNoteModal();
        });

        document.getElementById('saveNote').addEventListener('click', () => {
            this.saveNote();
        });

        // Clear history
        document.getElementById('clearHistory').addEventListener('click', () => {
            this.clearHistory();
        });

        // Chat interface
        document.getElementById('chatSendBtn').addEventListener('click', () => {
            this.sendChatMessage();
        });

        document.getElementById('chatInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendChatMessage();
            }
        });

        document.getElementById('clearChat').addEventListener('click', () => {
            this.clearChat();
        });
    }

    // ═══════════════════════════════════════════════════════════
    // WEBSOCKET
    // ═══════════════════════════════════════════════════════════

    setupWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;

        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            console.log('✅ WebSocket connected');
            this.updateStatus('online');
            this.ws.send(JSON.stringify({ type: 'subscribe' }));
        };

        this.ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            this.handleWebSocketMessage(message);
        };

        this.ws.onclose = () => {
            console.log('❌ WebSocket disconnected');
            this.updateStatus('offline');
            // Reconnect after 5 seconds
            setTimeout(() => this.setupWebSocket(), 5000);
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }

    handleWebSocketMessage(message) {
        console.log('📨 WebSocket message:', message);

        switch (message.type) {
            case 'command_executed':
                this.addToHistory(message.data);
                this.loadStats();
                break;

            case 'silent_mode_changed':
                this.updateSilentModeUI(message.data.silent);
                break;

            case 'note_created':
                this.loadNotes();
                this.loadStats();
                this.showToast('Nota guardada correctamente');
                break;

            case 'pong':
                // Keep-alive response
                break;
        }
    }

    // ═══════════════════════════════════════════════════════════
    // UI ACTIONS
    // ═══════════════════════════════════════════════════════════

    toggleTheme() {
        document.body.classList.toggle('dark-theme');
        const isDark = document.body.classList.contains('dark-theme');
        localStorage.setItem('theme', isDark ? 'dark' : 'light');

        const icon = document.querySelector('#themeToggle i');
        icon.className = isDark ? 'fas fa-sun' : 'fas fa-moon';

        document.getElementById('darkModeToggle').checked = isDark;
    }

    async toggleSilentMode() {
        try {
            const response = await fetch('/api/silent-mode', {
                method: 'POST'
            });

            const data = await response.json();
            this.updateSilentModeUI(data.silent);

            this.showToast(data.silent ? 'Modo silencioso activado' : 'Modo silencioso desactivado');
        } catch (error) {
            console.error('Error toggling silent mode:', error);
            this.showToast('Error cambiando modo silencioso', 'error');
        }
    }

    updateSilentModeUI(isSilent) {
        const icon = document.querySelector('#silentToggle i');
        icon.className = isSilent ? 'fas fa-volume-mute' : 'fas fa-volume-up';

        document.getElementById('silentModeToggle').checked = isSilent;
    }

    toggleVoiceRecording() {
        if (this.isRecording) {
            this.stopVoiceRecording();
        } else {
            this.startVoiceRecording();
        }
    }

    startVoiceRecording() {
        const btn = document.getElementById('voiceBtn');
        const status = document.getElementById('voiceStatus');

        // Check for browser support
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            this.showToast('Tu navegador no soporta reconocimiento de voz. Usa Chrome o Edge.', 'error');
            return;
        }

        // Initialize speech recognition
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = new SpeechRecognition();

        this.recognition.lang = 'es-ES';
        this.recognition.continuous = false;
        this.recognition.interimResults = true;
        this.recognition.maxAlternatives = 1;

        this.recognition.onstart = () => {
            this.isRecording = true;
            btn.classList.add('recording');
            btn.innerHTML = '<i class="fas fa-stop"></i>';
            status.innerHTML = '<p class="recording-text">🔴 Escuchando... di algo</p>';
        };

        this.recognition.onresult = (event) => {
            const transcript = Array.from(event.results)
                .map(result => result[0])
                .map(result => result.transcript)
                .join('');

            status.innerHTML = `<p class="recording-text">📝 "${transcript}"</p>`;

            // If final result
            if (event.results[0].isFinal) {
                this.processVoiceCommand(transcript);
            }
        };

        this.recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            this.stopVoiceRecording();

            if (event.error === 'no-speech') {
                this.showToast('No se detectó voz. Intenta de nuevo.', 'error');
            } else if (event.error === 'not-allowed') {
                this.showToast('Permiso de micrófono denegado. Permite acceso al micrófono.', 'error');
            } else {
                this.showToast(`Error: ${event.error}`, 'error');
            }
        };

        this.recognition.onend = () => {
            this.stopVoiceRecording();
        };

        // Start listening
        try {
            this.recognition.start();
        } catch (error) {
            console.error('Error starting recognition:', error);
            this.showToast('Error al iniciar el micrófono', 'error');
        }
    }

    stopVoiceRecording() {
        const btn = document.getElementById('voiceBtn');
        const status = document.getElementById('voiceStatus');

        this.isRecording = false;
        btn.classList.remove('recording');
        btn.innerHTML = '<i class="fas fa-microphone"></i>';
        status.innerHTML = '<p>Di "Terry" para comenzar</p>';

        if (this.recognition) {
            try {
                this.recognition.stop();
            } catch (error) {
                console.error('Error stopping recognition:', error);
            }
        }
    }

    async processVoiceCommand(transcript) {
        console.log('🎤 Voice command:', transcript);

        // Remove "terry" or "oye terry" from the beginning
        let command = transcript.toLowerCase()
            .replace(/^(terry|oye terry|hey terry)\s*/i, '')
            .trim();

        if (!command) {
            this.showToast('Comando vacío. Di "Terry" seguido de un comando.', 'error');
            return;
        }

        // Show in input field
        document.getElementById('commandInput').value = command;
        document.getElementById('chatInput').value = command;

        // Check which tab is active and send accordingly
        const activeTab = document.querySelector('.tab.active').dataset.tab;

        if (activeTab === 'chat') {
            // If chat tab is active, send to chat
            await this.sendChatMessage();
        } else {
            // Otherwise, send as command
            await this.sendCommand(command);
        }
    }

    async sendCommand(voiceCommand = null) {
        const input = document.getElementById('commandInput');
        const command = voiceCommand || input.value.trim();

        if (!command) return;

        // Clear input only if not from voice
        if (!voiceCommand) {
            input.value = '';
        }

        // Add to UI immediately
        this.addToHistory({
            command: command,
            response: 'Procesando...',
            timestamp: new Date().toISOString()
        });

        try {
            const response = await fetch('/api/command', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ command })
            });

            const data = await response.json();

            if (data.success) {
                // Update last item in history
                this.history[this.history.length - 1] = data;
                this.renderHistory();
            } else {
                this.showToast('Error ejecutando comando', 'error');
            }
        } catch (error) {
            console.error('Error sending command:', error);
            this.showToast('Error de conexión', 'error');
        }
    }

    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Update panels
        document.querySelectorAll('.tab-panel').forEach(panel => {
            panel.classList.remove('active');
        });
        document.getElementById(`${tabName}Panel`).classList.add('active');

        // Load data for specific tabs
        if (tabName === 'notes') {
            this.loadNotes();
        } else if (tabName === 'macros') {
            this.loadMacros();
        }
    }

    updateStatus(status) {
        const indicator = document.getElementById('statusIndicator');
        const dot = indicator.querySelector('.status-dot');
        const text = indicator.querySelector('.status-text');

        if (status === 'online') {
            dot.style.background = 'var(--success)';
            text.textContent = 'Online';
        } else {
            dot.style.background = 'var(--error)';
            text.textContent = 'Offline';
        }
    }

    showToast(message, type = 'success') {
        const toast = document.getElementById('toast');
        const toastMessage = document.getElementById('toastMessage');

        toastMessage.textContent = message;

        const icon = toast.querySelector('i');
        if (type === 'error') {
            icon.className = 'fas fa-exclamation-circle';
            icon.style.color = 'var(--error)';
        } else {
            icon.className = 'fas fa-check-circle';
            icon.style.color = 'var(--success)';
        }

        toast.classList.add('show');

        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }

    showNoteModal() {
        document.getElementById('noteModal').classList.add('show');
    }

    hideNoteModal() {
        document.getElementById('noteModal').classList.remove('show');
        document.getElementById('noteContent').value = '';
    }

    async saveNote() {
        const content = document.getElementById('noteContent').value.trim();
        const category = document.getElementById('noteCategory').value;
        const priority = parseInt(document.getElementById('notePriority').value);

        if (!content) {
            this.showToast('El contenido de la nota no puede estar vacío', 'error');
            return;
        }

        try {
            const response = await fetch('/api/notes', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ content, category, priority })
            });

            const data = await response.json();

            if (data.success) {
                this.hideNoteModal();
                this.loadNotes();
                this.loadStats();
                this.showToast('Nota guardada correctamente');
            } else {
                this.showToast('Error guardando nota', 'error');
            }
        } catch (error) {
            console.error('Error saving note:', error);
            this.showToast('Error de conexión', 'error');
        }
    }

    // ═══════════════════════════════════════════════════════════
    // CHAT INTERFACE
    // ═══════════════════════════════════════════════════════════

    async sendChatMessage() {
        const input = document.getElementById('chatInput');
        const message = input.value.trim();

        if (!message) return;

        // Add user message to chat
        this.addChatMessage(message, 'user');
        input.value = '';

        // Build conversation context from recent messages (last 6 messages = 3 turns)
        const context = this.buildChatContext();

        // Send to backend
        try {
            const response = await fetch('/api/command', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    command: message,
                    language: 'es',
                    context: context
                })
            });

            const data = await response.json();

            // Add Terry's response to chat
            if (data.response) {
                this.addChatMessage(data.response, 'assistant');
            } else {
                this.addChatMessage('Lo siento, no pude procesar tu mensaje.', 'assistant');
            }

            // Also add to history
            this.addToHistory(message, data.response || 'Sin respuesta');

        } catch (error) {
            console.error('Error sending chat message:', error);
            this.addChatMessage('Error de conexión. Por favor, intenta de nuevo.', 'assistant');
        }
    }

    buildChatContext() {
        // Get last 6 messages (3 exchanges) for context
        const recentMessages = this.chatMessages.slice(-6);

        if (recentMessages.length === 0) {
            return null;
        }

        // Format as conversation history
        const contextLines = recentMessages.map(msg => {
            const role = msg.sender === 'user' ? 'Usuario' : 'Asistente';
            return `${role}: ${msg.text}`;
        });

        return contextLines.join('\n');
    }

    addChatMessage(text, sender) {
        const container = document.getElementById('chatContainer');

        // Remove welcome message if it exists
        const welcome = container.querySelector('.chat-welcome');
        if (welcome) {
            welcome.remove();
        }

        // Create message element
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${sender}`;

        const avatar = document.createElement('div');
        avatar.className = 'chat-avatar';
        avatar.innerHTML = sender === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';

        const bubble = document.createElement('div');
        bubble.className = 'chat-bubble';

        const bubbleText = document.createElement('p');
        bubbleText.className = 'chat-bubble-text';
        bubbleText.textContent = text;

        const bubbleTime = document.createElement('div');
        bubbleTime.className = 'chat-bubble-time';
        const now = new Date();
        bubbleTime.textContent = now.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });

        bubble.appendChild(bubbleText);
        bubble.appendChild(bubbleTime);

        messageDiv.appendChild(avatar);
        messageDiv.appendChild(bubble);

        container.appendChild(messageDiv);

        // Scroll to bottom
        container.scrollTop = container.scrollHeight;

        // Store in chatMessages array
        this.chatMessages.push({ text, sender, timestamp: now });
    }

    clearChat() {
        const container = document.getElementById('chatContainer');
        container.innerHTML = `
            <div class="chat-welcome">
                <i class="fas fa-robot"></i>
                <h4>¡Hola! Soy Terry</h4>
                <p>Escribe un mensaje o usa el micrófono para hablar conmigo</p>
            </div>
        `;
        this.chatMessages = [];
        this.showToast('Chat limpiado');
    }

    // ═══════════════════════════════════════════════════════════
    // DATA LOADING
    // ═══════════════════════════════════════════════════════════

    async loadStats() {
        try {
            const response = await fetch('/api/stats');
            const data = await response.json();

            // Update stat cards
            document.getElementById('notesCount').textContent = data.notes.total || 0;
            document.getElementById('memoryCount').textContent = data.memory.interactions || 0;
            document.getElementById('macrosCount').textContent = data.macros.total || 0;
            document.getElementById('commandsCount').textContent = data.commands.today || 0;

        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }

    async loadNotes() {
        try {
            const response = await fetch('/api/notes?limit=20');
            const data = await response.json();

            const grid = document.getElementById('notesGrid');

            if (data.notes.length === 0) {
                grid.innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-sticky-note"></i>
                        <p>No hay notas guardadas</p>
                    </div>
                `;
                return;
            }

            grid.innerHTML = data.notes.map(note => `
                <div class="note-card">
                    <div class="note-content">${this.escapeHtml(note.content)}</div>
                    <div class="note-meta">
                        <span class="note-category">${note.category || 'general'}</span>
                        <span>${new Date(note.created_at).toLocaleDateString()}</span>
                    </div>
                </div>
            `).join('');

        } catch (error) {
            console.error('Error loading notes:', error);
        }
    }

    async loadMacros() {
        try {
            const response = await fetch('/api/macros');
            const data = await response.json();

            const list = document.getElementById('macrosList');

            if (data.macros.length === 0) {
                list.innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-bolt"></i>
                        <p>No hay macros creados</p>
                    </div>
                `;
                return;
            }

            list.innerHTML = data.macros.map(macro => `
                <div class="history-item">
                    <div class="history-command">
                        <i class="fas fa-bolt"></i> ${this.escapeHtml(macro.name)}
                    </div>
                    <div class="history-response">
                        ${macro.commands ? macro.commands.length : 0} comandos
                    </div>
                    <div class="history-time">
                        Creado: ${macro.created_at ? new Date(macro.created_at).toLocaleString() : 'N/A'}
                    </div>
                </div>
            `).join('');

        } catch (error) {
            console.error('Error loading macros:', error);
        }
    }

    loadSettings() {
        // Load theme
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'dark') {
            document.body.classList.add('dark-theme');
            document.getElementById('darkModeToggle').checked = true;
            document.querySelector('#themeToggle i').className = 'fas fa-sun';
        }
    }

    addToHistory(item) {
        this.history.push(item);

        // Keep only last 50 items
        if (this.history.length > 50) {
            this.history = this.history.slice(-50);
        }

        this.renderHistory();
    }

    renderHistory() {
        const list = document.getElementById('historyList');

        if (this.history.length === 0) {
            list.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-comment-slash"></i>
                    <p>No hay comandos recientes</p>
                </div>
            `;
            return;
        }

        list.innerHTML = this.history.slice().reverse().map(item => `
            <div class="history-item">
                <div class="history-command">
                    <i class="fas fa-terminal"></i> ${this.escapeHtml(item.command)}
                </div>
                <div class="history-response">
                    ${this.escapeHtml(item.response)}
                </div>
                <div class="history-time">
                    ${new Date(item.timestamp).toLocaleString()}
                </div>
            </div>
        `).join('');
    }

    clearHistory() {
        if (confirm('¿Estás seguro de que quieres limpiar el historial?')) {
            this.history = [];
            this.renderHistory();
            this.showToast('Historial limpiado');
        }
    }

    startStatusCheck() {
        // Check status every 30 seconds
        setInterval(async () => {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();

                if (data.status === 'online') {
                    this.updateStatus('online');
                }
            } catch (error) {
                this.updateStatus('offline');
            }
        }, 30000);
    }

    // ═══════════════════════════════════════════════════════════
    // UTILITIES
    // ═══════════════════════════════════════════════════════════

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.terryUI = new TerryUI();
});

// Handle visibility change for WebSocket reconnection
document.addEventListener('visibilitychange', () => {
    if (!document.hidden && window.terryUI && (!window.terryUI.ws || window.terryUI.ws.readyState !== WebSocket.OPEN)) {
        console.log('Page visible, reconnecting WebSocket...');
        window.terryUI.setupWebSocket();
    }
});
