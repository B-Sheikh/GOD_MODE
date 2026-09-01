// GOD MODE 75-Model Swarm - Desktop & Web Frontend Engine

// Safe Electron IPC Detection
let ipcRenderer = null;
try {
  if (typeof window !== 'undefined' && window.require) {
    const electron = window.require('electron');
    ipcRenderer = electron.ipcRenderer;
  }
} catch (e) {
  console.log('Running in browser web mode (Electron not detected)');
}

const API_BASE = window.location.origin.includes('localhost') || window.location.origin.includes('127.0.0.1')
  ? window.location.origin
  : 'http://localhost:8000';

// DOM Elements
const chatHistory = document.getElementById('chat-history');
const promptInput = document.getElementById('prompt-input');
const sendBtn = document.getElementById('send-btn');
const welcomeCard = document.getElementById('welcome-card');
const clearChatBtn = document.getElementById('clear-chat-btn');
const exportChatBtn = document.getElementById('export-chat-btn');
const themeToggleBtn = document.getElementById('theme-toggle-btn');
const swarmStatusPill = document.getElementById('swarm-status-pill');
const statusPillText = document.getElementById('status-pill-text');
const clusterIndicator = document.getElementById('cluster-indicator');

// Tabs
const navTabs = document.querySelectorAll('.tab-btn');
const viewSections = document.querySelectorAll('.view-section');

// Window Controls
const windowControls = document.getElementById('window-controls');
const minBtn = document.getElementById('min-btn');
const maxBtn = document.getElementById('max-btn');
const closeBtn = document.getElementById('close-btn');

// Network View Elements
const nodesOrchestrator = document.getElementById('nodes-orchestrator');
const nodesCoder = document.getElementById('nodes-coder');
const nodesGeneral = document.getElementById('nodes-general');
const nodesVision = document.getElementById('nodes-vision');
const svgLines = document.getElementById('network-lines');
const simulatePulseBtn = document.getElementById('simulate-pulse-btn');
const nodeInspector = document.getElementById('node-inspector-modal');
const inspClose = document.getElementById('insp-close');
const inspTitle = document.getElementById('insp-title');
const inspBadge = document.getElementById('insp-badge');
const inspModel = document.getElementById('insp-model');
const inspProvider = document.getElementById('insp-provider');
const inspTier = document.getElementById('insp-tier');

// Model Registry Elements
const modelsGrid = document.getElementById('models-grid');
const modelsSearchInput = document.getElementById('models-search-input');
const modelFilterBtns = document.querySelectorAll('.filter-btn');
const providerPills = document.querySelectorAll('.provider-pill');

// Settings Elements (4 Free Providers)
const keyGemini = document.getElementById('key-gemini');
const keyGroq = document.getElementById('key-groq');
const keyOpenrouter = document.getElementById('key-openrouter');
const keyHuggingface = document.getElementById('key-huggingface');

const toggleGeminiVis = document.getElementById('toggle-gemini-vis');
const toggleGroqVis = document.getElementById('toggle-groq-vis');
const toggleOrVis = document.getElementById('toggle-or-vis');
const toggleHfVis = document.getElementById('toggle-hf-vis');

const testGeminiBtn = document.getElementById('test-gemini-btn');
const testGroqBtn = document.getElementById('test-groq-btn');
const testOpenrouterBtn = document.getElementById('test-openrouter-btn');
const testHuggingfaceBtn = document.getElementById('test-huggingface-btn');

const testResultGemini = document.getElementById('test-result-gemini');
const testResultGroq = document.getElementById('test-result-groq');
const testResultOpenrouter = document.getElementById('test-result-openrouter');
const testResultHuggingface = document.getElementById('test-result-huggingface');

const saveKeysBtn = document.getElementById('save-keys-btn');
const saveFeedback = document.getElementById('save-feedback');

// Lightbox Modal
const imageModal = document.getElementById('image-modal');
const modalBackdrop = document.getElementById('modal-backdrop');
const modalCloseBtn = document.getElementById('modal-close-btn');
const modalImage = document.getElementById('modal-image');
const modalDownloadBtn = document.getElementById('modal-download-btn');

let allRegisteredModels = [];
let allNodesList = [];
let activeConnections = [];
let isExecuting = false;
let activeCategoryFilter = 'all';
let activeProviderFilter = 'all';

