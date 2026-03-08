// MechForge AI - Application Logic (Modular Architecture)
(function () {
  'use strict';

  // ==================== 常量 ====================
  const PARTICLE_COUNT       = 15;
  const WHALE_SPEECH_MAX_LEN = 30;
  const BOOT_COMPLETE_DELAY  = 300;
  const RUNE_COUNT           = 12;
  const RUNE_CHARS = [
    '\u25C8', '\u25C9', '\u25CA', '\u25CB', '\u25CC',
    '\u25CD', '\u25CE', '\u25CF', '\u25D0', '\u25D1',
    '\u25D2', '\u2B21', '\u2B22', '\u25B2', '\u25BC', '\u25C6'
  ];

  // ==================== State ====================
  const state = {
    activeTab:        'chat',
    booted:           false,
    messages:         [],
    knowledgeResults: [],
    caeModel:         null,
    meshData:         null,
    solveResults:     null,
    isAnimating:      false,
    aiService:        null,
    configService:    null
  };

  // ==================== DOM Elements ====================
  // 修复1：补全缺失的 apiSelector / apiButton / apiOptions
  const elements = {
    sidebarIcons:       document.querySelectorAll('.sidebar-icon'),
    tabPanels:          document.querySelectorAll('.tab-panel'),
    bootSequence:       document.getElementById('boot-sequence'),
    chatOutput:         document.getElementById('chat-output'),
    chatInput:          document.getElementById('chat-input'),
    sendBtn:            document.getElementById('send-btn'),
    knowledgeSearch:    document.getElementById('knowledge-search'),
    searchBtn:          document.getElementById('search-btn'),
    searchResults:      document.getElementById('search-results'),
    loadModelBtn:       document.getElementById('load-model-btn'),
    meshBtn:            document.getElementById('mesh-btn'),
    solveBtn:           document.getElementById('solve-btn'),
    visualizeBtn:       document.getElementById('visualize-btn'),
    clearBtn:           document.getElementById('clear-btn'),
    caeCanvas:          document.getElementById('cae-canvas'),
    viewportOverlay:    document.getElementById('viewport-overlay'),
    statusText:         document.getElementById('status-text'),
    modelName:          document.getElementById('model-name'),
    elementCount:       document.getElementById('element-count'),
    nodeCount:          document.getElementById('node-count'),
    windowBtns:         document.querySelectorAll('.window-btn'),
    particlesContainer: document.getElementById('particles'),
    mascotToggle:       document.getElementById('mascot-toggle'),
    mascotWhale:        document.querySelector('.mascot-whale'),
    defaultGear:        document.querySelector('.default-gear'),
    apiSelector:        document.getElementById('api-selector'),
    apiButton:          document.querySelector('[data-status="api"]'),
    apiOptions:         document.querySelectorAll('.api-option')
  };

  // ==================== Boot Sequence ====================
  const bootLines = [
    { text: '[21:04] SYSTEM: Initializing MechForge AI...', delay: 0,    color: '#c8d8e0', cls: 'system'  },
    { text: '> AI Assistant Ready',                          delay: 600,  color: '#00e5ff', cls: 'info'    },
    { text: 'Model: qwen2.5:3b',                            delay: 1000, color: '#00e5ff', cls: 'info'    },
    { text: 'RAG Status: Active',                           delay: 1200, color: '#00e5ff', cls: 'info'    },
    { text: 'API: Ollama',                                  delay: 1400, color: '#00e5ff', cls: 'info'    },
    { text: 'Memory: 42 KB',                                delay: 1600, color: '#00e5ff', cls: 'info'    },
    { text: 'Awaiting input...',                            delay: 2000, color: '#c8d8e0', cls: 'waiting' }
  ];

  // ==================== Initialization ====================
  function init() {
    initServices();
    runBootSequence();
    setupEventListeners();
    initCAECanvas();
    initParticles();
    setupClickSparks();
    registerEventHandlers();
  }

  function initServices() {
    state.aiService     = new AIService(apiClient, eventBus);
    state.configService = new ConfigService(apiClient, eventBus);

    state.configService.init()
      .then(({ config }) => { if (config) updateStatusBar(config); })
      .catch(() => { /* 使用默认值 */ });
  }

  function updateStatusBar(config) {
    const modelEl = document.querySelector('[data-status="model"]');
    const apiEl   = document.querySelector('[data-status="api"]');
    if (modelEl && config.ai) modelEl.textContent = `Model: ${config.ai.model    || 'qwen2.5:3b'}`;
    if (apiEl   && config.ai) apiEl.textContent   = `API: ${config.ai.provider  || 'Ollama'}`;
  }

  function registerEventHandlers() {
    eventBus.on(Events.AI_MESSAGE_SENT,      ({ message }) => console.log('Sent:', message));
    eventBus.on(Events.AI_RESPONSE_RECEIVED, ({ message }) => console.log('Received:', message));
    eventBus.on(Events.AI_ERROR,             ({ error })   => { console.error('AI Error:', error); addSystemMessage(`Error: ${error}`); });
    eventBus.on(Events.CONFIG_LOADED,        ({ config })  => updateStatusBar(config));
    eventBus.on(Events.RAG_ENABLED,          ()            => updateRAGStatus(true));
    eventBus.on(Events.RAG_DISABLED,         ()            => updateRAGStatus(false));
  }

  function updateRAGStatus(enabled) {
    const ragEl = document.querySelector('[data-status="rag"]');
    if (!ragEl) return;
    ragEl.textContent = enabled ? 'RAG: ON' : 'RAG: OFF';
    ragEl.classList.toggle('status-on', enabled);
  }

  // ==================== Boot Sequence ====================
  function runBootSequence() {
    bootLines.forEach((line, index) => {
      setTimeout(() => {
        const lineEl = document.createElement('div');
        lineEl.className = `boot-line ${line.cls}`;
        lineEl.style.color = line.color;
        lineEl.textContent = line.text;
        elements.bootSequence.appendChild(lineEl);

        if (index === bootLines.length - 1) {
          state.booted = true;
          setTimeout(() => {
            const sep = document.createElement('div');
            sep.style.cssText = 'height:1px;background:linear-gradient(90deg,#00e5ff33,transparent);margin:12px 0;';
            elements.bootSequence.appendChild(sep);

            const cursor = document.createElement('div');
            cursor.className = 'boot-line waiting-cursor';
            cursor.innerHTML = '<span class="cursor">_</span>';
            elements.bootSequence.appendChild(cursor);

            createPulseIndicator();
          }, BOOT_COMPLETE_DELAY);
        }
      }, line.delay);
    });
  }

  // ==================== AI 脉冲指示器 ====================
  let pulseIndicator   = null;
  let pulseStatusEl    = null;
  let pulseProgressBar = null;

  function createPulseIndicator() {
    pulseIndicator = document.createElement('div');
    pulseIndicator.className = 'ai-pulse-indicator';
    pulseIndicator.innerHTML = `
      <div class="pulse-wave"></div>
      <div class="pulse-dots">
        <div class="pulse-dot"></div>
        <div class="pulse-dot"></div>
        <div class="pulse-dot"></div>
      </div>
      <span class="pulse-status">Ready</span>
      <div class="response-progress">
        <div class="response-progress-bar"></div>
      </div>
    `;
    elements.bootSequence.appendChild(pulseIndicator);
    pulseStatusEl    = pulseIndicator.querySelector('.pulse-status');
    pulseProgressBar = pulseIndicator.querySelector('.response-progress-bar');
  }

  function showPulseThinking() {
    if (!pulseIndicator) return;
    pulseIndicator.classList.add('active', 'thinking');
    pulseIndicator.classList.remove('responding');
    if (pulseStatusEl)    pulseStatusEl.textContent    = 'AI Thinking...';
    if (pulseProgressBar) pulseProgressBar.style.width = '0%';
  }

  function showPulseResponding(progress = 0) {
    if (!pulseIndicator) return;
    pulseIndicator.classList.add('active', 'responding');
    pulseIndicator.classList.remove('thinking');
    if (pulseStatusEl) pulseStatusEl.textContent = 'AI Responding...';
    if (pulseProgressBar) {
      const current = parseFloat(pulseProgressBar.style.width) || 0;
      pulseProgressBar.style.width = `${Math.min(90, Math.max(current, progress * 0.9))}%`;
    }
  }

  function hidePulseIndicator() {
    if (!pulseIndicator) return;
    if (pulseProgressBar) pulseProgressBar.style.width = '100%';
    setTimeout(() => {
      pulseIndicator.classList.remove('active', 'thinking', 'responding');
      if (pulseStatusEl)    pulseStatusEl.textContent    = 'Ready';
      if (pulseProgressBar) pulseProgressBar.style.width = '0%';
    }, 300);
  }

  // ==================== Event Listeners ====================
  function setupEventListeners() {
    elements.sidebarIcons.forEach(icon => {
      icon.addEventListener('click', () => switchTab(icon.dataset.tab));
      icon.addEventListener('mouseenter', () => {
        const { left, top, width, height } = icon.getBoundingClientRect();
        createHoverSplash(left + width / 2, top + height / 2);
      });
    });

    elements.chatInput?.addEventListener('keypress', e => { if (e.key === 'Enter') sendMessage(); });
    elements.sendBtn?.addEventListener('click', sendMessage);
    elements.mascotToggle?.addEventListener('click', toggleMascot);
    elements.knowledgeSearch?.addEventListener('keypress', e => { if (e.key === 'Enter') performSearch(); });
    elements.searchBtn?.addEventListener('click', performSearch);
    elements.loadModelBtn?.addEventListener('click', loadModel);
    elements.meshBtn?.addEventListener('click', generateMesh);
    elements.solveBtn?.addEventListener('click', runSolve);
    elements.visualizeBtn?.addEventListener('click', visualizeResults);
    elements.clearBtn?.addEventListener('click', clearCAE);

    // 修复2：原来缺失这两行，导致窗口按钮和 API 选择器完全失效
    setupWindowControls();
    setupAPISelector();
  }

  // ==================== 窗口控制 ====================
  // 修复3：整个 setupWindowControls / handleWindowAction 原文件中缺失
  function setupWindowControls() {
    elements.windowBtns.forEach(btn => {
      btn.addEventListener('click', () => handleWindowAction(btn.dataset.action));
    });
  }

  async function handleWindowAction(action) {
    try {
      // PyWebView 通过 js_api 暴露的 API 在 window.pywebview.api
      const api = window.pywebview?.api;
      if (api) {
        switch (action) {
          case 'minimize': await api.minimize(); break;
          case 'maximize': await api.maximize();  break;
          case 'close':    await api.close();     break;
        }
      } else {
        console.log(`[dev] window action: ${action}`);
      }
    } catch (error) {
      console.error('Window action failed:', error);
    }
  }

  // ==================== API 选择器 ====================
  // 修复5：整个 setupAPISelector / selectAPI 原文件中缺失
  let currentAPI = 'ollama';

  function setupAPISelector() {
    if (!elements.apiButton || !elements.apiSelector) {
      console.warn('API selector elements not found, skipping');
      return;
    }

    elements.apiButton.addEventListener('click', e => {
      if (elements.apiSelector.contains(e.target)) return;
      e.preventDefault();
      e.stopPropagation();
      elements.apiSelector.classList.contains('active') ? closeAPISelector() : openAPISelector();
    });

    elements.apiSelector.addEventListener('click', e => {
      const option = e.target.closest('.api-option');
      if (option) { e.preventDefault(); e.stopPropagation(); selectAPI(option.dataset.api); }
    });

    document.addEventListener('click', e => {
      if (elements.apiSelector.classList.contains('active') && !elements.apiButton.contains(e.target)) {
        closeAPISelector();
      }
    });
  }

  function openAPISelector()  { elements.apiSelector.classList.add('active');    elements.apiButton.classList.add('selector-open'); }
  function closeAPISelector() { elements.apiSelector.classList.remove('active'); elements.apiButton.classList.remove('selector-open'); }

  async function selectAPI(api) {
    closeAPISelector();
    if (api === currentAPI) return;
    currentAPI = api;

    document.querySelectorAll('.api-option').forEach(opt => opt.classList.toggle('selected', opt.dataset.api === api));
    elements.apiButton.classList.remove('api-ollama', 'api-gguf');
    elements.apiButton.classList.add(`api-${api}`);

    const apiNames = { ollama: 'Ollama', gguf: 'Local GGUF' };
    const textNode = Array.from(elements.apiButton.childNodes).find(n => n.nodeType === Node.TEXT_NODE);
    if (textNode) textNode.textContent = `API: ${apiNames[api] || api} `;

    try {
      const response = await apiClient.post('/api/config/provider', { provider: api });
      if (response.model) {
        const modelEl = document.querySelector('[data-status="model"]');
        if (modelEl) modelEl.textContent = `Model: ${response.model}`;
      }
      addSystemMessage(`Switched to ${apiNames[api] || api} backend`);
    } catch (error) {
      console.error('Switch failed:', error);
      addSystemMessage(`Failed to switch: ${error.message}`);
    }
  }

  // ==================== Tab 切换 ====================
  function switchTab(tab) {
    state.activeTab = tab;
    elements.sidebarIcons.forEach(icon  => icon.classList.toggle('active', icon.dataset.tab === tab));
    elements.tabPanels.forEach(panel    => panel.classList.toggle('active', panel.id === `${tab}-panel`));
    eventBus.emit(Events.UI_TAB_CHANGED, { tab });
  }

  // ==================== 聊天 ====================
  async function sendMessage() {
    const text = elements.chatInput?.value.trim();
    if (!text || !state.booted || !state.aiService) return;

    elements.chatInput.disabled = true;
    elements.sendBtn.disabled   = true;

    // 修复6：startResonance / showPulseThinking 原文件缺失，现已补全
    startResonance();
    showPulseThinking();

    const btnRect = elements.sendBtn.getBoundingClientRect();
    createSendBurst(btnRect.left + btnRect.width / 2, btnRect.top + btnRect.height / 2);

    const now  = new Date();
    const time = `[${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}]`;
    addMessage('user', text, time);
    elements.chatInput.value = '';

    try {
      let aiMessageEl = null;
      let lastContent = '';
      let charCount   = 0;

      await state.aiService.sendMessageStream(text, (content) => {
        if (!aiMessageEl) {
          showPulseResponding(0);
          aiMessageEl = document.createElement('div');
          aiMessageEl.className = 'chat-message ai slide-in';
          aiMessageEl.innerHTML = '<span class="ai-prefix">&gt;</span>';
          elements.chatOutput.appendChild(aiMessageEl);
        }

        const newContent = content.slice(lastContent.length);
        if (newContent) {
          const span = document.createElement('span');
          span.textContent = newContent;
          aiMessageEl.appendChild(span);
          lastContent  = content;
          charCount   += newContent.length;
          updateWhaleSpeech(content);
          showPulseResponding(charCount / 100);
        }

        elements.chatOutput.scrollTop = elements.chatOutput.scrollHeight;
      });

    } catch (error) {
      addSystemMessage(`Error: ${error.message}`);
    } finally {
      // 修复7：stopResonance / hidePulseIndicator 原文件缺失，现已补全
      stopResonance();
      hidePulseIndicator();
      elements.chatInput.disabled = false;
      elements.sendBtn.disabled   = false;
      elements.chatInput.focus();
    }
  }

  function addMessage(type, text, time) {
    const el = document.createElement('div');
    el.className = `chat-message ${type} slide-in`;
    if (type === 'user') {
      el.innerHTML = `<span class="message-time">${time}</span><span class="message-prefix">&gt;</span> ${escapeHtml(text)}`;
    } else {
      el.innerHTML = text.split('\n').map(line =>
        line.startsWith('>')
          ? `<div><span class="ai-prefix">${escapeHtml(line)}</span></div>`
          : `<div>${escapeHtml(line)}</div>`
      ).join('');
    }
    elements.chatOutput.appendChild(el);
    elements.chatOutput.scrollTop = elements.chatOutput.scrollHeight;
  }

  function addSystemMessage(text) {
    const el = document.createElement('div');
    el.className = 'chat-message ai slide-in';
    el.innerHTML = `<span style="color:#ff4757;">${escapeHtml(text)}</span>`;
    elements.chatOutput.appendChild(el);
    elements.chatOutput.scrollTop = elements.chatOutput.scrollHeight;
  }

  // 修复8：移除从未调用的 showTypingIndicator / removeTypingIndicator 死代码

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  // ==================== 吉祥物 ====================
  let mascotVisible = false;

  function toggleMascot() {
    mascotVisible = !mascotVisible;
    elements.mascotToggle?.classList.toggle('active', mascotVisible);

    // 修复9：mascotWhale / defaultGear 可能为 null，原来无 null 检查
    if (mascotVisible) {
      elements.mascotWhale?.classList.remove('hidden');
      elements.mascotWhale?.classList.add('visible');
      elements.defaultGear?.classList.add('hidden');
    } else {
      elements.mascotWhale?.classList.remove('visible');
      elements.mascotWhale?.classList.add('hidden');
      elements.defaultGear?.classList.remove('hidden');
    }
  }

  // ==================== 数据共鸣效果 ====================
  let runeElements      = [];
  let resonanceInterval = null;

  // 修复10：startResonance / stopResonance 原文件完全缺失
  function startResonance() {
    if (!mascotVisible) return;
    elements.mascotWhale?.classList.add('resonating');
    const container = document.getElementById('rune-container');
    if (container) { container.classList.add('active'); generateRunes(container); }
    resonanceInterval = setInterval(updateRunes, 500);
  }

  function stopResonance() {
    // 修复11：mascotWhale 可能为 null，加可选链
    elements.mascotWhale?.classList.remove('resonating');
    document.getElementById('rune-container')?.classList.remove('active');
    if (resonanceInterval) { clearInterval(resonanceInterval); resonanceInterval = null; }
    const whaleSpeech = document.getElementById('whale-speech');
    if (whaleSpeech) { whaleSpeech.classList.remove('active'); whaleSpeech.textContent = ''; }
  }

  function generateRunes(container) {
    runeElements.forEach(el => el.remove());
    runeElements = [];
    for (let i = 0; i < RUNE_COUNT; i++) {
      const rune  = document.createElement('div');
      rune.className = 'rune-char';
      const angle = (i / RUNE_COUNT) * Math.PI * 2 - Math.PI / 2;
      const r     = 160 + Math.random() * 40;
      rune.style.left           = `${Math.cos(angle) * r + 200}px`;
      rune.style.top            = `${Math.sin(angle) * r + 200}px`;
      rune.style.animationDelay = `${i * 0.1}s`;
      rune.textContent = RUNE_CHARS[Math.floor(Math.random() * RUNE_CHARS.length)];
      container.appendChild(rune);
      runeElements.push(rune);
    }
  }

  function updateRunes() {
    runeElements.forEach(rune => {
      if (Math.random() > 0.7) rune.textContent = RUNE_CHARS[Math.floor(Math.random() * RUNE_CHARS.length)];
    });
  }

  function updateWhaleSpeech(text) {
    const el = document.getElementById('whale-speech');
    if (!el || !mascotVisible) return;
    el.classList.add('active');
    const display = text.length > WHALE_SPEECH_MAX_LEN ? text.substring(0, WHALE_SPEECH_MAX_LEN) + '...' : text;
    el.innerHTML = `${escapeHtml(display)}<span class="typing-cursor"></span>`;
  }

  // ==================== 知识库搜索 ====================
  async function performSearch() {
    const query = elements.knowledgeSearch?.value.trim();
    if (!query) return;

    elements.searchResults.innerHTML = '<div class="result-placeholder">Searching...</div>';

    try {
      const raw = await state.aiService.searchKnowledge(query);
      // 修复12：server 返回 {results:[...]}，原来直接传入对象导致 .length 出错
      const results = Array.isArray(raw) ? raw : (raw?.results ?? []);
      displaySearchResults(results);
    } catch (error) {
      elements.searchResults.innerHTML = `<div class="result-placeholder">Error: ${escapeHtml(error.message)}</div>`;
    }
  }

  function displaySearchResults(results) {
    if (!results || results.length === 0) {
      elements.searchResults.innerHTML = '<div class="result-placeholder">No results found</div>';
      return;
    }
    elements.searchResults.innerHTML = results.map((result, index) => `
      <div class="result-item">
        <div class="result-title">${escapeHtml(result.title || `Result ${index + 1}`)}</div>
        <div class="result-snippet">${escapeHtml(result.content || result.snippet || '')}</div>
        <div class="result-meta">
          <span>Score: ${(result.score || 0).toFixed(2)}</span>
          ${result.source ? `<span>Source: ${escapeHtml(result.source)}</span>` : ''}
        </div>
      </div>
    `).join('');
  }

  // ==================== CAE ====================
  function initCAECanvas() {
    const canvas = elements.caeCanvas;
    // 修复13：canvas 可能为 null，原来直接调用 getContext 会崩溃
    if (!canvas) return;
    const resize = () => {
      canvas.width  = canvas.parentElement.clientWidth;
      canvas.height = canvas.parentElement.clientHeight;
    };
    resize();
    window.addEventListener('resize', resize);
  }

  function loadModel() {
    elements.viewportOverlay?.classList.add('hidden');
    updateCAEStatus('Model Loaded', 'bracket.step', 0, 0);
  }

  function generateMesh() {
    updateCAEStatus('Meshing...', '', 0, 0);
    setTimeout(() => { updateCAEStatus('Mesh Complete', '', 1250, 486); drawMeshPreview(); }, 1000);
  }

  function runSolve() {
    updateCAEStatus('Solving...', '', 1250, 486);
    setTimeout(() => updateCAEStatus('Solve Complete', '', 1250, 486), 2000);
  }

  function visualizeResults() {
    drawStressContour();
    updateCAEStatus('Visualizing', '', 1250, 486);
  }

  function clearCAE() {
    elements.viewportOverlay?.classList.remove('hidden');
    updateCAEStatus('Ready', 'None', 0, 0);
    const canvas = elements.caeCanvas;
    if (canvas) canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height);
  }

  function updateCAEStatus(status, model, elementsCount, nodesCount) {
    // 修复14：原来直接访问无 null 检查，CAE 面板未激活时会崩溃
    if (elements.statusText)   elements.statusText.textContent   = status;
    if (elements.modelName)    elements.modelName.textContent    = model;
    if (elements.elementCount) elements.elementCount.textContent = elementsCount;
    if (elements.nodeCount)    elements.nodeCount.textContent    = nodesCount;
  }

  function drawMeshPreview() {
    const canvas = elements.caeCanvas;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    ctx.strokeStyle = 'rgba(0, 229, 255, 0.5)';
    ctx.lineWidth   = 0.5;
    for (let i = 0; i < 50; i++) {
      const x1 = Math.random() * canvas.width,  y1 = Math.random() * canvas.height;
      const x2 = x1 + (Math.random() - 0.5) * 100, y2 = y1 + (Math.random() - 0.5) * 100;
      ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke();
    }
  }

  function drawStressContour() {
    const canvas = elements.caeCanvas;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const g   = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
    g.addColorStop(0,   'rgba(0, 100, 255, 0.3)');
    g.addColorStop(0.5, 'rgba(0, 255, 100, 0.3)');
    g.addColorStop(1,   'rgba(255, 50, 50, 0.3)');
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
  }

  // ==================== 粒子效果 ====================
  function initParticles() {
    const container = elements.particlesContainer;
    if (!container) return;
    for (let i = 0; i < PARTICLE_COUNT; i++) createParticle(container);
  }

  function createParticle(container) {
    const p   = document.createElement('div');
    p.className = 'particle';
    const dur = Math.random() * 20 + 15;
    const twk = Math.random() * 2  + 1.5;
    p.style.cssText = `
      width:${Math.random() * 3 + 2}px;height:${Math.random() * 3 + 2}px;
      left:${Math.random() * 100}%;top:${Math.random() * 100}%;
      animation:floatParticle ${dur}s linear ${Math.random() * -30}s infinite,
               twinkle ${twk}s ease-in-out infinite
               ${Math.random() > 0.5 ? ',particleTrail 1.5s ease-out infinite' : ''};
    `;
    container.appendChild(p);
  }

  function setupClickSparks() {
    document.addEventListener('click', e => {
      if (e.target.closest('.sidebar-icon, #send-btn, #search-btn, .cae-btn, .window-btn')) {
        createSparks(e.clientX, e.clientY);
      }
    });
  }

  // 提取公共 spark 工厂，消除三处重复代码
  function _createSparkEl(x, y, dx, dy, size, duration) {
    const el = document.createElement('div');
    el.className = 'spark-particle';
    el.style.cssText = `left:${x}px;top:${y}px;--dx:${dx}px;--dy:${dy}px;width:${size}px;height:${size}px;animation-duration:${duration}s;`;
    return el;
  }

  function createSparks(x, y) {
    const container = elements.particlesContainer;
    if (!container) return;
    const count = 8 + Math.floor(Math.random() * 5);
    for (let i = 0; i < count; i++) {
      const angle = Math.random() * Math.PI * 2;
      const dist  = 30 + Math.random() * 50;
      const el = _createSparkEl(x, y, Math.cos(angle)*dist, Math.sin(angle)*dist, 2+Math.random()*3, 0.8);
      container.appendChild(el);
      setTimeout(() => el.remove(), 800);
    }
  }

  function createHoverSplash(x, y) {
    const container = elements.particlesContainer;
    if (!container) return;
    const count = 5 + Math.floor(Math.random() * 4);
    for (let i = 0; i < count; i++) {
      const angle = (Math.PI * 2 / count) * i + Math.random() * 0.5;
      const dist  = 20 + Math.random() * 30;
      const el = _createSparkEl(x, y, Math.cos(angle)*dist, Math.sin(angle)*dist, 2+Math.random()*2, 0.6);
      container.appendChild(el);
      setTimeout(() => el.remove(), 600);
    }
  }

  function createSendBurst(x, y) {
    const container = elements.particlesContainer;
    if (!container) return;
    for (let i = 0; i < 20; i++) {
      const angle  = Math.random() * Math.PI * 2;
      const startD = 40 + Math.random() * 30;
      const endD   = 10 + Math.random() * 20;
      const sx     = x + Math.cos(angle) * startD;
      const sy     = y + Math.sin(angle) * startD;
      const el = _createSparkEl(sx, sy, Math.cos(angle)*(endD-startD), Math.sin(angle)*(endD-startD), 2+Math.random()*3, 0.5);
      el.style.animationTimingFunction = 'cubic-bezier(0.25, 0.46, 0.45, 0.94)';
      container.appendChild(el);
      setTimeout(() => el.remove(), 500);
    }
  }

  // ==================== 启动 ====================
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();