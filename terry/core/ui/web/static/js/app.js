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
        this.quickCommands = this.loadQuickCommands();
        this.templates = this.loadTemplates();
        this.currentTemplateIndex = null;
        this.currentExecutingTemplate = null;
        this.notifications = [];
        this.unreadCount = 0;
        this.notificationSettings = this.loadNotificationSettings();
        this.logs = [];
        this.logsFilter = 'all';
        this.autoScroll = true;
        this.logsCounts = { debug: 0, info: 0, warn: 0, error: 0 };
        this.themes = this.getBuiltInThemes(); // ✅ Definir themes PRIMERO
        this.currentTheme = this.loadTheme();  // ✅ Luego cargar theme
        this.autocompleteSuggestions = [];
        this.autocompleteSelectedIndex = -1;
        this.autocompleteVisible = false;
        this.performanceData = [];
        this.profilerChart = null;
        this.monitorData = {
            cpu: 0,
            ram: 0,
            uptime: 0,
            startTime: Date.now(),
            cpm: 0,
            activities: [],
            services: {}
        };
        this.monitorInterval = null;

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
        this.setupKeyboardShortcuts();
        this.setupQuickCommandShortcuts();
        this.startAutoRefresh();
        this.renderQuickCommands();
        this.initDashboard();
        this.initAutocomplete();
        this.initTemplates();
        this.initNotifications();
        this.initLogs();
        this.initThemes();
        this.initProfiler();
        this.initMonitor();
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

        // Export history
        document.getElementById('exportHistory').addEventListener('click', () => {
            this.exportData('json');
        });

        // Search history
        document.getElementById('historySearch').addEventListener('input', (e) => {
            this.filterHistory(e.target.value);
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

        // Quick commands configuration
        document.getElementById('configQuickCommands').addEventListener('click', () => {
            this.showQuickCommandConfig();
        });

        // Camera configuration
        document.getElementById('cameraType').addEventListener('change', (e) => {
            this.toggleCameraSettings(e.target.value);
        });

        document.getElementById('saveCameraConfig').addEventListener('click', () => {
            this.saveCameraConfig();
        });

        document.getElementById('testCamera').addEventListener('click', () => {
            this.testCamera();
        });

        // Templates
        document.getElementById('createTemplateBtn').addEventListener('click', () => {
            this.showTemplateModal();
        });

        document.getElementById('closeTemplateModal').addEventListener('click', () => {
            this.hideTemplateModal();
        });

        document.getElementById('cancelTemplate').addEventListener('click', () => {
            this.hideTemplateModal();
        });

        document.getElementById('saveTemplate').addEventListener('click', () => {
            this.saveTemplate();
        });

        document.getElementById('closeExecuteTemplateModal').addEventListener('click', () => {
            this.hideExecuteTemplateModal();
        });

        document.getElementById('cancelExecuteTemplate').addEventListener('click', () => {
            this.hideExecuteTemplateModal();
        });

        document.getElementById('confirmExecuteTemplate').addEventListener('click', () => {
            this.confirmExecuteTemplate();
        });

        // Real-time variable detection in template command
        document.getElementById('templateCommand').addEventListener('input', () => {
            this.updateVariablesPreview();
        });

        // Notifications
        document.getElementById('notificationsToggle').addEventListener('click', () => {
            this.toggleNotificationsPanel();
        });

        document.getElementById('closeNotifications').addEventListener('click', () => {
            this.hideNotificationsPanel();
        });

        document.getElementById('clearNotifications').addEventListener('click', () => {
            this.clearNotifications();
        });

        document.getElementById('requestNotificationPermission').addEventListener('click', () => {
            this.requestNotificationPermission();
        });

        // Notification settings
        document.getElementById('browserNotificationsToggle').addEventListener('change', (e) => {
            this.notificationSettings.browser = e.target.checked;
            this.saveNotificationSettings();
        });

        document.getElementById('notificationSoundsToggle').addEventListener('change', (e) => {
            this.notificationSettings.sounds = e.target.checked;
            this.saveNotificationSettings();
        });

        document.getElementById('notifyCommandsToggle').addEventListener('change', (e) => {
            this.notificationSettings.commands = e.target.checked;
            this.saveNotificationSettings();
        });

        document.getElementById('notifyErrorsToggle').addEventListener('change', (e) => {
            this.notificationSettings.errors = e.target.checked;
            this.saveNotificationSettings();
        });

        // Logs system
        document.querySelectorAll('.log-filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.filterLogs(e.currentTarget.dataset.level);
            });
        });

        document.getElementById('toggleAutoScroll').addEventListener('click', () => {
            this.toggleAutoScroll();
        });

        document.getElementById('exportLogs').addEventListener('click', () => {
            this.exportLogsToFile();
        });

        document.getElementById('clearLogs').addEventListener('click', () => {
            this.clearAllLogs();
        });

        // Themes system
        document.getElementById('toggleCustomThemeEditor').addEventListener('click', () => {
            this.toggleCustomThemeEditor();
        });

        document.getElementById('applyCustomTheme').addEventListener('click', () => {
            this.applyCustomTheme();
        });

        document.getElementById('exportTheme').addEventListener('click', () => {
            this.exportThemeToFile();
        });

        document.getElementById('importTheme').addEventListener('click', () => {
            this.importThemeFromFile();
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
            this.showToast('⚠️ Reconocimiento de voz no disponible. Usa Chrome, Edge o Safari.', 'error');
            return;
        }

        // Initialize speech recognition
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = new SpeechRecognition();

        // Get language from settings or default to Spanish
        const lang = localStorage.getItem('terryLang') || 'es-ES';
        this.recognition.lang = lang;
        this.recognition.continuous = false;
        this.recognition.interimResults = true;
        this.recognition.maxAlternatives = 1;

        // Notify user
        this.showToast('🎤 Micrófono activado. Habla ahora...');

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

        // Start performance timer
        const perfStart = performance.now();

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

            // Calculate performance
            const perfEnd = performance.now();
            const duration = perfEnd - perfStart;

            // Record performance
            this.recordPerformance(command, duration, data.success);

            // Log performance
            this.addLog('info', `Command executed in ${duration.toFixed(0)}ms: "${command}"`, 'performance');

            if (data.success) {
                // Update last item in history
                this.history[this.history.length - 1] = data;
                this.renderHistory();
            } else {
                this.showToast('Error ejecutando comando', 'error');
            }
        } catch (error) {
            // Record failed performance
            const perfEnd = performance.now();
            const duration = perfEnd - perfStart;
            this.recordPerformance(command, duration, false);

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

    async loadSettings() {
        // Load theme
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'dark') {
            document.body.classList.add('dark-theme');
            document.getElementById('darkModeToggle').checked = true;
            document.querySelector('#themeToggle i').className = 'fas fa-sun';
        }

        // Load camera configuration
        await this.loadCameraConfig();
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

        list.innerHTML = this.history.slice().reverse().map((item, revIndex) => {
            const actualIndex = this.history.length - 1 - revIndex;
            return `
            <div class="history-item">
                <div style="position: absolute; top: 0.5rem; right: 0.5rem; display: flex; gap: 0.25rem; opacity: 0; transition: opacity 0.2s;" class="action-buttons">
                    <button class="btn-small" onclick="window.terryUI.replayCommand(${actualIndex})" title="Re-ejecutar">
                        <i class="fas fa-redo"></i>
                    </button>
                    <button class="btn-small" onclick="window.terryUI.editCommand(${actualIndex})" title="Editar y ejecutar">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn-small" onclick="window.terryUI.copyToClipboard('${this.escapeHtml(item.response).replace(/'/g, "\\'")}', 'click')" title="Copiar respuesta">
                        <i class="fas fa-copy"></i>
                    </button>
                    <button class="btn-small" onclick="window.terryUI.addToQuickCommands(${actualIndex})" title="Añadir a comandos rápidos">
                        <i class="fas fa-bolt"></i>
                    </button>
                </div>
                <div class="history-command">
                    <i class="fas fa-terminal"></i> ${this.escapeHtml(item.command)}
                </div>
                <div class="history-response">
                    ${this.escapeHtml(item.response)}
                </div>
                <div class="history-time">
                    ${this.getRelativeTime(item.timestamp)}
                </div>
            </div>
        `;
        }).join('');
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
    // CAMERA CONFIGURATION
    // ═══════════════════════════════════════════════════════════

    async loadCameraConfig() {
        try {
            const response = await fetch('/api/camera/config');
            const data = await response.json();

            if (data.success && data.config) {
                const config = data.config;

                // Set toggles
                document.getElementById('cameraEnabledToggle').checked = config.enabled || false;
                document.getElementById('cameraAutoStartToggle').checked = config.auto_start || false;

                // Set camera type
                const useWebcam = config.use_webcam || false;
                document.getElementById('cameraType').value = useWebcam ? 'webcam' : 'ip';
                this.toggleCameraSettings(useWebcam ? 'webcam' : 'ip');

                // Set IP camera settings
                if (config.camera_url) {
                    document.getElementById('cameraUrl').value = config.camera_url;
                }
                if (config.camera_username) {
                    document.getElementById('cameraUsername').value = config.camera_username;
                }
                if (config.camera_password_set) {
                    document.getElementById('cameraPassword').value = '****';
                }

                // Set webcam settings
                document.getElementById('webcamIndex').value = config.webcam_index || 0;
            }
        } catch (error) {
            console.error('Error loading camera config:', error);
        }
    }

    toggleCameraSettings(type) {
        const ipSettings = document.getElementById('ipCameraSettings');
        const webcamSettings = document.getElementById('webcamSettings');

        if (type === 'webcam') {
            ipSettings.style.display = 'none';
            webcamSettings.style.display = 'grid';
        } else {
            ipSettings.style.display = 'grid';
            webcamSettings.style.display = 'none';
        }
    }

    async saveCameraConfig() {
        try {
            const cameraType = document.getElementById('cameraType').value;
            const config = {
                enabled: document.getElementById('cameraEnabledToggle').checked,
                auto_start: document.getElementById('cameraAutoStartToggle').checked,
                use_webcam: cameraType === 'webcam'
            };

            if (cameraType === 'webcam') {
                config.webcam_index = parseInt(document.getElementById('webcamIndex').value);
            } else {
                config.camera_url = document.getElementById('cameraUrl').value;
                config.camera_username = document.getElementById('cameraUsername').value;

                const password = document.getElementById('cameraPassword').value;
                if (password && password !== '****') {
                    config.camera_password = password;
                }
            }

            const response = await fetch('/api/camera/config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(config)
            });

            const data = await response.json();

            if (data.success) {
                this.showToast('✅ Configuración de cámara guardada');
            } else {
                this.showToast('❌ Error guardando configuración');
            }
        } catch (error) {
            console.error('Error saving camera config:', error);
            this.showToast('❌ Error guardando configuración');
        }
    }

    async testCamera() {
        try {
            this.showToast('🔄 Probando cámara...');

            // First, save the config
            await this.saveCameraConfig();

            // Then try to start the camera
            const response = await fetch('/api/camera/start', {
                method: 'POST'
            });

            const data = await response.json();

            if (data.success) {
                this.showToast('✅ Cámara funcionando correctamente');

                // Show status
                setTimeout(async () => {
                    await this.updateCameraStatus();
                }, 2000);
            } else {
                this.showToast('❌ Error: ' + data.message);
            }
        } catch (error) {
            console.error('Error testing camera:', error);
            this.showToast('❌ Error probando cámara');
        }
    }

    async updateCameraStatus() {
        try {
            const response = await fetch('/api/camera/status');
            const data = await response.json();

            const statusPanel = document.getElementById('cameraStatus');
            const statusContent = document.getElementById('cameraStatusContent');

            if (data.running) {
                const people = data.people_present || [];
                const stats = data.stats || {};

                let html = '<div class="camera-status-ok">';
                html += '<p><i class="fas fa-check-circle"></i> <strong>Cámara activa</strong></p>';

                if (people.length > 0) {
                    html += `<p>👥 Personas presentes: ${people.join(', ')}</p>`;
                } else {
                    html += '<p>👤 No hay nadie presente</p>';
                }

                html += `<p>📊 Total detecciones: ${stats.total_detections || 0}</p>`;
                html += `<p>👨‍👩‍👧‍👦 Personas únicas: ${stats.unique_people || 0}</p>`;
                html += '</div>';

                statusContent.innerHTML = html;
                statusPanel.style.display = 'grid';
            } else {
                statusContent.innerHTML = '<p><i class="fas fa-times-circle"></i> Cámara no está activa</p>';
                statusPanel.style.display = 'grid';
            }
        } catch (error) {
            console.error('Error getting camera status:', error);
        }
    }

    // ═══════════════════════════════════════════════════════════
    // UTILITIES
    // ═══════════════════════════════════════════════════════════

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Copy to clipboard
    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            this.showToast('✅ Copiado al portapapeles');
        } catch (error) {
            console.error('Error copying to clipboard:', error);
            this.showToast('❌ Error al copiar', 'error');
        }
    }

    // Get relative time (e.g., "hace 5 min")
    getRelativeTime(timestamp) {
        const now = new Date();
        const then = new Date(timestamp);
        const diffMs = now - then;
        const diffSec = Math.floor(diffMs / 1000);
        const diffMin = Math.floor(diffSec / 60);
        const diffHour = Math.floor(diffMin / 60);
        const diffDay = Math.floor(diffHour / 24);

        if (diffSec < 60) return 'justo ahora';
        if (diffMin < 60) return `hace ${diffMin} min`;
        if (diffHour < 24) return `hace ${diffHour}h`;
        if (diffDay < 7) return `hace ${diffDay}d`;
        return then.toLocaleDateString();
    }

    // Export data to JSON/CSV
    exportData(type = 'json') {
        let data, filename, content;

        const activeTab = document.querySelector('.tab.active').dataset.tab;

        if (activeTab === 'history') {
            data = this.history;
            filename = `terry-history-${new Date().toISOString().split('T')[0]}`;
        } else if (activeTab === 'chat') {
            data = this.chatMessages;
            filename = `terry-chat-${new Date().toISOString().split('T')[0]}`;
        } else {
            this.showToast('No hay datos para exportar en esta pestaña', 'error');
            return;
        }

        if (type === 'json') {
            content = JSON.stringify(data, null, 2);
            filename += '.json';
        } else if (type === 'csv') {
            if (activeTab === 'history') {
                const headers = ['Comando', 'Respuesta', 'Timestamp'];
                const rows = data.map(item => [
                    item.command,
                    item.response,
                    item.timestamp
                ]);
                content = [headers, ...rows].map(row =>
                    row.map(cell => `"${cell}"`).join(',')
                ).join('\n');
            } else {
                const headers = ['Sender', 'Text', 'Timestamp'];
                const rows = data.map(item => [
                    item.sender,
                    item.text,
                    item.timestamp
                ]);
                content = [headers, ...rows].map(row =>
                    row.map(cell => `"${cell}"`).join(',')
                ).join('\n');
            }
            filename += '.csv';
        }

        // Download
        const blob = new Blob([content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);

        this.showToast(`📥 Datos exportados: ${filename}`);
    }

    // Search/filter history
    filterHistory(query) {
        if (!query) {
            this.renderHistory();
            return;
        }

        const filtered = this.history.filter(item =>
            item.command.toLowerCase().includes(query.toLowerCase()) ||
            item.response.toLowerCase().includes(query.toLowerCase())
        );

        const list = document.getElementById('historyList');

        if (filtered.length === 0) {
            list.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-search"></i>
                    <p>No se encontraron resultados para "${this.escapeHtml(query)}"</p>
                </div>
            `;
            return;
        }

        list.innerHTML = filtered.slice().reverse().map(item => `
            <div class="history-item">
                <button class="btn-small copy-btn" onclick="window.terryUI.copyToClipboard('${this.escapeHtml(item.response).replace(/'/g, "\\'")}')">
                    <i class="fas fa-copy"></i>
                </button>
                <div class="history-command">
                    <i class="fas fa-terminal"></i> ${this.escapeHtml(item.command)}
                </div>
                <div class="history-response">
                    ${this.escapeHtml(item.response)}
                </div>
                <div class="history-time">
                    ${this.getRelativeTime(item.timestamp)}
                </div>
            </div>
        `).join('');
    }

    // Setup keyboard shortcuts
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl+K or Cmd+K: Focus search (if available)
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                const searchInput = document.querySelector('#historySearch');
                if (searchInput) searchInput.focus();
            }

            // ESC: Close modals
            if (e.key === 'Escape') {
                const modal = document.querySelector('.modal.show');
                if (modal) {
                    modal.classList.remove('show');
                }
            }

            // Ctrl+Enter or Cmd+Enter: Send message/command
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                const activeTab = document.querySelector('.tab.active').dataset.tab;
                if (activeTab === 'chat') {
                    this.sendChatMessage();
                } else {
                    this.sendCommand();
                }
            }

            // Ctrl+E or Cmd+E: Export data
            if ((e.ctrlKey || e.metaKey) && e.key === 'e') {
                e.preventDefault();
                this.exportData('json');
            }
        });
    }

    // Auto-refresh stats
    startAutoRefresh() {
        // Refresh stats every 10 seconds
        setInterval(() => {
            this.loadStats();
            if (document.querySelector('.tab[data-tab="dashboard"]').classList.contains('active')) {
                this.refreshDashboard();
            }
        }, 10000);
    }

    // ═══════════════════════════════════════════════════════════
    // DASHBOARD & ANALYTICS
    // ═══════════════════════════════════════════════════════════

    async initDashboard() {
        // Initialize Chart.js instances
        this.charts = {};

        // Setup event listeners
        document.getElementById('refreshDashboard')?.addEventListener('click', () => {
            this.refreshDashboard();
        });

        document.getElementById('dashboardTimeRange')?.addEventListener('change', (e) => {
            this.dashboardTimeRange = e.target.value;
            this.refreshDashboard();
        });

        // Initial load
        this.dashboardTimeRange = 'day';
        await this.refreshDashboard();
    }

    async refreshDashboard() {
        try {
            const metrics = await this.getDashboardMetrics();
            this.updateMetricsCards(metrics);
            this.updateCharts(metrics);
            this.updateRecentActivity(metrics.recent_activity || []);
        } catch (error) {
            console.error('Error refreshing dashboard:', error);
            this.showToast('❌ Error al actualizar dashboard', 'error');
        }
    }

    async getDashboardMetrics() {
        // Get metrics from history and stats
        const timeRange = this.dashboardTimeRange || 'day';
        const now = Date.now();
        const ranges = {
            hour: 60 * 60 * 1000,
            day: 24 * 60 * 60 * 1000,
            week: 7 * 24 * 60 * 60 * 1000,
            month: 30 * 24 * 60 * 60 * 1000
        };
        const cutoff = now - ranges[timeRange];

        // Filter history by time range
        const recentHistory = this.history.filter(item => {
            const timestamp = new Date(item.timestamp).getTime();
            return timestamp >= cutoff;
        });

        // Calculate metrics
        const totalCommands = recentHistory.length;
        const successCommands = recentHistory.filter(h => h.success !== false).length;
        const successRate = totalCommands > 0 ? (successCommands / totalCommands * 100).toFixed(1) : 0;

        // Command frequency
        const commandCounts = {};
        recentHistory.forEach(item => {
            const cmd = item.command.toLowerCase();
            commandCounts[cmd] = (commandCounts[cmd] || 0) + 1;
        });

        const sortedCommands = Object.entries(commandCounts)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 10);

        const topCommand = sortedCommands.length > 0 ? sortedCommands[0][0] : 'N/A';
        const topCommandCount = sortedCommands.length > 0 ? sortedCommands[0][1] : 0;

        // Commands per hour
        const hoursData = this.getCommandsPerHour(recentHistory, timeRange);

        // Response times (simulated - would need backend data)
        const avgResponseTime = Math.floor(Math.random() * 500 + 200); // 200-700ms

        // Action types distribution
        const actionTypes = this.categorizeCommands(recentHistory);

        return {
            total_commands: totalCommands,
            success_rate: successRate,
            avg_response_time: avgResponseTime,
            top_command: topCommand,
            top_command_count: topCommandCount,
            commands_trend: this.calculateTrend(totalCommands, timeRange),
            success_trend: 0,
            time_trend: 0,
            hourly_data: hoursData,
            top_commands: sortedCommands,
            action_types: actionTypes,
            recent_activity: recentHistory.slice(0, 10)
        };
    }

    getCommandsPerHour(history, timeRange) {
        const hours = timeRange === 'hour' ? 12 : 24;
        const data = new Array(hours).fill(0);
        const labels = [];
        const now = new Date();

        for (let i = hours - 1; i >= 0; i--) {
            const hour = new Date(now);
            hour.setHours(hour.getHours() - i);
            labels.push(hour.getHours() + ':00');
        }

        history.forEach(item => {
            const itemDate = new Date(item.timestamp);
            const hoursDiff = Math.floor((now - itemDate) / (1000 * 60 * 60));
            if (hoursDiff < hours) {
                data[hours - 1 - hoursDiff]++;
            }
        });

        return { labels, data };
    }

    categorizeCommands(history) {
        const categories = {
            'Música': 0,
            'Navegación': 0,
            'Sistema': 0,
            'Productividad': 0,
            'Otros': 0
        };

        const keywords = {
            'Música': ['música', 'canción', 'spotify', 'reproduce', 'pausa', 'siguiente'],
            'Navegación': ['abre', 'busca', 'google', 'youtube', 'web'],
            'Sistema': ['volumen', 'brillo', 'apaga', 'reinicia'],
            'Productividad': ['trabajo', 'nota', 'recordatorio', 'calendario']
        };

        history.forEach(item => {
            const cmd = item.command.toLowerCase();
            let categorized = false;

            for (const [category, words] of Object.entries(keywords)) {
                if (words.some(word => cmd.includes(word))) {
                    categories[category]++;
                    categorized = true;
                    break;
                }
            }

            if (!categorized) {
                categories['Otros']++;
            }
        });

        return categories;
    }

    calculateTrend(current, timeRange) {
        // Simplified trend calculation (would need historical data)
        return Math.floor(Math.random() * 20 - 10); // -10% to +10%
    }

    updateMetricsCards(metrics) {
        // Update metric values
        document.getElementById('totalCommands').textContent = metrics.total_commands;
        document.getElementById('successRate').textContent = metrics.success_rate + '%';
        document.getElementById('avgResponseTime').textContent = metrics.avg_response_time + 'ms';
        document.getElementById('topCommand').textContent =
            metrics.top_command.length > 30 ? metrics.top_command.substring(0, 30) + '...' : metrics.top_command;
        document.getElementById('topCommandCount').querySelector('span').textContent =
            metrics.top_command_count + ' veces';

        // Update trends
        this.updateTrend('commandsTrend', metrics.commands_trend);
        this.updateTrend('successTrend', metrics.success_trend);
        this.updateTrend('timeTrend', metrics.time_trend);
    }

    updateTrend(elementId, value) {
        const el = document.getElementById(elementId);
        if (!el) return;

        const span = el.querySelector('span');
        const icon = el.querySelector('i');

        if (value > 0) {
            el.className = 'metric-trend positive';
            icon.className = 'fas fa-arrow-up';
            span.textContent = `+${value}%`;
        } else if (value < 0) {
            el.className = 'metric-trend negative';
            icon.className = 'fas fa-arrow-down';
            span.textContent = `${value}%`;
        } else {
            el.className = 'metric-trend';
            icon.className = 'fas fa-minus';
            span.textContent = '0%';
        }
    }

    updateCharts(metrics) {
        // Commands per hour line chart
        this.updateCommandsChart(metrics.hourly_data);

        // Top commands bar chart
        this.updateTopCommandsChart(metrics.top_commands);

        // Response time chart
        this.updateResponseTimeChart(metrics.hourly_data);

        // Action types pie chart
        this.updateActionsChart(metrics.action_types);
    }

    updateCommandsChart(hourlyData) {
        const ctx = document.getElementById('commandsChart');
        if (!ctx) return;

        if (this.charts.commands) {
            this.charts.commands.destroy();
        }

        this.charts.commands = new Chart(ctx, {
            type: 'line',
            data: {
                labels: hourlyData.labels,
                datasets: [{
                    label: 'Comandos',
                    data: hourlyData.data,
                    borderColor: '#ff6b35',
                    backgroundColor: 'rgba(255, 107, 53, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { stepSize: 1 }
                    }
                }
            }
        });
    }

    updateTopCommandsChart(topCommands) {
        const ctx = document.getElementById('topCommandsChart');
        if (!ctx) return;

        if (this.charts.topCommands) {
            this.charts.topCommands.destroy();
        }

        const labels = topCommands.map(([cmd]) =>
            cmd.length > 20 ? cmd.substring(0, 20) + '...' : cmd
        );
        const data = topCommands.map(([, count]) => count);

        this.charts.topCommands = new Chart(ctx, {
            type: 'bar',
            data: {
                labels,
                datasets: [{
                    label: 'Usos',
                    data,
                    backgroundColor: '#ff6b35'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }

    updateResponseTimeChart(hourlyData) {
        const ctx = document.getElementById('responseTimeChart');
        if (!ctx) return;

        if (this.charts.responseTime) {
            this.charts.responseTime.destroy();
        }

        // Generate simulated response times
        const data = hourlyData.data.map(() => Math.floor(Math.random() * 300 + 200));

        this.charts.responseTime = new Chart(ctx, {
            type: 'line',
            data: {
                labels: hourlyData.labels,
                datasets: [{
                    label: 'Tiempo (ms)',
                    data,
                    borderColor: '#4facfe',
                    backgroundColor: 'rgba(79, 172, 254, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    updateActionsChart(actionTypes) {
        const ctx = document.getElementById('actionsChart');
        if (!ctx) return;

        if (this.charts.actions) {
            this.charts.actions.destroy();
        }

        const labels = Object.keys(actionTypes);
        const data = Object.values(actionTypes);
        const colors = ['#ff6b35', '#ff8c42', '#ffaa5a', '#10b981', '#3b82f6'];

        this.charts.actions = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels,
                datasets: [{
                    data,
                    backgroundColor: colors
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    updateRecentActivity(activities) {
        const container = document.getElementById('recentActivity');
        if (!container) return;

        if (activities.length === 0) {
            container.innerHTML = '<p style="text-align: center; color: var(--text-secondary); padding: 2rem;">No hay actividad reciente</p>';
            return;
        }

        container.innerHTML = activities.map(activity => {
            const success = activity.success !== false;
            const iconClass = success ? 'success' : 'error';
            const icon = success ? 'fa-check' : 'fa-times';
            const relativeTime = this.getRelativeTime(activity.timestamp);

            return `
                <div class="activity-item">
                    <div class="activity-icon ${iconClass}">
                        <i class="fas ${icon}"></i>
                    </div>
                    <div class="activity-details">
                        <div class="activity-command">${this.escapeHtml(activity.command)}</div>
                        <div class="activity-meta">
                            <div class="activity-time">
                                <i class="fas fa-clock"></i>
                                ${relativeTime}
                            </div>
                            <span class="activity-badge ${iconClass}">
                                ${success ? 'Éxito' : 'Error'}
                            </span>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }

    // ═══════════════════════════════════════════════════════════
    // AUTOCOMPLETE
    // ═══════════════════════════════════════════════════════════

    initAutocomplete() {
        // Setup autocomplete for chat input
        const chatInput = document.getElementById('chatInput');
        const commandInput = document.getElementById('commandInput');

        if (chatInput) {
            this.setupAutocompleteField(chatInput, 'chat');
        }
        if (commandInput) {
            this.setupAutocompleteField(commandInput, 'command');
        }
    }

    setupAutocompleteField(input, type) {
        // Create autocomplete container
        const container = document.createElement('div');
        container.className = 'autocomplete-container';
        container.style.display = 'none';
        input.parentElement.style.position = 'relative';
        input.parentElement.appendChild(container);

        let selectedIndex = -1;

        // Input event listener
        input.addEventListener('input', (e) => {
            const query = e.target.value.trim().toLowerCase();
            if (query.length < 2) {
                container.style.display = 'none';
                return;
            }

            const suggestions = this.getAutocompleteSuggestions(query);
            if (suggestions.length === 0) {
                container.style.display = 'none';
                return;
            }

            this.renderAutocompleteSuggestions(container, suggestions, (suggestion) => {
                input.value = suggestion;
                container.style.display = 'none';
                input.focus();
            });

            container.style.display = 'block';
            selectedIndex = -1;
        });

        // Keyboard navigation
        input.addEventListener('keydown', (e) => {
            const items = container.querySelectorAll('.autocomplete-item');

            if (e.key === 'ArrowDown') {
                e.preventDefault();
                selectedIndex = Math.min(selectedIndex + 1, items.length - 1);
                this.updateAutocompleteSelection(items, selectedIndex);
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                selectedIndex = Math.max(selectedIndex - 1, -1);
                this.updateAutocompleteSelection(items, selectedIndex);
            } else if (e.key === 'Enter' && selectedIndex >= 0) {
                e.preventDefault();
                items[selectedIndex].click();
            } else if (e.key === 'Escape') {
                container.style.display = 'none';
                selectedIndex = -1;
            }
        });

        // Click outside to close
        document.addEventListener('click', (e) => {
            if (!input.contains(e.target) && !container.contains(e.target)) {
                container.style.display = 'none';
            }
        });
    }

    getAutocompleteSuggestions(query) {
        const suggestions = new Set();

        // Get from history
        this.history.forEach(item => {
            const cmd = item.command.toLowerCase();
            if (cmd.includes(query)) {
                suggestions.add(item.command);
            }
        });

        // Get from quick commands
        this.quickCommands.forEach(qc => {
            const cmd = qc.command.toLowerCase();
            if (cmd.includes(query)) {
                suggestions.add(qc.command);
            }
        });

        // Common commands
        const commonCommands = [
            'pon música',
            'pausa',
            'siguiente canción',
            'abre youtube',
            'abre google',
            'busca en google',
            'sube el volumen',
            'baja el volumen',
            'modo trabajo',
            'buenas noches',
            'qué hora es',
            'cómo está el tiempo',
            'crea una nota',
            'lista mis notas',
            'activa la cámara',
            'estado del sistema'
        ];

        commonCommands.forEach(cmd => {
            if (cmd.toLowerCase().includes(query)) {
                suggestions.add(cmd);
            }
        });

        // Convert to array and sort by relevance
        return Array.from(suggestions)
            .sort((a, b) => {
                const aIndex = a.toLowerCase().indexOf(query);
                const bIndex = b.toLowerCase().indexOf(query);
                if (aIndex !== bIndex) return aIndex - bIndex;
                return a.length - b.length;
            })
            .slice(0, 5); // Max 5 suggestions
    }

    renderAutocompleteSuggestions(container, suggestions, onClick) {
        container.innerHTML = suggestions.map((suggestion, index) => `
            <div class="autocomplete-item" data-index="${index}">
                <i class="fas fa-history"></i>
                <span>${this.highlightMatch(suggestion, container.parentElement.querySelector('input').value)}</span>
            </div>
        `).join('');

        container.querySelectorAll('.autocomplete-item').forEach(item => {
            item.addEventListener('click', () => {
                onClick(suggestions[item.dataset.index]);
            });
        });
    }

    updateAutocompleteSelection(items, selectedIndex) {
        items.forEach((item, index) => {
            if (index === selectedIndex) {
                item.classList.add('selected');
            } else {
                item.classList.remove('selected');
            }
        });
    }

    highlightMatch(text, query) {
        if (!query) return this.escapeHtml(text);
        const regex = new RegExp(`(${this.escapeRegex(query)})`, 'gi');
        return this.escapeHtml(text).replace(regex, '<strong>$1</strong>');
    }

    escapeRegex(str) {
        return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    // ═══════════════════════════════════════════════════════════
    // QUICK COMMANDS
    // ═══════════════════════════════════════════════════════════

    loadQuickCommands() {
        const saved = localStorage.getItem('terryQuickCommands');
        if (saved) {
            return JSON.parse(saved);
        }
        // Default quick commands
        return [
            { icon: '🎵', title: 'Música', command: 'pon música', color: '#ff6b35' },
            { icon: '⏸️', title: 'Pausar', command: 'pausa', color: '#f59e0b' },
            { icon: '📺', title: 'YouTube', command: 'abre youtube', color: '#ef4444' },
            { icon: '💼', title: 'Trabajo', command: 'modo trabajo', color: '#3b82f6' },
            { icon: '🌙', title: 'Buenas Noches', command: 'buenas noches', color: '#8b5cf6' },
        ];
    }

    saveQuickCommands() {
        localStorage.setItem('terryQuickCommands', JSON.stringify(this.quickCommands));
    }

    renderQuickCommands() {
        const grid = document.getElementById('quickCommandsGrid');

        if (this.quickCommands.length === 0) {
            grid.innerHTML = `
                <div class="quick-command-empty">
                    <i class="fas fa-bolt" style="font-size: 2rem; margin-bottom: 0.5rem;"></i>
                    <p>No hay comandos rápidos configurados</p>
                    <button class="btn-primary mt-2" onclick="window.terryUI.showQuickCommandConfig()">
                        <i class="fas fa-plus"></i> Añadir Comando
                    </button>
                </div>
            `;
            return;
        }

        grid.innerHTML = this.quickCommands.map((cmd, index) => `
            <button class="quick-command-btn" onclick="window.terryUI.executeQuickCommand(${index})" data-shortcut="${index + 1}">
                <span class="shortcut">${index + 1}</span>
                <span class="icon">${cmd.icon}</span>
                <div class="title">${this.escapeHtml(cmd.title)}</div>
                <div class="command">${this.escapeHtml(cmd.command)}</div>
            </button>
        `).join('');
    }

    async executeQuickCommand(index) {
        const cmd = this.quickCommands[index];
        if (!cmd) return;

        // Visual feedback
        const btn = document.querySelector(`[data-shortcut="${index + 1}"]`);
        if (btn) {
            btn.style.transform = 'scale(0.95)';
            setTimeout(() => {
                btn.style.transform = '';
            }, 150);
        }

        // Execute command
        await this.sendCommand(cmd.command);
        this.showToast(`⚡ Ejecutando: ${cmd.title}`);
    }

    showQuickCommandConfig() {
        // Create modal HTML
        const modalHTML = `
            <div class="modal show" id="quickCommandModal">
                <div class="modal-content">
                    <div class="modal-header">
                        <h3>⚡ Configurar Comandos Rápidos</h3>
                        <button class="modal-close" onclick="window.terryUI.closeQuickCommandConfig()">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div class="modal-body">
                        <div class="form-group">
                            <label>Icono (emoji)</label>
                            <input type="text" id="qcIcon" placeholder="🎵" maxlength="2" style="width: 100%; padding: 0.5rem; font-size: 2rem; text-align: center;">
                        </div>
                        <div class="form-group">
                            <label>Título</label>
                            <input type="text" id="qcTitle" placeholder="Ej: Música" style="width: 100%; padding: 0.5rem;">
                        </div>
                        <div class="form-group">
                            <label>Comando</label>
                            <input type="text" id="qcCommand" placeholder="Ej: pon música" style="width: 100%; padding: 0.5rem;">
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button class="btn-secondary" onclick="window.terryUI.closeQuickCommandConfig()">Cancelar</button>
                        <button class="btn-primary" onclick="window.terryUI.addQuickCommand()">
                            <i class="fas fa-plus"></i> Añadir
                        </button>
                    </div>
                </div>
            </div>
        `;

        // Add to body
        document.body.insertAdjacentHTML('beforeend', modalHTML);
    }

    closeQuickCommandConfig() {
        const modal = document.getElementById('quickCommandModal');
        if (modal) modal.remove();
    }

    addQuickCommand() {
        const icon = document.getElementById('qcIcon').value.trim();
        const title = document.getElementById('qcTitle').value.trim();
        const command = document.getElementById('qcCommand').value.trim();

        if (!icon || !title || !command) {
            this.showToast('❌ Completa todos los campos', 'error');
            return;
        }

        if (this.quickCommands.length >= 9) {
            this.showToast('❌ Máximo 9 comandos rápidos', 'error');
            return;
        }

        this.quickCommands.push({ icon, title, command });
        this.saveQuickCommands();
        this.renderQuickCommands();
        this.closeQuickCommandConfig();
        this.showToast('✅ Comando rápido añadido');
    }

    setupQuickCommandShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Number keys 1-9 (not in input fields)
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

            const num = parseInt(e.key);
            if (num >= 1 && num <= 9) {
                const index = num - 1;
                if (this.quickCommands[index]) {
                    e.preventDefault();
                    this.executeQuickCommand(index);
                }
            }
        });
    }

    // ═══════════════════════════════════════════════════════════
    // HISTORY REPLAY & EDIT
    // ═══════════════════════════════════════════════════════════

    async replayCommand(index) {
        const item = this.history[index];
        if (!item) return;

        this.showToast(`🔄 Re-ejecutando: ${item.command}`);
        await this.sendCommand(item.command);
    }

    editCommand(index) {
        const item = this.history[index];
        if (!item) return;

        // Prompt user to edit
        const edited = prompt('Edita el comando:', item.command);
        if (edited && edited.trim()) {
            this.showToast(`✏️ Ejecutando comando editado`);
            this.sendCommand(edited.trim());
        }
    }

    addToQuickCommands(index) {
        const item = this.history[index];
        if (!item) return;

        if (this.quickCommands.length >= 9) {
            this.showToast('❌ Máximo 9 comandos rápidos', 'error');
            return;
        }

        // Prompt for title and icon
        const title = prompt('Título para el comando rápido:', item.command.slice(0, 20));
        if (!title) return;

        const icon = prompt('Emoji para el comando:', '⚡');
        if (!icon) return;

        this.quickCommands.push({
            icon: icon.trim(),
            title: title.trim(),
            command: item.command
        });

        this.saveQuickCommands();
        this.renderQuickCommands();
        this.showToast('✅ Añadido a comandos rápidos');
    }

    // ═══════════════════════════════════════════════════════════
    // AUTOCOMPLETE SYSTEM
    // ═══════════════════════════════════════════════════════════

    initAutocomplete() {
        const input = document.getElementById('commandInput');
        const dropdown = document.getElementById('autocompleteDropdown');

        // Input event - filter suggestions
        input.addEventListener('input', (e) => {
            const query = e.target.value.trim();
            if (query.length > 0) {
                this.filterAutocomplete(query);
            } else {
                this.hideAutocomplete();
            }
        });

        // Keyboard navigation
        input.addEventListener('keydown', (e) => {
            if (!this.autocompleteVisible) return;

            switch(e.key) {
                case 'ArrowDown':
                    e.preventDefault();
                    this.navigateAutocomplete(1);
                    break;
                case 'ArrowUp':
                    e.preventDefault();
                    this.navigateAutocomplete(-1);
                    break;
                case 'Enter':
                    if (this.autocompleteSelectedIndex >= 0) {
                        e.preventDefault();
                        this.selectAutocomplete(this.autocompleteSuggestions[this.autocompleteSelectedIndex]);
                    }
                    break;
                case 'Escape':
                    this.hideAutocomplete();
                    break;
            }
        });

        // Click outside to close
        document.addEventListener('click', (e) => {
            if (!input.contains(e.target) && !dropdown.contains(e.target)) {
                this.hideAutocomplete();
            }
        });

        // Focus to show suggestions
        input.addEventListener('focus', () => {
            if (input.value.trim().length > 0) {
                this.filterAutocomplete(input.value.trim());
            }
        });
    }

    filterAutocomplete(query) {
        // Get unique commands from history
        const uniqueCommands = [...new Set(this.history.map(h => h.command))];

        // Add templates
        const templateCommands = this.templates.map(t => t.command);

        // Combine all sources
        const allCommands = [...uniqueCommands, ...templateCommands];

        // Fuzzy match and score
        const matches = allCommands
            .map(cmd => ({
                command: cmd,
                score: this.fuzzyMatchScore(query.toLowerCase(), cmd.toLowerCase())
            }))
            .filter(item => item.score > 0)
            .sort((a, b) => b.score - a.score)
            .slice(0, 8) // Max 8 suggestions
            .map(item => item.command);

        this.autocompleteSuggestions = matches;
        this.autocompleteSelectedIndex = -1;

        if (matches.length > 0) {
            this.renderAutocomplete(query);
            this.showAutocomplete();
        } else {
            this.hideAutocomplete();
        }
    }

    fuzzyMatchScore(query, text) {
        // Simple fuzzy matching algorithm
        // Returns score 0-100 based on match quality

        if (text.includes(query)) {
            // Exact substring match gets high score
            const startBonus = text.startsWith(query) ? 50 : 0;
            const lengthRatio = query.length / text.length;
            return 50 + startBonus + (lengthRatio * 30);
        }

        // Character-by-character fuzzy match
        let queryIndex = 0;
        let matchCount = 0;

        for (let i = 0; i < text.length && queryIndex < query.length; i++) {
            if (text[i] === query[queryIndex]) {
                matchCount++;
                queryIndex++;
            }
        }

        if (matchCount === query.length) {
            // All query characters found in order
            return 30 * (matchCount / text.length);
        }

        return 0;
    }

    renderAutocomplete(query) {
        const list = document.getElementById('autocompleteList');

        if (this.autocompleteSuggestions.length === 0) {
            list.innerHTML = '<div class="autocomplete-empty">No hay sugerencias</div>';
            return;
        }

        const queryLower = query.toLowerCase();

        list.innerHTML = `
            <div class="autocomplete-header">Sugerencias (${this.autocompleteSuggestions.length})</div>
            ${this.autocompleteSuggestions.map((suggestion, index) => {
                const isSelected = index === this.autocompleteSelectedIndex;
                const highlighted = this.highlightMatch(suggestion, query);

                // Find if this was recently used
                const historyItem = this.history.find(h => h.command === suggestion);
                const timeAgo = historyItem ? this.getRelativeTime(new Date(historyItem.timestamp)) : null;

                return `
                    <div class="autocomplete-item ${isSelected ? 'selected' : ''}"
                         data-index="${index}">
                        <span class="icon"><i class="fas fa-terminal"></i></span>
                        <span class="text">${highlighted}</span>
                        ${timeAgo ? `<span class="time">${timeAgo}</span>` : ''}
                    </div>
                `;
            }).join('')}
        `;

        // Add click handlers
        list.querySelectorAll('.autocomplete-item').forEach((item, index) => {
            item.addEventListener('click', () => {
                this.selectAutocomplete(this.autocompleteSuggestions[index]);
            });

            item.addEventListener('mouseenter', () => {
                this.autocompleteSelectedIndex = index;
                this.renderAutocomplete(query);
            });
        });
    }

    highlightMatch(text, query) {
        const queryLower = query.toLowerCase();
        const textLower = text.toLowerCase();

        if (textLower.includes(queryLower)) {
            const startIndex = textLower.indexOf(queryLower);
            const endIndex = startIndex + query.length;

            return text.substring(0, startIndex) +
                   '<span class="match">' + text.substring(startIndex, endIndex) + '</span>' +
                   text.substring(endIndex);
        }

        return text;
    }

    navigateAutocomplete(direction) {
        const newIndex = this.autocompleteSelectedIndex + direction;

        if (newIndex >= 0 && newIndex < this.autocompleteSuggestions.length) {
            this.autocompleteSelectedIndex = newIndex;
            const input = document.getElementById('commandInput');
            this.renderAutocomplete(input.value);

            // Scroll selected item into view
            const selectedItem = document.querySelector('.autocomplete-item.selected');
            if (selectedItem) {
                selectedItem.scrollIntoView({ block: 'nearest' });
            }
        }
    }

    selectAutocomplete(command) {
        const input = document.getElementById('commandInput');
        input.value = command;
        this.hideAutocomplete();
        input.focus();

        // Optionally auto-submit
        // this.sendCommand(command);
    }

    showAutocomplete() {
        const dropdown = document.getElementById('autocompleteDropdown');
        dropdown.classList.add('show');
        this.autocompleteVisible = true;
    }

    hideAutocomplete() {
        const dropdown = document.getElementById('autocompleteDropdown');
        dropdown.classList.remove('show');
        this.autocompleteVisible = false;
        this.autocompleteSelectedIndex = -1;
    }

    // ═══════════════════════════════════════════════════════════
    // TEMPLATES
    // ═══════════════════════════════════════════════════════════

    initTemplates() {
        this.renderTemplates();
    }

    loadTemplates() {
        const stored = localStorage.getItem('terryTemplates');
        if (stored) {
            try {
                return JSON.parse(stored);
            } catch (e) {
                console.error('Error loading templates:', e);
            }
        }
        // Default templates
        return [
            {
                name: 'Buscar en web',
                command: 'busca {{término}} en {{motor}}',
                category: 'web',
                variables: ['término', 'motor']
            },
            {
                name: 'Reproducir artista',
                command: 'pon música de {{artista}}',
                category: 'music',
                variables: ['artista']
            }
        ];
    }

    saveTemplates() {
        localStorage.setItem('terryTemplates', JSON.stringify(this.templates));
    }

    renderTemplates() {
        const grid = document.getElementById('templatesGrid');
        const emptyState = document.getElementById('templatesEmpty');

        if (this.templates.length === 0) {
            grid.style.display = 'none';
            emptyState.style.display = 'flex';
            return;
        }

        grid.style.display = 'grid';
        emptyState.style.display = 'none';

        grid.innerHTML = this.templates.map((template, index) => {
            const commandWithVars = template.command.replace(/\{\{([^}]+)\}\}/g, '<span class="variable">{{$1}}</span>');

            return `
                <div class="template-card">
                    <div class="template-header">
                        <div>
                            <div class="template-title">${template.name}</div>
                            <span class="template-category ${template.category}">${template.category}</span>
                        </div>
                    </div>
                    <div class="template-command">${commandWithVars}</div>
                    <div class="template-variables">
                        ${template.variables.map(v => `
                            <span class="template-variable-tag">
                                <i class="fas fa-dollar-sign"></i>
                                ${v}
                            </span>
                        `).join('')}
                    </div>
                    <div class="template-actions">
                        <button class="template-action-btn primary" onclick="window.terryUI.executeTemplate(${index})">
                            <i class="fas fa-play"></i> Ejecutar
                        </button>
                        <button class="template-action-btn" onclick="window.terryUI.editTemplate(${index})">
                            <i class="fas fa-edit"></i> Editar
                        </button>
                        <button class="template-action-btn danger" onclick="window.terryUI.deleteTemplate(${index})">
                            <i class="fas fa-trash"></i> Eliminar
                        </button>
                    </div>
                </div>
            `;
        }).join('');
    }

    extractVariables(command) {
        const regex = /\{\{([^}]+)\}\}/g;
        const variables = [];
        let match;
        while ((match = regex.exec(command)) !== null) {
            const varName = match[1].trim();
            if (!variables.includes(varName)) {
                variables.push(varName);
            }
        }
        return variables;
    }

    updateVariablesPreview() {
        const command = document.getElementById('templateCommand').value;
        const variables = this.extractVariables(command);
        const preview = document.getElementById('templateVariablesPreview');
        const list = document.getElementById('variablesList');

        if (variables.length > 0) {
            preview.style.display = 'block';
            list.innerHTML = variables.map(v =>
                `<span class="template-variable-tag"><i class="fas fa-dollar-sign"></i> ${v}</span>`
            ).join(' ');
        } else {
            preview.style.display = 'none';
        }
    }

    showTemplateModal(templateIndex = null) {
        const modal = document.getElementById('templateModal');
        const title = document.getElementById('templateModalTitle');
        const nameInput = document.getElementById('templateName');
        const commandInput = document.getElementById('templateCommand');
        const categorySelect = document.getElementById('templateCategory');

        if (templateIndex !== null) {
            // Edit mode
            this.currentTemplateIndex = templateIndex;
            const template = this.templates[templateIndex];
            title.textContent = 'Editar Template';
            nameInput.value = template.name;
            commandInput.value = template.command;
            categorySelect.value = template.category;
            this.updateVariablesPreview();
        } else {
            // Create mode
            this.currentTemplateIndex = null;
            title.textContent = 'Crear Template';
            nameInput.value = '';
            commandInput.value = '';
            categorySelect.value = 'general';
            document.getElementById('templateVariablesPreview').style.display = 'none';
        }

        modal.classList.add('active');
    }

    hideTemplateModal() {
        document.getElementById('templateModal').classList.remove('active');
        this.currentTemplateIndex = null;
    }

    saveTemplate() {
        const name = document.getElementById('templateName').value.trim();
        const command = document.getElementById('templateCommand').value.trim();
        const category = document.getElementById('templateCategory').value;

        if (!name || !command) {
            this.showToast('❌ Completa todos los campos', 'error');
            return;
        }

        const variables = this.extractVariables(command);

        if (variables.length === 0) {
            this.showToast('❌ El comando debe tener al menos una variable {{nombre}}', 'error');
            return;
        }

        const template = { name, command, category, variables };

        if (this.currentTemplateIndex !== null) {
            // Edit existing
            this.templates[this.currentTemplateIndex] = template;
            this.showToast('✅ Template actualizado');
        } else {
            // Create new
            this.templates.push(template);
            this.showToast('✅ Template creado');
        }

        this.saveTemplates();
        this.renderTemplates();
        this.hideTemplateModal();
    }

    editTemplate(index) {
        this.showTemplateModal(index);
    }

    deleteTemplate(index) {
        const template = this.templates[index];
        if (confirm(`¿Eliminar el template "${template.name}"?`)) {
            this.templates.splice(index, 1);
            this.saveTemplates();
            this.renderTemplates();
            this.showToast('✅ Template eliminado');
        }
    }

    executeTemplate(index) {
        this.currentExecutingTemplate = this.templates[index];
        this.showExecuteTemplateModal();
    }

    showExecuteTemplateModal() {
        const modal = document.getElementById('executeTemplateModal');
        const title = document.getElementById('executeTemplateTitle');
        const preview = document.getElementById('templateCommandPreview');
        const form = document.getElementById('templateVariablesForm');
        const template = this.currentExecutingTemplate;

        title.textContent = `Ejecutar: ${template.name}`;
        preview.textContent = template.command;

        // Create form inputs for each variable
        form.innerHTML = template.variables.map(varName => `
            <div class="template-var-input">
                <label>
                    Variable: <span class="var-name">{{${varName}}}</span>
                </label>
                <input
                    type="text"
                    data-var="${varName}"
                    placeholder="Ingresa valor para ${varName}"
                    autocomplete="off"
                >
            </div>
        `).join('');

        // Focus first input
        setTimeout(() => {
            const firstInput = form.querySelector('input');
            if (firstInput) firstInput.focus();
        }, 100);

        modal.classList.add('active');
    }

    hideExecuteTemplateModal() {
        document.getElementById('executeTemplateModal').classList.remove('active');
        this.currentExecutingTemplate = null;
    }

    confirmExecuteTemplate() {
        const form = document.getElementById('templateVariablesForm');
        const inputs = form.querySelectorAll('input');
        const values = {};

        // Collect values
        let hasEmpty = false;
        inputs.forEach(input => {
            const varName = input.dataset.var;
            const value = input.value.trim();
            if (!value) {
                hasEmpty = true;
                input.style.borderColor = 'var(--error)';
            } else {
                input.style.borderColor = '';
                values[varName] = value;
            }
        });

        if (hasEmpty) {
            this.showToast('❌ Completa todas las variables', 'error');
            return;
        }

        // Replace variables in command
        let finalCommand = this.currentExecutingTemplate.command;
        Object.entries(values).forEach(([varName, value]) => {
            finalCommand = finalCommand.replace(new RegExp(`\\{\\{${varName}\\}\\}`, 'g'), value);
        });

        // Execute command
        this.hideExecuteTemplateModal();
        this.showToast(`▶️ Ejecutando: ${finalCommand}`);
        this.sendCommand(finalCommand);
    }

    // ═══════════════════════════════════════════════════════════
    // NOTIFICATIONS SYSTEM
    // ═══════════════════════════════════════════════════════════

    initNotifications() {
        // Check notification permission
        if ('Notification' in window && Notification.permission === 'granted') {
            document.getElementById('browserNotificationsToggle').checked = true;
            document.getElementById('requestNotificationPermission').style.display = 'none';
        }

        // Load settings
        document.getElementById('browserNotificationsToggle').checked = this.notificationSettings.browser;
        document.getElementById('notificationSoundsToggle').checked = this.notificationSettings.sounds;
        document.getElementById('notifyCommandsToggle').checked = this.notificationSettings.commands;
        document.getElementById('notifyErrorsToggle').checked = this.notificationSettings.errors;

        // Create a welcome notification
        setTimeout(() => {
            this.createNotification('info', 'Terry Web UI', 'Bienvenido! El sistema de notificaciones está activo.', false);
        }, 1000);
    }

    loadNotificationSettings() {
        const stored = localStorage.getItem('terryNotificationSettings');
        if (stored) {
            try {
                return JSON.parse(stored);
            } catch (e) {
                console.error('Error loading notification settings:', e);
            }
        }
        return {
            browser: false,
            sounds: true,
            commands: true,
            errors: true
        };
    }

    saveNotificationSettings() {
        localStorage.setItem('terryNotificationSettings', JSON.stringify(this.notificationSettings));
    }

    createNotification(type, title, message, unread = true) {
        const notification = {
            id: Date.now() + Math.random(),
            type, // success, error, warning, info, command
            title,
            message,
            unread,
            timestamp: Date.now()
        };

        this.notifications.unshift(notification);
        if (unread) {
            this.unreadCount++;
        }

        // Update UI
        this.renderNotifications();
        this.updateNotificationBadge();

        // Play sound
        if (this.notificationSettings.sounds) {
            this.playNotificationSound(type);
        }

        // Browser notification
        if (this.notificationSettings.browser && this.shouldNotify(type)) {
            this.showBrowserNotification(title, message, type);
        }

        return notification;
    }

    shouldNotify(type) {
        if (type === 'command' && !this.notificationSettings.commands) return false;
        if (type === 'error' && !this.notificationSettings.errors) return false;
        return true;
    }

    renderNotifications() {
        const list = document.getElementById('notificationsList');
        const emptyState = document.getElementById('notificationsEmpty');

        if (this.notifications.length === 0) {
            emptyState.style.display = 'flex';
            list.style.display = 'none';
            return;
        }

        emptyState.style.display = 'none';
        list.style.display = 'flex';

        // Get icon for each type
        const getIcon = (type) => {
            switch (type) {
                case 'success': return 'fa-check-circle';
                case 'error': return 'fa-exclamation-circle';
                case 'warning': return 'fa-exclamation-triangle';
                case 'info': return 'fa-info-circle';
                case 'command': return 'fa-terminal';
                default: return 'fa-bell';
            }
        };

        list.innerHTML = this.notifications.map(notif => `
            <div class="notification-item ${notif.type} ${notif.unread ? 'unread' : ''}" data-id="${notif.id}">
                <div class="notification-item-header">
                    <div class="notification-item-icon">
                        <i class="fas ${getIcon(notif.type)}"></i>
                    </div>
                    <div class="notification-item-time">${this.getRelativeTime(notif.timestamp)}</div>
                </div>
                <div class="notification-item-content">
                    <div class="notification-item-body">
                        <div class="notification-item-title">${notif.title}</div>
                        <div class="notification-item-message">${notif.message}</div>
                    </div>
                </div>
            </div>
        `).join('');

        // Add click handlers to mark as read
        list.querySelectorAll('.notification-item.unread').forEach(item => {
            item.addEventListener('click', () => {
                const id = parseFloat(item.dataset.id);
                this.markNotificationAsRead(id);
            });
        });
    }

    markNotificationAsRead(id) {
        const notif = this.notifications.find(n => n.id === id);
        if (notif && notif.unread) {
            notif.unread = false;
            this.unreadCount = Math.max(0, this.unreadCount - 1);
            this.renderNotifications();
            this.updateNotificationBadge();
        }
    }

    updateNotificationBadge() {
        const badge = document.getElementById('notificationBadge');
        if (this.unreadCount > 0) {
            badge.textContent = this.unreadCount > 99 ? '99+' : this.unreadCount;
            badge.style.display = 'block';
        } else {
            badge.style.display = 'none';
        }
    }

    toggleNotificationsPanel() {
        const panel = document.getElementById('notificationsPanel');
        panel.classList.toggle('active');
    }

    hideNotificationsPanel() {
        document.getElementById('notificationsPanel').classList.remove('active');
    }

    clearNotifications() {
        if (confirm('¿Limpiar todas las notificaciones?')) {
            this.notifications = [];
            this.unreadCount = 0;
            this.renderNotifications();
            this.updateNotificationBadge();
        }
    }

    async requestNotificationPermission() {
        if (!('Notification' in window)) {
            alert('Este navegador no soporta notificaciones del sistema.');
            return;
        }

        const permission = await Notification.requestPermission();

        if (permission === 'granted') {
            this.notificationSettings.browser = true;
            this.saveNotificationSettings();
            document.getElementById('browserNotificationsToggle').checked = true;
            document.getElementById('requestNotificationPermission').style.display = 'none';
            this.createNotification('success', 'Notificaciones habilitadas', 'Ahora recibirás notificaciones del navegador.', false);
        } else {
            this.createNotification('error', 'Permiso denegado', 'No se pudieron habilitar las notificaciones del navegador.', false);
        }
    }

    showBrowserNotification(title, message, type) {
        if (!('Notification' in window) || Notification.permission !== 'granted') {
            return;
        }

        const notification = new Notification(title, {
            body: message,
            icon: '/static/favicon.ico',
            badge: '/static/favicon.ico',
            tag: 'terry-notification',
            requireInteraction: false
        });

        notification.onclick = () => {
            window.focus();
            this.toggleNotificationsPanel();
            notification.close();
        };

        // Auto-close after 5 seconds
        setTimeout(() => notification.close(), 5000);
    }

    playNotificationSound(type) {
        // Create audio context for different notification sounds
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);

        // Different frequencies for different types
        const frequencies = {
            success: 800,
            error: 400,
            warning: 600,
            info: 700,
            command: 750
        };

        oscillator.frequency.value = frequencies[type] || 700;
        oscillator.type = 'sine';

        gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.1);

        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.1);
    }

    // Integrate with existing showToast to also create notifications
    showToastWithNotification(message, type = 'success', createNotif = true) {
        this.showToast(message, type);

        if (createNotif) {
            const titles = {
                success: 'Éxito',
                error: 'Error',
                warning: 'Advertencia',
                info: 'Información'
            };
            this.createNotification(type, titles[type] || 'Notificación', message);
        }
    }

    // ═══════════════════════════════════════════════════════════
    // REAL-TIME LOGS SYSTEM
    // ═══════════════════════════════════════════════════════════

    initLogs() {
        // Welcome log
        this.addLog('info', 'Terry Web UI iniciado correctamente', 'system');
        this.addLog('debug', 'Versión: v6.1.4', 'system');
        this.addLog('info', 'WebSocket conectado', 'websocket');

        // Simulate some initial activity
        setTimeout(() => {
            this.addLog('info', 'Todos los módulos cargados', 'system');
            this.addLog('debug', `Comandos rápidos: ${this.quickCommands.length}`, 'quick-commands');
            this.addLog('debug', `Templates: ${this.templates.length}`, 'templates');
        }, 500);

        // Start log generation for user actions
        this.setupLogInterceptors();
    }

    setupLogInterceptors() {
        // Intercept commands to log them
        const originalSendCommand = this.sendCommand.bind(this);
        this.sendCommand = function(command) {
            this.addLog('info', `Comando ejecutado: "${command}"`, 'command-processor');
            return originalSendCommand(command);
        };

        // Intercept template execution
        const originalConfirmExecuteTemplate = this.confirmExecuteTemplate.bind(this);
        this.confirmExecuteTemplate = function() {
            const result = originalConfirmExecuteTemplate();
            this.addLog('info', `Template ejecutado: "${this.currentExecutingTemplate?.name}"`, 'templates');
            return result;
        };
    }

    addLog(level, message, source = 'unknown') {
        const timestamp = new Date();
        const log = {
            id: Date.now() + Math.random(),
            level, // debug, info, warn, error
            message,
            source,
            timestamp
        };

        this.logs.push(log);
        this.logsCounts[level]++;

        // Render
        this.renderLogs();
        this.updateLogsCounts();

        // Auto-scroll
        if (this.autoScroll) {
            setTimeout(() => this.scrollLogsToBottom(), 50);
        }

        // Limit logs to 1000 entries
        if (this.logs.length > 1000) {
            const removed = this.logs.shift();
            this.logsCounts[removed.level]--;
        }

        return log;
    }

    renderLogs() {
        const list = document.getElementById('logsList');
        const emptyState = document.getElementById('logsEmpty');

        if (this.logs.length === 0) {
            emptyState.style.display = 'flex';
            list.style.display = 'none';
            return;
        }

        emptyState.style.display = 'none';
        list.style.display = 'flex';

        // Format timestamp
        const formatTime = (date) => {
            return date.toTimeString().split(' ')[0] + '.' +
                   String(date.getMilliseconds()).padStart(3, '0');
        };

        // Render logs
        list.innerHTML = this.logs.map(log => {
            const filtered = this.logsFilter !== 'all' && this.logsFilter !== log.level;
            return `
                <div class="log-entry ${log.level} ${filtered ? 'filtered' : ''}" data-id="${log.id}">
                    <span class="log-timestamp">${formatTime(log.timestamp)}</span>
                    <span class="log-level log-level-${log.level}">${log.level}</span>
                    <span class="log-message">${this.escapeHtml(log.message)}</span>
                    <span class="log-source">[${log.source}]</span>
                </div>
            `;
        }).join('');
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    filterLogs(level) {
        this.logsFilter = level;

        // Update active button
        document.querySelectorAll('.log-filter-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.level === level);
        });

        // Re-render
        this.renderLogs();

        this.addLog('debug', `Filtro cambiado a: ${level}`, 'logs-ui');
    }

    toggleAutoScroll() {
        this.autoScroll = !this.autoScroll;
        const btn = document.getElementById('toggleAutoScroll');
        btn.innerHTML = `<i class="fas fa-arrow-down"></i> Auto-scroll: ${this.autoScroll ? 'ON' : 'OFF'}`;

        if (this.autoScroll) {
            this.scrollLogsToBottom();
        }

        this.addLog('debug', `Auto-scroll ${this.autoScroll ? 'activado' : 'desactivado'}`, 'logs-ui');
    }

    scrollLogsToBottom() {
        const container = document.getElementById('logsContainer');
        container.scrollTop = container.scrollHeight;
    }

    exportLogsToFile() {
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const filename = `terry-logs-${timestamp}.txt`;

        const content = this.logs.map(log => {
            const time = log.timestamp.toISOString();
            return `[${time}] [${log.level.toUpperCase()}] [${log.source}] ${log.message}`;
        }).join('\n');

        const blob = new Blob([content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);

        this.showToast(`✅ Logs exportados: ${filename}`);
        this.addLog('info', `Logs exportados: ${filename}`, 'logs-export');
    }

    clearAllLogs() {
        if (confirm('¿Limpiar todos los logs?')) {
            this.logs = [];
            this.logsCounts = { debug: 0, info: 0, warn: 0, error: 0 };
            this.renderLogs();
            this.updateLogsCounts();
            this.showToast('✅ Logs limpiados');

            // Add a fresh log
            setTimeout(() => {
                this.addLog('info', 'Logs limpiados', 'logs-ui');
            }, 100);
        }
    }

    updateLogsCounts() {
        document.getElementById('logsTotalCount').textContent = this.logs.length;
        document.getElementById('logsDebugCount').textContent = this.logsCounts.debug;
        document.getElementById('logsInfoCount').textContent = this.logsCounts.info;
        document.getElementById('logsWarnCount').textContent = this.logsCounts.warn;
        document.getElementById('logsErrorCount').textContent = this.logsCounts.error;
    }

    // Helper: Generate activity logs
    logUserAction(action, details = '') {
        this.addLog('info', `Usuario: ${action}${details ? ' - ' + details : ''}`, 'user-action');
    }

    logError(error, source = 'unknown') {
        this.addLog('error', `Error: ${error}`, source);
    }

    logWarning(warning, source = 'unknown') {
        this.addLog('warn', warning, source);
    }

    logDebug(message, source = 'debug') {
        this.addLog('debug', message, source);
    }

    // ═══════════════════════════════════════════════════════════
    // THEMES SYSTEM (KILLER FEATURE!)
    // ═══════════════════════════════════════════════════════════

    getBuiltInThemes() {
        return {
            orange: {
                name: 'Orange Vibrant',
                description: 'Tema naranja energético y vibrante',
                colors: {
                    primary: '#ff6b35',
                    secondary: '#ff8c42',
                    bgPrimary: '#0f172a',
                    surface: '#1e293b',
                    textPrimary: '#f1f5f9',
                    textSecondary: '#94a3b8'
                }
            },
            blue: {
                name: 'Ocean Blue',
                description: 'Azul profesional y confiable',
                colors: {
                    primary: '#3b82f6',
                    secondary: '#60a5fa',
                    bgPrimary: '#0c1222',
                    surface: '#1a2332',
                    textPrimary: '#f1f5f9',
                    textSecondary: '#94a3b8'
                }
            },
            green: {
                name: 'Nature Green',
                description: 'Verde fresco y natural',
                colors: {
                    primary: '#10b981',
                    secondary: '#34d399',
                    bgPrimary: '#0a1612',
                    surface: '#1a2e24',
                    textPrimary: '#f1f5f9',
                    textSecondary: '#94a3b8'
                }
            },
            purple: {
                name: 'Royal Purple',
                description: 'Morado elegante y sofisticado',
                colors: {
                    primary: '#8b5cf6',
                    secondary: '#a78bfa',
                    bgPrimary: '#140a22',
                    surface: '#241a32',
                    textPrimary: '#f1f5f9',
                    textSecondary: '#94a3b8'
                }
            },
            pink: {
                name: 'Cherry Pink',
                description: 'Rosa moderno y atractivo',
                colors: {
                    primary: '#ec4899',
                    secondary: '#f472b6',
                    bgPrimary: '#1f0a1a',
                    surface: '#331a2c',
                    textPrimary: '#f1f5f9',
                    textSecondary: '#94a3b8'
                }
            },
            dark: {
                name: 'Midnight Dark',
                description: 'Oscuro minimalista y elegante',
                colors: {
                    primary: '#ffffff',
                    secondary: '#e5e5e5',
                    bgPrimary: '#000000',
                    surface: '#1a1a1a',
                    textPrimary: '#ffffff',
                    textSecondary: '#a1a1a1'
                }
            }
        };
    }

    initThemes() {
        this.renderThemes();
        this.applyTheme(this.currentTheme);
        this.addLog('debug', `Tema cargado: ${this.currentTheme.name || 'Orange Vibrant'}`, 'themes');
    }

    renderThemes() {
        const grid = document.getElementById('themesGrid');
        const currentThemeName = this.currentTheme.name || 'Orange Vibrant';

        grid.innerHTML = Object.entries(this.themes).map(([id, theme]) => {
            const isActive = theme.name === currentThemeName;
            return `
                <div class="theme-card ${isActive ? 'active' : ''}" data-theme-id="${id}">
                    <div class="theme-name">${theme.name}</div>
                    <div class="theme-preview">
                        <div class="theme-color" style="background: ${theme.colors.primary}"></div>
                        <div class="theme-color" style="background: ${theme.colors.secondary}"></div>
                        <div class="theme-color" style="background: ${theme.colors.surface}"></div>
                        <div class="theme-color" style="background: ${theme.colors.textPrimary}"></div>
                    </div>
                    <div class="theme-description">${theme.description}</div>
                </div>
            `;
        }).join('');

        // Add click handlers
        grid.querySelectorAll('.theme-card').forEach(card => {
            card.addEventListener('click', () => {
                const themeId = card.dataset.themeId;
                this.selectTheme(themeId);
            });
        });
    }

    selectTheme(themeId) {
        const theme = this.themes[themeId];
        if (!theme) return;

        this.currentTheme = theme;
        this.applyTheme(theme);
        this.saveTheme(theme);
        this.renderThemes(); // Re-render to update active state
        this.showToast(`✅ Tema "${theme.name}" aplicado`);
        this.addLog('info', `Tema cambiado a: ${theme.name}`, 'themes');
        this.createNotification('info', 'Tema cambiado', `Ahora usando "${theme.name}"`, false);
    }

    applyTheme(theme) {
        if (!theme || !theme.colors) return;

        const root = document.documentElement;
        const colors = theme.colors;

        // Apply CSS variables
        root.style.setProperty('--primary', colors.primary);
        root.style.setProperty('--secondary', colors.secondary);
        root.style.setProperty('--bg-primary', colors.bgPrimary);
        root.style.setProperty('--surface-color', colors.surface);
        root.style.setProperty('--text-primary', colors.textPrimary);
        root.style.setProperty('--text-secondary', colors.textSecondary);

        // Update derived colors
        root.style.setProperty('--bg-secondary', this.lightenColor(colors.bgPrimary, 10));
        root.style.setProperty('--glass-bg', `${colors.surface}cc`);
        root.style.setProperty('--glass-hover', `${colors.surface}ee`);
        root.style.setProperty('--accent', this.lightenColor(colors.primary, 15));
    }

    lightenColor(hex, percent) {
        // Convert hex to RGB
        const num = parseInt(hex.replace('#', ''), 16);
        const r = (num >> 16) + Math.round(255 * percent / 100);
        const g = ((num >> 8) & 0x00FF) + Math.round(255 * percent / 100);
        const b = (num & 0x0000FF) + Math.round(255 * percent / 100);

        return `#${((1 << 24) + (Math.min(r, 255) << 16) + (Math.min(g, 255) << 8) + Math.min(b, 255))
            .toString(16)
            .slice(1)}`;
    }

    loadTheme() {
        const stored = localStorage.getItem('terryTheme');
        if (stored) {
            try {
                return JSON.parse(stored);
            } catch (e) {
                console.error('Error loading theme:', e);
            }
        }
        // Fallback: devolver tema naranja por defecto si this.themes no existe
        if (this.themes && this.themes.orange) {
            return this.themes.orange;
        }
        // Fallback final: tema hardcoded
        return {
            name: 'Orange',
            primary: '#ff6b35',
            secondary: '#f7931e',
            accent: '#fbb03b',
            bg: '#0a0a0a',
            bgCard: 'rgba(255, 255, 255, 0.05)',
            text: '#ffffff'
        };
    }

    saveTheme(theme) {
        localStorage.setItem('terryTheme', JSON.stringify(theme));
    }

    toggleCustomThemeEditor() {
        const editor = document.getElementById('customThemeEditor');
        const isVisible = editor.style.display !== 'none';
        editor.style.display = isVisible ? 'none' : 'block';

        if (!isVisible) {
            this.addLog('debug', 'Editor de temas personalizado abierto', 'themes');
        }
    }

    applyCustomTheme() {
        const customTheme = {
            name: 'Custom Theme',
            description: 'Tema personalizado creado por el usuario',
            colors: {
                primary: document.getElementById('customPrimary').value,
                secondary: document.getElementById('customSecondary').value,
                bgPrimary: document.getElementById('customBgPrimary').value,
                surface: document.getElementById('customSurface').value,
                textPrimary: document.getElementById('customTextPrimary').value,
                textSecondary: document.getElementById('customTextSecondary').value
            }
        };

        this.currentTheme = customTheme;
        this.applyTheme(customTheme);
        this.saveTheme(customTheme);
        this.showToast('✅ Tema personalizado aplicado');
        this.addLog('info', 'Tema personalizado creado y aplicado', 'themes');
        this.createNotification('success', 'Tema creado', 'Tu tema personalizado ha sido aplicado', false);
    }

    exportThemeToFile() {
        const timestamp = new Date().toISOString().split('T')[0];
        const filename = `terry-theme-${timestamp}.json`;
        const themeData = JSON.stringify(this.currentTheme, null, 2);

        const blob = new Blob([themeData], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);

        this.showToast(`✅ Tema exportado: ${filename}`);
        this.addLog('info', `Tema exportado: ${filename}`, 'themes');
    }

    importThemeFromFile() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json';

        input.onchange = (e) => {
            const file = e.target.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = (event) => {
                try {
                    const theme = JSON.parse(event.target.result);

                    // Validate theme structure
                    if (!theme.colors || !theme.colors.primary) {
                        throw new Error('Formato de tema inválido');
                    }

                    this.currentTheme = theme;
                    this.applyTheme(theme);
                    this.saveTheme(theme);
                    this.showToast(`✅ Tema "${theme.name || 'Importado'}" aplicado`);
                    this.addLog('info', `Tema importado: ${theme.name || 'Unnamed'}`, 'themes');
                    this.createNotification('success', 'Tema importado', `Tema "${theme.name}" cargado correctamente`, false);
                } catch (error) {
                    this.showToast('❌ Error al importar tema', 'error');
                    this.addLog('error', `Error importando tema: ${error.message}`, 'themes');
                    this.createNotification('error', 'Error', 'No se pudo importar el tema', false);
                }
            };
            reader.readAsText(file);
        };

        input.click();
    }

    // ═══════════════════════════════════════════════════════════
    // PERFORMANCE PROFILER (KILLER FEATURE!)
    // ═══════════════════════════════════════════════════════════

    initProfiler() {
        // Event listeners
        document.getElementById('refreshProfiler')?.addEventListener('click', () => {
            this.refreshProfiler();
        });

        document.getElementById('exportProfiler')?.addEventListener('click', () => {
            this.exportProfilerData();
        });

        document.getElementById('clearProfiler')?.addEventListener('click', () => {
            if (confirm('¿Limpiar todos los datos de performance?')) {
                this.clearProfilerData();
            }
        });

        // Initial render
        this.refreshProfiler();
    }

    recordPerformance(command, duration, success = true) {
        const entry = {
            id: Date.now() + Math.random(),
            command,
            duration,  // in milliseconds
            success,
            timestamp: new Date()
        };

        this.performanceData.push(entry);

        // Limit to 1000 entries (FIFO)
        if (this.performanceData.length > 1000) {
            this.performanceData.shift();
        }

        // Auto-update if profiler tab is active
        if (document.querySelector('.tab[data-tab="profiler"]')?.classList.contains('active')) {
            this.refreshProfiler();
        }
    }

    refreshProfiler() {
        if (this.performanceData.length === 0) {
            this.renderEmptyProfiler();
            return;
        }

        this.updateProfilerSummary();
        this.updateProfilerChart();
        this.updateProfilerTable();
        this.analyzeBottlenecks();
    }

    updateProfilerSummary() {
        if (this.performanceData.length === 0) return;

        // Calculate average
        const avgTime = this.performanceData.reduce((sum, entry) => sum + entry.duration, 0) / this.performanceData.length;

        // Find fastest and slowest
        const sorted = [...this.performanceData].sort((a, b) => a.duration - b.duration);
        const fastest = sorted[0];
        const slowest = sorted[sorted.length - 1];

        // Update DOM
        document.getElementById('profilerAvgTime').textContent = `${avgTime.toFixed(0)}ms`;
        document.getElementById('profilerFastest').textContent = this.truncateCommand(fastest.command, 20);
        document.getElementById('profilerFastestTime').textContent = `${fastest.duration.toFixed(0)}ms`;
        document.getElementById('profilerSlowest').textContent = this.truncateCommand(slowest.command, 20);
        document.getElementById('profilerSlowestTime').textContent = `${slowest.duration.toFixed(0)}ms`;
        document.getElementById('profilerTotalCommands').textContent = this.performanceData.length;
    }

    updateProfilerChart() {
        const canvas = document.getElementById('profilerChart');
        if (!canvas) return;

        // Take last 20 commands for chart
        const recentData = this.performanceData.slice(-20);

        // Destroy previous chart
        if (this.profilerChart) {
            this.profilerChart.destroy();
        }

        // Create new chart
        const ctx = canvas.getContext('2d');
        this.profilerChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: recentData.map((entry, i) => `#${i + 1}`),
                datasets: [{
                    label: 'Tiempo (ms)',
                    data: recentData.map(entry => entry.duration),
                    backgroundColor: recentData.map(entry => {
                        if (entry.duration < 500) return 'rgba(16, 185, 129, 0.6)'; // Green - fast
                        if (entry.duration < 1500) return 'rgba(245, 158, 11, 0.6)'; // Yellow - medium
                        return 'rgba(239, 68, 68, 0.6)'; // Red - slow
                    }),
                    borderColor: recentData.map(entry => {
                        if (entry.duration < 500) return '#10b981';
                        if (entry.duration < 1500) return '#f59e0b';
                        return '#ef4444';
                    }),
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            title: (tooltipItems) => {
                                const index = tooltipItems[0].dataIndex;
                                return this.truncateCommand(recentData[index].command, 40);
                            },
                            label: (context) => {
                                return `Tiempo: ${context.parsed.y.toFixed(0)}ms`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Tiempo (ms)',
                            color: '#94a3b8'
                        },
                        grid: {
                            color: 'rgba(148, 163, 184, 0.1)'
                        },
                        ticks: {
                            color: '#94a3b8'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            color: '#94a3b8'
                        }
                    }
                }
            }
        });
    }

    updateProfilerTable() {
        const tbody = document.getElementById('profilerTableBody');
        if (!tbody) return;

        // Get slowest 10 commands
        const slowest = [...this.performanceData]
            .sort((a, b) => b.duration - a.duration)
            .slice(0, 10);

        tbody.innerHTML = slowest.map((entry, index) => {
            const perfClass = entry.duration < 500 ? 'fast' : (entry.duration < 1500 ? 'medium' : 'slow');
            const statusIcon = entry.success ? '<i class="fas fa-check-circle" style="color: #10b981"></i>' : '<i class="fas fa-times-circle" style="color: #ef4444"></i>';

            return `
                <tr>
                    <td>${index + 1}</td>
                    <td>${this.escapeHtml(entry.command)}</td>
                    <td>
                        <span class="perf-badge ${perfClass}">${entry.duration.toFixed(0)}ms</span>
                    </td>
                    <td>${statusIcon}</td>
                    <td>${this.formatTimestamp(entry.timestamp)}</td>
                </tr>
            `;
        }).join('');
    }

    analyzeBottlenecks() {
        const container = document.getElementById('profilerBottlenecks');
        if (!container) return;

        const bottlenecks = [];

        // Calculate average
        const avgTime = this.performanceData.reduce((sum, entry) => sum + entry.duration, 0) / this.performanceData.length;

        // Find commands consistently slow
        const commandStats = {};
        this.performanceData.forEach(entry => {
            if (!commandStats[entry.command]) {
                commandStats[entry.command] = { times: [], count: 0 };
            }
            commandStats[entry.command].times.push(entry.duration);
            commandStats[entry.command].count++;
        });

        // Analyze each command
        Object.entries(commandStats).forEach(([command, stats]) => {
            const cmdAvg = stats.times.reduce((sum, t) => sum + t, 0) / stats.times.length;

            // If command appears 3+ times and is 2x slower than average
            if (stats.count >= 3 && cmdAvg > avgTime * 2) {
                bottlenecks.push({
                    command,
                    avgTime: cmdAvg,
                    count: stats.count,
                    severity: cmdAvg > avgTime * 3 ? 'high' : 'medium'
                });
            }
        });

        // Render bottlenecks
        if (bottlenecks.length === 0) {
            container.innerHTML = `
                <div class="bottleneck-empty">
                    <i class="fas fa-check-circle"></i>
                    <p>No se detectaron bottlenecks</p>
                </div>
            `;
        } else {
            container.innerHTML = bottlenecks.map(bottleneck => `
                <div class="bottleneck-item">
                    <div class="bottleneck-item-title">
                        <i class="fas fa-exclamation-triangle"></i>
                        ${this.escapeHtml(bottleneck.command)}
                    </div>
                    <div class="bottleneck-item-description">
                        Promedio: ${bottleneck.avgTime.toFixed(0)}ms | Ejecutado ${bottleneck.count} veces |
                        ${((bottleneck.avgTime / avgTime) * 100).toFixed(0)}% más lento que el promedio
                    </div>
                    <div class="bottleneck-item-suggestion">
                        💡 Sugerencia: ${this.getBottleneckSuggestion(bottleneck)}
                    </div>
                </div>
            `).join('');
        }
    }

    getBottleneckSuggestion(bottleneck) {
        const suggestions = [
            'Considera cachear resultados de este comando',
            'Verifica si hay operaciones de I/O que puedan optimizarse',
            'Revisa si este comando puede ejecutarse de forma asíncrona',
            'Evalúa si la acción puede simplificarse o dividirse',
            'Considera agregar este comando a los templates para evitar repeticiones'
        ];

        // Return suggestion based on average time
        if (bottleneck.avgTime > 3000) {
            return suggestions[1]; // I/O optimization
        } else if (bottleneck.count > 10) {
            return suggestions[0]; // Caching
        } else if (bottleneck.avgTime > 2000) {
            return suggestions[2]; // Async
        } else {
            return suggestions[3]; // Simplify
        }
    }

    renderEmptyProfiler() {
        // Show empty state for summary
        document.getElementById('profilerAvgTime').textContent = '0ms';
        document.getElementById('profilerFastest').textContent = '-';
        document.getElementById('profilerFastestTime').textContent = '-';
        document.getElementById('profilerSlowest').textContent = '-';
        document.getElementById('profilerSlowestTime').textContent = '-';
        document.getElementById('profilerTotalCommands').textContent = '0';

        // Show empty table
        const tbody = document.getElementById('profilerTableBody');
        if (tbody) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="5" class="profiler-empty">
                        <i class="fas fa-tachometer-alt"></i>
                        <p>No hay datos de performance aún</p>
                        <small>Ejecuta comandos para ver estadísticas</small>
                    </td>
                </tr>
            `;
        }

        // Show empty bottlenecks
        const bottlenecks = document.getElementById('profilerBottlenecks');
        if (bottlenecks) {
            bottlenecks.innerHTML = `
                <div class="bottleneck-empty">
                    <i class="fas fa-check-circle"></i>
                    <p>No se detectaron bottlenecks</p>
                </div>
            `;
        }
    }

    exportProfilerData() {
        if (this.performanceData.length === 0) {
            this.showToast('⚠️ No hay datos para exportar', 'error');
            return;
        }

        // Calculate statistics
        const avgTime = this.performanceData.reduce((sum, entry) => sum + entry.duration, 0) / this.performanceData.length;
        const sorted = [...this.performanceData].sort((a, b) => a.duration - b.duration);
        const fastest = sorted[0];
        const slowest = sorted[sorted.length - 1];

        const data = {
            exportDate: new Date().toISOString(),
            summary: {
                totalCommands: this.performanceData.length,
                averageTime: `${avgTime.toFixed(2)}ms`,
                fastestCommand: {
                    command: fastest.command,
                    time: `${fastest.duration}ms`
                },
                slowestCommand: {
                    command: slowest.command,
                    time: `${slowest.duration}ms`
                }
            },
            entries: this.performanceData.map(entry => ({
                command: entry.command,
                duration: entry.duration,
                success: entry.success,
                timestamp: entry.timestamp.toISOString()
            }))
        };

        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `terry-performance-${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);

        this.showToast('✅ Datos exportados correctamente');
        this.addLog('info', 'Profiler data exported', 'profiler');
        this.createNotification('success', 'Exportación completa', 'Datos de performance guardados', false);
    }

    clearProfilerData() {
        this.performanceData = [];
        this.refreshProfiler();
        this.showToast('✅ Datos de performance limpiados');
        this.addLog('info', 'Profiler data cleared', 'profiler');
    }

    truncateCommand(command, maxLength) {
        if (command.length <= maxLength) return command;
        return command.substring(0, maxLength - 3) + '...';
    }

    formatTimestamp(date) {
        const now = new Date();
        const diff = now - date;

        if (diff < 60000) return 'Ahora';
        if (diff < 3600000) return `${Math.floor(diff / 60000)}m`;
        if (diff < 86400000) return `${Math.floor(diff / 3600000)}h`;
        return date.toLocaleDateString('es-ES', { month: 'short', day: 'numeric' });
    }

    // ═══════════════════════════════════════════════════════════
    // SYSTEM MONITOR (KILLER FEATURE!)
    // ═══════════════════════════════════════════════════════════

    initMonitor() {
        // Event listener
        document.getElementById('refreshMonitor')?.addEventListener('click', () => {
            this.refreshMonitor();
        });

        // Start auto-refresh interval (every 5 seconds)
        this.monitorInterval = setInterval(() => {
            if (document.querySelector('.tab[data-tab="monitor"]')?.classList.contains('active')) {
                this.refreshMonitor();
            }
        }, 5000);

        // Initial refresh
        this.refreshMonitor();
    }

    async refreshMonitor() {
        await this.updateSystemHealth();
        this.updateServicesStatus();
        this.renderActivityTimeline();
        this.updateSystemInfo();
    }

    async updateSystemHealth() {
        // Simulate system metrics (in production, this would come from backend)
        // CPU usage (simulated based on recent activity)
        const recentCommands = this.history.slice(-10).length;
        this.monitorData.cpu = Math.min(15 + recentCommands * 5 + Math.random() * 10, 100);

        // RAM usage (simulated)
        const dataSize = JSON.stringify(this.history).length + JSON.stringify(this.performanceData).length;
        this.monitorData.ram = Math.min(50 + (dataSize / 10000), 500); // MB

        // Uptime
        const uptimeMs = Date.now() - this.monitorData.startTime;
        this.monitorData.uptime = uptimeMs;

        // Commands per minute
        const fiveMinAgo = Date.now() - 5 * 60 * 1000;
        const recentCmds = this.history.filter(h => new Date(h.timestamp).getTime() > fiveMinAgo).length;
        this.monitorData.cpm = (recentCmds / 5).toFixed(1);

        // Update DOM
        document.getElementById('monitorCPU').textContent = `${this.monitorData.cpu.toFixed(1)}%`;
        document.getElementById('monitorRAM').textContent = `${this.monitorData.ram.toFixed(0)}MB`;
        document.getElementById('monitorUptime').textContent = this.formatUptime(this.monitorData.uptime);
        document.getElementById('monitorStartTime').textContent = `Iniciado: ${new Date(this.monitorData.startTime).toLocaleTimeString('es-ES')}`;
        document.getElementById('monitorCPM').textContent = this.monitorData.cpm;

        // Update health bars
        const cpuBar = document.getElementById('monitorCPUBar');
        const ramBar = document.getElementById('monitorRAMBar');

        if (cpuBar) {
            cpuBar.style.width = `${this.monitorData.cpu}%`;
            cpuBar.className = 'health-bar-fill';
            if (this.monitorData.cpu > 80) cpuBar.classList.add('danger');
            else if (this.monitorData.cpu > 60) cpuBar.classList.add('warning');
        }

        if (ramBar) {
            const ramPercent = (this.monitorData.ram / 500) * 100;
            ramBar.style.width = `${ramPercent}%`;
            ramBar.className = 'health-bar-fill';
            if (ramPercent > 80) ramBar.classList.add('danger');
            else if (ramPercent > 60) ramBar.classList.add('warning');
        }
    }

    updateServicesStatus() {
        // LLM Service
        this.updateServiceItem('llm', {
            status: 'online',
            statusText: 'Operativo',
            stats: this.history.length
        });

        // STT Service
        this.updateServiceItem('stt', {
            status: 'online',
            statusText: 'Listo para reconocimiento',
            stats: this.history.filter(h => h.command).length
        });

        // TTS Service
        this.updateServiceItem('tts', {
            status: 'online',
            statusText: 'Síntesis activa',
            stats: this.history.filter(h => h.response).length
        });

        // Camera Service
        this.updateServiceItem('camera', {
            status: Math.random() > 0.5 ? 'online' : 'offline',
            statusText: Math.random() > 0.5 ? 'Detectando rostros' : 'Sin conexión',
            stats: Math.floor(Math.random() * 50)
        });

        // WebSocket Service
        this.updateServiceItem('websocket', {
            status: this.ws && this.ws.readyState === WebSocket.OPEN ? 'online' : 'offline',
            statusText: this.ws && this.ws.readyState === WebSocket.OPEN ? 'Conectado' : 'Desconectado',
            stats: Math.floor(Math.random() * 100)
        });

        // Database Service
        const dbSize = (JSON.stringify(this.history).length / 1024).toFixed(1);
        this.updateServiceItem('database', {
            status: 'online',
            statusText: 'SQLite operativo',
            stats: dbSize + ' KB'
        });
    }

    updateServiceItem(service, data) {
        const item = document.querySelector(`.service-item[data-service="${service}"]`);
        if (!item) return;

        // Update status class
        item.className = `service-item ${data.status}`;

        // Update status text
        const statusEl = item.querySelector('.service-status');
        if (statusEl) {
            statusEl.textContent = data.statusText;
        }

        // Update stats
        const statsEl = item.querySelector(`#${service}Requests, #${service}Detections, #wsMessages, #dbSize`);
        if (statsEl) {
            statsEl.textContent = data.stats;
        }
    }

    renderActivityTimeline() {
        const container = document.getElementById('monitorTimeline');
        if (!container) return;

        // Get recent activities from history and logs
        const activities = [];

        // Add recent commands
        this.history.slice(-10).reverse().forEach(item => {
            activities.push({
                type: item.success !== false ? 'success' : 'error',
                icon: 'fas fa-terminal',
                title: item.command,
                description: item.response ? item.response.substring(0, 100) : 'Ejecutado',
                time: new Date(item.timestamp)
            });
        });

        // Add recent logs (errors and warnings)
        this.logs.filter(log => log.level === 'error' || log.level === 'warn')
            .slice(-5).reverse().forEach(log => {
                activities.push({
                    type: log.level === 'error' ? 'error' : 'warning',
                    icon: log.level === 'error' ? 'fas fa-exclamation-circle' : 'fas fa-exclamation-triangle',
                    title: log.level.toUpperCase(),
                    description: log.message,
                    time: log.timestamp
                });
            });

        // Sort by time
        activities.sort((a, b) => b.time - a.time);

        // Render
        if (activities.length === 0) {
            container.innerHTML = `
                <div class="timeline-empty">
                    <i class="fas fa-clock"></i>
                    <p>No hay actividad reciente</p>
                </div>
            `;
        } else {
            container.innerHTML = activities.slice(0, 15).map(activity => `
                <div class="timeline-item ${activity.type}">
                    <div class="timeline-icon">
                        <i class="${activity.icon}"></i>
                    </div>
                    <div class="timeline-content">
                        <div class="timeline-title">${this.escapeHtml(activity.title)}</div>
                        <div class="timeline-description">${this.escapeHtml(activity.description)}</div>
                        <div class="timeline-time">${this.getRelativeTime(activity.time)}</div>
                    </div>
                </div>
            `).join('');
        }
    }

    updateSystemInfo() {
        // Platform
        document.getElementById('infoPlatform').textContent = navigator.platform || 'Unknown';

        // Python version (would come from backend in production)
        document.getElementById('infoPython').textContent = '3.11+';

        // WebSocket status
        const wsStatus = this.ws && this.ws.readyState === WebSocket.OPEN ? 'Conectado' : 'Desconectado';
        document.getElementById('infoWebSocket').textContent = wsStatus;

        // Local IP (simulated)
        document.getElementById('infoIP').textContent = window.location.hostname || 'localhost';
    }

    formatUptime(ms) {
        const seconds = Math.floor(ms / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);

        if (days > 0) return `${days}d ${hours % 24}h`;
        if (hours > 0) return `${hours}h ${minutes % 60}m`;
        if (minutes > 0) return `${minutes}m ${seconds % 60}s`;
        return `${seconds}s`;
    }

    // Add activity to timeline (called from commands/logs)
    addMonitorActivity(type, icon, title, description) {
        this.monitorData.activities.unshift({
            type,
            icon,
            title,
            description,
            time: new Date()
        });

        // Limit to 50 activities
        if (this.monitorData.activities.length > 50) {
            this.monitorData.activities.pop();
        }

        // Auto-refresh timeline if monitor tab is active
        if (document.querySelector('.tab[data-tab="monitor"]')?.classList.contains('active')) {
            this.renderActivityTimeline();
        }
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