// ==============================================================================
// 1. INITIALIZATION & WINDOW CONTROLS
// ==============================================================================
function initApp() {
  if (ipcRenderer) {
    minBtn.addEventListener('click', () => ipcRenderer.send('min-window'));
    maxBtn.addEventListener('click', () => ipcRenderer.send('max-window'));
    closeBtn.addEventListener('click', () => ipcRenderer.send('close-window'));
  } else {
    if (windowControls) windowControls.style.display = 'none';
  }

  // Init Network Nodes
  buildNetworkNodes();

  // Load Models Registry
  loadModelRegistry();

  // Load API Keys & Status
  checkSystemStatus();
  loadSavedKeys();

  // Wire Tab Buttons
  navTabs.forEach(btn => {
    btn.addEventListener('click', () => {
      const tabName = btn.getAttribute('data-tab');
      switchTab(tabName);
    });
  });

  // Wire Starter Chips
  document.querySelectorAll('.starter-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      const promptText = chip.getAttribute('data-prompt');
      if (promptText) {
        promptInput.value = promptText;
        adjustTextareaHeight();
        promptInput.focus();
      }
    });
  });

  // Inspector Close
  if (inspClose) {
    inspClose.addEventListener('click', () => nodeInspector.classList.add('hidden'));
  }
}

// Tab Switching
function switchTab(tabId) {
  navTabs.forEach(btn => {
    btn.classList.toggle('active', btn.getAttribute('data-tab') === tabId);
  });
  viewSections.forEach(sec => {
    sec.classList.toggle('active', sec.id === `view-${tabId}`);
  });

  if (tabId === 'network') {
    requestAnimationFrame(() => updateSvgLines());
  }
}

// Theme Toggle
themeToggleBtn.addEventListener('click', () => {
  const isLight = document.body.classList.toggle('theme-light');
  themeToggleBtn.querySelector('.theme-icon').textContent = isLight ? '🌙' : '🎨';
  localStorage.setItem('godmode_theme', isLight ? 'light' : 'cyberpunk');
  if (document.getElementById('view-network').classList.contains('active')) {
    updateSvgLines();
  }
});

if (localStorage.getItem('godmode_theme') === 'light') {
  document.body.classList.add('theme-light');
  themeToggleBtn.querySelector('.theme-icon').textContent = '🌙';
}

// ==============================================================================
// 2. CHAT & MULTI-AGENT SWARM EXECUTION
// ==============================================================================
function adjustTextareaHeight() {
  promptInput.style.height = 'auto';
  promptInput.style.height = Math.min(promptInput.scrollHeight, 180) + 'px';
}

promptInput.addEventListener('input', adjustTextareaHeight);
promptInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    submitPrompt();
  }
});

sendBtn.addEventListener('click', submitPrompt);

async function submitPrompt() {
  const prompt = promptInput.value.trim();
  if (!prompt || isExecuting) return;

  isExecuting = true;
  promptInput.value = '';
  adjustTextareaHeight();

  if (welcomeCard) welcomeCard.style.display = 'none';

  appendUserMessage(prompt);
  const loadingId = appendLoadingMessage();
  simulateSwarmActivation();

  try {
    const response = await fetch(`${API_BASE}/godmode`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt: prompt })
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    removeMessage(loadingId);
    appendSwarmResponse(data);

  } catch (err) {
    removeMessage(loadingId);
    appendErrorMessage(`Swarm Execution Notice: ${err.message}. Ensure the FastAPI server is running on http://localhost:8000.`);
  } finally {
    isExecuting = false;
    promptInput.focus();
  }
}

function appendUserMessage(text) {
  const msg = document.createElement('div');
  msg.className = 'message user';
  msg.innerHTML = `
    <div class="avatar-wrapper">👤</div>
    <div class="msg-bubble">${escapeHtml(text)}</div>
  `;
  chatHistory.appendChild(msg);
  scrollToBottom();
}

function appendLoadingMessage() {
  const id = 'loading-' + Date.now();
  const msg = document.createElement('div');
  msg.className = 'message swarm';
  msg.id = id;
  msg.innerHTML = `
    <div class="avatar-wrapper">⚡</div>
    <div class="swarm-bubble loading-bubble">
      <div class="pipeline-loader">
        <div class="pipeline-step active">
          <span class="step-dot"></span>
          <span>🧠 1. Brain Orchestrator Decomposing Task</span>
        </div>
        <div class="pipeline-step active">
          <span class="step-dot pulse"></span>
          <span>⚡ 2. Concurrent Swarm Agents (Coder, NLP, Vision, Writer)</span>
        </div>
        <div class="pipeline-step">
          <span class="step-dot"></span>
          <span>📝 3. Multimodal Presentation Synthesis</span>
        </div>
        <div class="pipeline-step">
          <span class="step-dot"></span>
          <span>🛡️ 4. QA Verifier Quality Audit</span>
        </div>
      </div>
    </div>
  `;
  chatHistory.appendChild(msg);
  scrollToBottom();
  return id;
}

function removeMessage(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

function appendSwarmResponse(data) {
  const msg = document.createElement('div');
  msg.className = 'message swarm';

  const totalMs = data.total_latency_ms || 850;
  const tasks = data.tasks || [];
  const brainModel = data.orchestrator?.model_name || data.orchestrator?.model || 'Brain Orchestrator';
  const brainProv = data.orchestrator?.provider || 'AI Core';
  const verifierModel = data.verifier?.model_name || data.verifier?.model || 'QA Verifier';
  const verifierProv = data.verifier?.provider || 'QA Core';

  // Build Rich Telemetry Accordion
  let telemetryHtml = `
    <div class="swarm-telemetry-box">
      <div class="telemetry-header" onclick="this.parentElement.querySelector('.telemetry-agents-list').classList.toggle('hidden')">
        <span>⚡ Swarm Pipeline: ${tasks.length} Specialist Agents (${(totalMs/1000).toFixed(2)}s)</span>
        <span class="telemetry-toggle-btn">▼ Agent Specs</span>
      </div>
      <div class="telemetry-agents-list hidden">
        <div class="agent-badge-row">
          <div class="agent-badge-info">
            <span class="agent-cat-tag cat-orchestrator">Brain</span>
            <span class="provider-tag">${escapeHtml(brainProv)}</span>
            <span>${escapeHtml(brainModel)}</span>
          </div>
          <span class="agent-latency">Planning</span>
        </div>
  `;

  tasks.forEach(t => {
    const catClass = `cat-${t.category || 'general'}`;
    const provName = t.provider || 'AI Specialist';
    telemetryHtml += `
      <div class="agent-badge-row">
        <div class="agent-badge-info">
          <span class="agent-cat-tag ${catClass}">${escapeHtml(t.category || 'agent')}</span>
          <span class="provider-tag">${escapeHtml(provName)}</span>
          <span>${escapeHtml(t.model_name || t.model || 'Specialist')}</span>
        </div>
        <span class="agent-latency">${t.latency_ms || 0}ms</span>
      </div>
    `;
  });

  telemetryHtml += `
        <div class="agent-badge-row">
          <div class="agent-badge-info">
            <span class="agent-cat-tag cat-orchestrator">Verifier</span>
            <span class="provider-tag">${escapeHtml(verifierProv)}</span>
            <span>${escapeHtml(verifierModel)}</span>
          </div>
          <span class="agent-latency">Verified</span>
        </div>
      </div>
    </div>
  `;

  const renderedContent = parseMarkdown(data.output || '');

  msg.innerHTML = `
    <div class="avatar-wrapper">⚡</div>
    <div class="swarm-bubble">
      ${telemetryHtml}
      <div class="msg-content">${renderedContent}</div>
      <div class="msg-footer-actions">
        <button class="quick-copy-btn" title="Copy Full Response">📋 Copy Response</button>
      </div>
    </div>
  `;

  chatHistory.appendChild(msg);
  attachCodeCopyHandlers(msg);
  attachImageZoomHandlers(msg);
  attachQuickCopyHandler(msg, data.output || '');
  scrollToBottom();
}

function attachQuickCopyHandler(container, text) {
  const btn = container.querySelector('.quick-copy-btn');
  if (btn) {
    btn.addEventListener('click', async () => {
      await navigator.clipboard.writeText(text);
      btn.textContent = '✅ Copied!';
      setTimeout(() => { btn.textContent = '📋 Copy Response'; }, 2000);
    });
  }
}

function appendErrorMessage(errorText) {
  const msg = document.createElement('div');
  msg.className = 'message swarm';
  msg.innerHTML = `
    <div class="avatar-wrapper">⚠️</div>
    <div class="swarm-bubble" style="border-color:var(--neon-red); background:rgba(239, 68, 68, 0.08);">
      <div style="color:var(--neon-red); font-weight:700; margin-bottom:4px;">Swarm Execution Notice</div>
      <div class="msg-content" style="color:#fca5a5;">${escapeHtml(errorText)}</div>
    </div>
  `;
  chatHistory.appendChild(msg);
  scrollToBottom();
}

function scrollToBottom() {
  chatHistory.scrollTop = chatHistory.scrollHeight;
}

// Clear & Export Chat
clearChatBtn.addEventListener('click', () => {
  chatHistory.innerHTML = '';
  if (welcomeCard) {
    chatHistory.appendChild(welcomeCard);
    welcomeCard.style.display = 'block';
  }
});

exportChatBtn.addEventListener('click', () => {
  const messages = chatHistory.querySelectorAll('.message');
  let exportText = `# GOD MODE AI Swarm Conversation\nExported: ${new Date().toLocaleString()}\n\n`;
  messages.forEach(m => {
    const isUser = m.classList.contains('user');
    const content = isUser ? m.querySelector('.msg-bubble').textContent : m.querySelector('.msg-content').textContent;
    exportText += `### ${isUser ? 'User' : 'GOD MODE Swarm'}\n${content}\n\n`;
  });

  const blob = new Blob([exportText], { type: 'text/markdown' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `godmode-swarm-chat-${Date.now()}.md`;
  a.click();
  URL.revokeObjectURL(url);
});

// ==============================================================================
// 3. RICH MARKDOWN & CODE PARSER
// ==============================================================================
function parseMarkdown(text) {
  if (!text) return '';

  let html = text;

  // 1. Extract Images (data:image or <img src="...">)
  html = html.replace(/<img\s+src=["'](data:image\/[^"']+)["'][^>]*>/gi, (match, src) => {
    return `<div class="image-preview-card"><img src="${src}" alt="AI Generated Artwork" class="zoomable-img" /></div>`;
  });

  html = html.replace(/(data:image\/(?:png|jpeg|webp|svg\+xml);base64,[A-Za-z0-9+/=]+)/g, (src) => {
    return `<div class="image-preview-card"><img src="${src}" alt="AI Generated Artwork" class="zoomable-img" /></div>`;
  });

  // 2. Fenced Code Blocks (```lang ... ```)
  html = html.replace(/```([a-zA-Z0-9_\-+]*)\n([\s\S]*?)```/g, (match, lang, code) => {
    const language = lang.trim() || 'code';
    const escapedCode = escapeHtml(code.trim());
    return `
      <div class="code-block-wrapper">
        <div class="code-header">
          <span>${language.toUpperCase()}</span>
          <button class="copy-code-btn" data-code="${encodeURIComponent(code.trim())}">
            <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
            <span>Copy</span>
          </button>
        </div>
        <pre><code>${escapedCode}</code></pre>
      </div>
    `;
  });

  // 3. Headings
  html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
  html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
  html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');

  // 4. Bold & Italic
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');

  // 5. Blockquotes
  html = html.replace(/^\> (.*$)/gim, '<blockquote>$1</blockquote>');

  // 6. Unordered Lists
  html = html.replace(/^\s*[-*]\s+(.*$)/gim, '<li>$1</li>');

  // 7. Inline Code
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

  // 8. Line breaks
  html = html.replace(/\n\n/g, '<p></p>');
  html = html.replace(/\n/g, '<br>');

  return html;
}

function escapeHtml(text) {
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  };
  return text.replace(/[&<>"']/g, m => map[m]);
}

function attachCodeCopyHandlers(container) {
  container.querySelectorAll('.copy-code-btn').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      e.stopPropagation();
      const code = decodeURIComponent(btn.getAttribute('data-code'));
      try {
        await navigator.clipboard.writeText(code);
        const span = btn.querySelector('span');
        const orig = span.textContent;
        span.textContent = 'Copied!';
        btn.style.borderColor = 'var(--neon-emerald)';
        btn.style.color = 'var(--neon-emerald)';
        setTimeout(() => {
          span.textContent = orig;
          btn.style.borderColor = '';
          btn.style.color = '';
        }, 2000);
      } catch (err) {
        console.error('Clipboard copy failed:', err);
      }
    });
  });
}

function attachImageZoomHandlers(container) {
  container.querySelectorAll('.zoomable-img').forEach(img => {
    img.addEventListener('click', () => {
      modalImage.src = img.src;
      modalDownloadBtn.href = img.src;
      imageModal.classList.remove('hidden');
    });
  });
}

// Lightbox Close
modalBackdrop.addEventListener('click', () => imageModal.classList.add('hidden'));
modalCloseBtn.addEventListener('click', () => imageModal.classList.add('hidden'));

// ==============================================================================
// 4. SWARM NETWORK GRAPH (75 NODES & SYNAPSE LINES)
// ==============================================================================
function buildNetworkNodes() {
  nodesOrchestrator.innerHTML = '';
  nodesCoder.innerHTML = '';
  nodesGeneral.innerHTML = '';
  nodesVision.innerHTML = '';
  allNodesList = [];

  // Column 1: Orchestrators (15)
  for (let i = 1; i <= 15; i++) {
    createNeuralNode(nodesOrchestrator, `orchestrator_${i}`, `Brain ${i}`, 'orchestrator');
  }
  // Column 2: Coder (20)
  for (let i = 1; i <= 20; i++) {
    createNeuralNode(nodesCoder, `coder_${i}`, `Coder ${i}`, 'coder');
  }
  // Column 3: General & NLP (25)
  for (let i = 1; i <= 15; i++) {
    createNeuralNode(nodesGeneral, `general_${i}`, `Gen ${i}`, 'general');
  }
  for (let i = 1; i <= 10; i++) {
    createNeuralNode(nodesGeneral, `nlp_${i}`, `NLP ${i}`, 'nlp');
  }
  // Column 4: Vision & Video (15)
  for (let i = 1; i <= 10; i++) {
    createNeuralNode(nodesVision, `vision_${i}`, `Vision ${i}`, 'vision');
  }
  for (let i = 1; i <= 5; i++) {
    createNeuralNode(nodesVision, `video_${i}`, `Video ${i}`, 'video');
  }

  setTimeout(updateSvgLines, 200);
  window.addEventListener('resize', updateSvgLines);
}

function createNeuralNode(container, agentKey, label, category) {
  const node = document.createElement('div');
  node.className = 'neural-node';
  node.setAttribute('data-key', agentKey);
  node.setAttribute('data-cat', category);
  node.textContent = agentKey.replace('_', ' ');

  node.addEventListener('mouseenter', () => highlightNodeConnections(node));
  node.addEventListener('mouseleave', () => resetNodeConnections());
  node.addEventListener('click', (e) => {
    e.stopPropagation();
    openNodeInspector(agentKey, category);
  });

  container.appendChild(node);
  allNodesList.push(node);
  return node;
}

function updateSvgLines() {
  if (!svgLines) return;
  svgLines.innerHTML = '';
  activeConnections = [];

  const col1Nodes = nodesOrchestrator.querySelectorAll('.neural-node');
  const col2Nodes = nodesCoder.querySelectorAll('.neural-node');
  const col3Nodes = nodesGeneral.querySelectorAll('.neural-node');
  const col4Nodes = nodesVision.querySelectorAll('.neural-node');

  if (!col1Nodes.length || !col2Nodes.length) return;

  const containerRect = svgLines.getBoundingClientRect();
  connectColumns(col1Nodes, col2Nodes, containerRect, 2);
  connectColumns(col2Nodes, col3Nodes, containerRect, 2);
  connectColumns(col3Nodes, col4Nodes, containerRect, 2);
}

function connectColumns(fromList, toList, containerRect, connectionsPerNode = 2) {
  fromList.forEach(fromEl => {
    for (let k = 0; k < connectionsPerNode; k++) {
      const targetEl = toList[Math.floor(Math.random() * toList.length)];
      drawSynapseLine(fromEl, targetEl, containerRect);
    }
  });
}

function drawSynapseLine(el1, el2, containerRect) {
  const r1 = el1.getBoundingClientRect();
  const r2 = el2.getBoundingClientRect();

  const x1 = r1.right - containerRect.left;
  const y1 = r1.top + r1.height / 2 - containerRect.top;
  const x2 = r2.left - containerRect.left;
  const y2 = r2.top + r2.height / 2 - containerRect.top;

  const line = document.createElementNS('http://www.w3.org/2000/svg', 'path');
  const dx = (x2 - x1) / 2;
  const d = `M ${x1} ${y1} C ${x1 + dx} ${y1}, ${x2 - dx} ${y2}, ${x2} ${y2}`;
  line.setAttribute('d', d);
  line.setAttribute('fill', 'none');
  line.classList.add('synapse-line');

  svgLines.appendChild(line);
  activeConnections.push({ line, el1, el2 });
}

function highlightNodeConnections(node) {
  node.classList.add('active');
  activeConnections.forEach(conn => {
    if (conn.el1 === node || conn.el2 === node) {
      conn.line.classList.add('active');
      conn.el1.classList.add('active');
      conn.el2.classList.add('active');
    }
  });
}

function resetNodeConnections() {
  allNodesList.forEach(n => n.classList.remove('active'));
  activeConnections.forEach(conn => conn.line.classList.remove('active'));
}

function simulateSwarmActivation() {
  resetNodeConnections();
  const activeSubset = [];
  for (let i = 0; i < 25; i++) {
    const n = allNodesList[Math.floor(Math.random() * allNodesList.length)];
    if (n && !activeSubset.includes(n)) activeSubset.push(n);
  }

  activeSubset.forEach(n => n.classList.add('active'));
  activeConnections.forEach(conn => {
    if (activeSubset.includes(conn.el1) && activeSubset.includes(conn.el2)) {
      conn.line.classList.add('active');
    }
  });

  setTimeout(() => {
    resetNodeConnections();
  }, 3500);
}

if (simulatePulseBtn) {
  simulatePulseBtn.addEventListener('click', simulateSwarmActivation);
}

function openNodeInspector(agentKey, category) {
  inspBadge.textContent = `${category.toUpperCase()} AGENT`;
  inspTitle.textContent = `Agent ${agentKey}`;
  
  const found = allRegisteredModels.find(m => m.agent_key === agentKey);
  if (found) {
    inspModel.textContent = found.model_id;
    inspProvider.textContent = `${found.provider} • Free Tier`;
    inspTier.textContent = '100% Free';
  } else {
    inspModel.textContent = 'qwen/qwen3.8-27b';
    inspProvider.textContent = 'Groq / Free Tier';
    inspTier.textContent = '100% Free';
  }

  nodeInspector.classList.remove('hidden');
}

// ==============================================================================
// 5. MODEL REGISTRY EXPLORER
// ==============================================================================
async function loadModelRegistry() {
  try {
    const res = await fetch(`${API_BASE}/api/models`);
    if (res.ok) {
      const data = await res.json();
      allRegisteredModels = data.models || [];
      renderFilteredModels();
    }
  } catch (e) {
    console.log('Using local fallback for models registry');
  }
}

function renderFilteredModels() {
  if (!modelsGrid) return;
  const q = modelsSearchInput ? modelsSearchInput.value.toLowerCase().trim() : '';

  const filtered = allRegisteredModels.filter(m => {
    const matchesCat = (activeCategoryFilter === 'all' || m.category === activeCategoryFilter);
    const matchesProv = (activeProviderFilter === 'all' || m.provider === activeProviderFilter);
    const matchesSearch = !q || (
      (m.name && m.name.toLowerCase().includes(q)) || 
      (m.model_id && m.model_id.toLowerCase().includes(q)) || 
      (m.category && m.category.toLowerCase().includes(q)) ||
      (m.provider && m.provider.toLowerCase().includes(q))
    );
    return matchesCat && matchesProv && matchesSearch;
  });

  renderModelsGrid(filtered);
}

function renderModelsGrid(models) {
  if (!modelsGrid) return;
  modelsGrid.innerHTML = '';

  if (models.length === 0) {
    modelsGrid.innerHTML = `
      <div style="grid-column: 1/-1; text-align:center; padding: 40px; color: var(--text-muted);">
        No models match your current filters.
      </div>
    `;
    return;
  }

  models.forEach(m => {
    const card = document.createElement('div');
    card.className = 'model-card';
    card.setAttribute('data-category', m.category);

    let providerClass = 'badge-or';
    if (m.provider === 'Google Gemini') providerClass = 'badge-gemini';
    else if (m.provider === 'Groq') providerClass = 'badge-groq';
    else if (m.provider === 'HuggingFace') providerClass = 'badge-hf';

    card.innerHTML = `
      <div class="model-card-top">
        <span class="model-card-name">${escapeHtml(m.name || m.agent_key)}</span>
        <span class="badge ${providerClass}">${escapeHtml(m.provider || 'AI Core')}</span>
      </div>
      <div class="model-card-id">${escapeHtml(m.model_id)}</div>
      <div class="model-card-badges">
        <span class="badge badge-free">Free Tier</span>
        <span class="badge" style="background:rgba(255,255,255,0.05); color:var(--text-muted);">${m.category}</span>
      </div>
    `;

    modelsGrid.appendChild(card);
  });
}

// Search & Filter Listeners
if (modelsSearchInput) {
  modelsSearchInput.addEventListener('input', renderFilteredModels);
}

modelFilterBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    modelFilterBtns.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    activeCategoryFilter = btn.getAttribute('data-filter') || 'all';
    renderFilteredModels();
  });
});

providerPills.forEach(pill => {
  pill.addEventListener('click', () => {
    providerPills.forEach(p => p.classList.remove('active'));
    pill.classList.add('active');
    activeProviderFilter = pill.getAttribute('data-provider') || 'all';
    renderFilteredModels();
  });
});

// ==============================================================================
// 6. SETTINGS & 4-PROVIDER KEYS MANAGEMENT
// ==============================================================================
async function checkSystemStatus() {
  try {
    const res = await fetch(`${API_BASE}/api/status`);
    if (res.ok) {
      const data = await res.json();
      const count = data.active_providers_count || 0;

      if (count > 0) {
        statusPillText.textContent = `SWARM ONLINE (${count} PROVIDERS)`;
        swarmStatusPill.style.color = 'var(--neon-emerald)';
        swarmStatusPill.style.borderColor = 'rgba(16, 185, 129, 0.4)';
        if (clusterIndicator) clusterIndicator.innerHTML = `Cluster: <strong>${count} Cloud Providers Active</strong>`;
      } else {
        statusPillText.textContent = 'SWARM READY (DEMO)';
        swarmStatusPill.style.color = 'var(--neon-cyan)';
        swarmStatusPill.style.borderColor = 'rgba(0, 240, 255, 0.4)';
        if (clusterIndicator) clusterIndicator.innerHTML = `Cluster: <strong>75 Models Ready</strong>`;
      }
    }
  } catch (e) {
    statusPillText.textContent = 'BACKEND OFFLINE';
    swarmStatusPill.style.color = 'var(--neon-red)';
  }
}

async function loadSavedKeys() {
  try {
    const res = await fetch(`${API_BASE}/api/keys`);
    if (res.ok) {
      const data = await res.json();
      if (data.gemini_preview && keyGemini) keyGemini.placeholder = `Configured (${data.gemini_preview})`;
      if (data.groq_preview && keyGroq) keyGroq.placeholder = `Configured (${data.groq_preview})`;
      if (data.openrouter_preview && keyOpenrouter) keyOpenrouter.placeholder = `Configured (${data.openrouter_preview})`;
      if (data.huggingface_preview && keyHuggingface) keyHuggingface.placeholder = `Configured (${data.huggingface_preview})`;
    }
  } catch (e) {
    console.log('Unable to load key previews');
  }
}

// Password Vis toggles
if (toggleGeminiVis && keyGemini) {
  toggleGeminiVis.addEventListener('click', () => {
    keyGemini.type = keyGemini.type === 'password' ? 'text' : 'password';
  });
}
if (toggleGroqVis && keyGroq) {
  toggleGroqVis.addEventListener('click', () => {
    keyGroq.type = keyGroq.type === 'password' ? 'text' : 'password';
  });
}
if (toggleOrVis && keyOpenrouter) {
  toggleOrVis.addEventListener('click', () => {
    keyOpenrouter.type = keyOpenrouter.type === 'password' ? 'text' : 'password';
  });
}
if (toggleHfVis && keyHuggingface) {
  toggleHfVis.addEventListener('click', () => {
    keyHuggingface.type = keyHuggingface.type === 'password' ? 'text' : 'password';
  });
}

// 1. Test Gemini Connection
if (testGeminiBtn) {
  testGeminiBtn.addEventListener('click', async () => {
    testResultGemini.className = 'test-result-box';
    testResultGemini.style.display = 'block';
    testResultGemini.textContent = 'Testing Google Gemini key...';
    try {
      const res = await fetch(`${API_BASE}/api/keys/test`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider: 'gemini', key: keyGemini.value.trim() || undefined })
      });
      const data = await res.json();
      testResultGemini.className = `test-result-box ${data.success ? 'success' : 'error'}`;
      testResultGemini.textContent = data.message;
      checkSystemStatus();
    } catch (err) {
      testResultGemini.className = 'test-result-box error';
      testResultGemini.textContent = `Test request failed: ${err.message}`;
    }
  });
}

// 2. Test Groq Connection
if (testGroqBtn) {
  testGroqBtn.addEventListener('click', async () => {
    testResultGroq.className = 'test-result-box';
    testResultGroq.style.display = 'block';
    testResultGroq.textContent = 'Testing Groq Cloud key...';
    try {
      const res = await fetch(`${API_BASE}/api/keys/test`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider: 'groq', key: keyGroq.value.trim() || undefined })
      });
      const data = await res.json();
      testResultGroq.className = `test-result-box ${data.success ? 'success' : 'error'}`;
      testResultGroq.textContent = data.message;
      checkSystemStatus();
    } catch (err) {
      testResultGroq.className = 'test-result-box error';
      testResultGroq.textContent = `Test request failed: ${err.message}`;
    }
  });
}

// 3. Test OpenRouter Connection
if (testOpenrouterBtn) {
  testOpenrouterBtn.addEventListener('click', async () => {
    testResultOpenrouter.className = 'test-result-box';
    testResultOpenrouter.style.display = 'block';
    testResultOpenrouter.textContent = 'Testing OpenRouter key...';
    try {
      const res = await fetch(`${API_BASE}/api/keys/test`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider: 'openrouter', key: keyOpenrouter.value.trim() || undefined })
      });
      const data = await res.json();
      testResultOpenrouter.className = `test-result-box ${data.success ? 'success' : 'error'}`;
      testResultOpenrouter.textContent = data.message;
      checkSystemStatus();
    } catch (err) {
      testResultOpenrouter.className = 'test-result-box error';
      testResultOpenrouter.textContent = `Test request failed: ${err.message}`;
    }
  });
}

// 4. Test Hugging Face Connection
if (testHuggingfaceBtn) {
  testHuggingfaceBtn.addEventListener('click', async () => {
    testResultHuggingface.className = 'test-result-box';
    testResultHuggingface.style.display = 'block';
    testResultHuggingface.textContent = 'Testing Hugging Face token...';
    try {
      const res = await fetch(`${API_BASE}/api/keys/test`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider: 'huggingface', key: keyHuggingface.value.trim() || undefined })
      });
      const data = await res.json();
      testResultHuggingface.className = `test-result-box ${data.success ? 'success' : 'error'}`;
      testResultHuggingface.textContent = data.message;
      checkSystemStatus();
    } catch (err) {
      testResultHuggingface.className = 'test-result-box error';
      testResultHuggingface.textContent = `Test request failed: ${err.message}`;
    }
  });
}

// Save All Keys
if (saveKeysBtn) {
  saveKeysBtn.addEventListener('click', async () => {
    const gemVal = keyGemini ? keyGemini.value.trim() : '';
    const grqVal = keyGroq ? keyGroq.value.trim() : '';
    const orVal = keyOpenrouter ? keyOpenrouter.value.trim() : '';
    const hfVal = keyHuggingface ? keyHuggingface.value.trim() : '';

    saveFeedback.textContent = 'Saving keys to .env...';
    saveFeedback.style.color = 'var(--text-muted)';

    try {
      const res = await fetch(`${API_BASE}/api/keys`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          gemini_key: gemVal || undefined,
          groq_key: grqVal || undefined,
          openrouter_key: orVal || undefined,
          huggingface_token: hfVal || undefined,
          save_to_env: true
        })
      });

      if (res.ok) {
        saveFeedback.textContent = '✅ Saved & applied successfully!';
        saveFeedback.style.color = 'var(--neon-emerald)';
        checkSystemStatus();
        loadSavedKeys();
        setTimeout(() => { saveFeedback.textContent = ''; }, 3000);
      } else {
        throw new Error('Save failed');
      }
    } catch (e) {
      saveFeedback.textContent = `❌ Error: ${e.message}`;
      saveFeedback.style.color = 'var(--neon-red)';
    }
  });
}

// Start App
document.addEventListener('DOMContentLoaded', initApp);

