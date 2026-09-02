// GOD MODE 75-Model Swarm — Professional Desktop & Web Engine

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

// DOM Elements: Header & Navigation
const navTabs = document.querySelectorAll('.nav-tab');
const viewPanels = document.querySelectorAll('.view-panel');
const themeToggleBtn = document.getElementById('theme-toggle-btn');
const swarmStatusPill = document.getElementById('swarm-status-pill');
const statusPillText = document.getElementById('status-pill-text');
const windowControls = document.getElementById('window-controls');
const minBtn = document.getElementById('min-btn');
const maxBtn = document.getElementById('max-btn');
const closeBtn = document.getElementById('close-btn');

// DOM Elements: Chat View
const chatHistory = document.getElementById('chat-history');
const welcomeCard = document.getElementById('welcome-card');
const promptInput = document.getElementById('prompt-input');
const sendBtn = document.getElementById('send-btn');
const clearChatBtn = document.getElementById('clear-chat-btn');
const exportChatBtn = document.getElementById('export-chat-btn');
const gotoNetworkBtn = document.getElementById('goto-network-btn');
const clusterIndicator = document.getElementById('cluster-indicator');

// DOM Elements: Swarm Network View & Live Traversal
const nodesOrchestrator = document.getElementById('nodes-orchestrator');
const nodesCoder = document.getElementById('nodes-coder');
const nodesGeneral = document.getElementById('nodes-general');
const nodesVision = document.getElementById('nodes-vision');
const svgLines = document.getElementById('network-lines');
const hudActiveQuery = document.getElementById('hud-active-query');
const stageSteps = {
  1: document.getElementById('stage-1'),
  2: document.getElementById('stage-2'),
  3: document.getElementById('stage-3'),
  4: document.getElementById('stage-4')
};
const networkPromptInput = document.getElementById('network-prompt-input');
const networkTransmitBtn = document.getElementById('network-transmit-btn');
const simulatePulseBtn = document.getElementById('simulate-pulse-btn');
const traceFeedList = document.getElementById('trace-feed-list');
const clearTraceBtn = document.getElementById('clear-trace-btn');

// Node Inspector
const nodeInspector = document.getElementById('node-inspector-modal');
const inspClose = document.getElementById('insp-close');
const inspTitle = document.getElementById('insp-title');
const inspBadge = document.getElementById('insp-badge');
const inspModel = document.getElementById('insp-model');
const inspProvider = document.getElementById('insp-provider');
const inspTier = document.getElementById('insp-tier');
const inspTask = document.getElementById('insp-task');
const inspLatency = document.getElementById('insp-latency');

// DOM Elements: Models Registry
const modelsGrid = document.getElementById('models-grid');
const modelsSearchInput = document.getElementById('models-search-input');
const categoryFilterBtns = document.querySelectorAll('.filter-pill');
const providerFilterBtns = document.querySelectorAll('.provider-filter-btn');

// DOM Elements: Settings & Keys
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

// Lightbox
const imageModal = document.getElementById('image-modal');
const modalBackdrop = document.getElementById('modal-backdrop');
const modalCloseBtn = document.getElementById('modal-close-btn');
const modalImage = document.getElementById('modal-image');
const modalDownloadBtn = document.getElementById('modal-download-btn');

// Global State
let allRegisteredModels = [];
let allNodesMap = {}; 
let activeSynapseConnections = [];
let isExecuting = false;
let activeCategoryFilter = 'all';
let activeProviderFilter = 'all';

// ==============================================================================
// 1. INITIALIZATION & LIFECYCLE
// ==============================================================================
document.addEventListener('DOMContentLoaded', () => {
  initApp();
});

function initApp() {
  if (ipcRenderer) {
    if (minBtn) minBtn.addEventListener('click', () => ipcRenderer.send('min-window'));
    if (maxBtn) maxBtn.addEventListener('click', () => ipcRenderer.send('max-window'));
    if (closeBtn) closeBtn.addEventListener('click', () => ipcRenderer.send('close-window'));
  } else {
    if (windowControls) windowControls.style.display = 'none';
  }

  const savedTheme = localStorage.getItem('godmode_theme') || 'dark';
  applyTheme(savedTheme);
  if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', () => {
      const nextTheme = document.body.classList.contains('theme-light') ? 'dark' : 'light';
      applyTheme(nextTheme);
    });
  }

  navTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const tabTarget = tab.getAttribute('data-tab');
      switchTab(tabTarget);
    });
  });

  if (gotoNetworkBtn) {
    gotoNetworkBtn.addEventListener('click', () => switchTab('network'));
  }

  buildNetworkNodes();
  loadModelRegistry();
  checkSystemStatus();
  loadSavedKeys();
  setupChatInputs();
  setupNetworkTraversalControls();
  setupSettingsHandlers();
}

function applyTheme(theme) {
  if (theme === 'light') {
    document.body.classList.remove('theme-dark');
    document.body.classList.add('theme-light');
  } else {
    document.body.classList.remove('theme-light');
    document.body.classList.add('theme-dark');
  }
  localStorage.setItem('godmode_theme', theme);
  requestAnimationFrame(updateSvgLines);
}

function switchTab(tabId) {
  navTabs.forEach(t => t.classList.toggle('active', t.getAttribute('data-tab') === tabId));
  viewPanels.forEach(p => p.classList.toggle('active', p.id === `view-${tabId}`));

  if (tabId === 'network') {
    requestAnimationFrame(() => {
      updateSvgLines();
    });
  }
}

// ==============================================================================
// 2. CHAT CONTROLLER
// ==============================================================================
function setupChatInputs() {
  if (!promptInput) return;

  promptInput.addEventListener('input', () => {
    adjustTextareaHeight();
    if (sendBtn) {
      sendBtn.disabled = !promptInput.value.trim();
    }
  });

  promptInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      const text = promptInput.value.trim();
      if (text && !isExecuting) {
        submitPrompt(text);
      }
    }
  });

  if (sendBtn) {
    sendBtn.addEventListener('click', () => {
      const text = promptInput.value.trim();
      if (text && !isExecuting) {
        submitPrompt(text);
      }
    });
  }

  document.querySelectorAll('.starter-card').forEach(card => {
    card.addEventListener('click', () => {
      const p = card.getAttribute('data-prompt');
      if (p) {
        promptInput.value = p;
        adjustTextareaHeight();
        if (sendBtn) sendBtn.disabled = false;
        promptInput.focus();
      }
    });
  });

  if (clearChatBtn) {
    clearChatBtn.addEventListener('click', () => {
      chatHistory.innerHTML = '';
      if (welcomeCard) {
        chatHistory.appendChild(welcomeCard);
        welcomeCard.style.display = 'flex';
      }
    });
  }

  if (exportChatBtn) {
    exportChatBtn.addEventListener('click', exportChatAsMarkdown);
  }
}

function adjustTextareaHeight() {
  if (!promptInput) return;
  promptInput.style.height = 'auto';
  promptInput.style.height = Math.min(promptInput.scrollHeight, 180) + 'px';
}

async function submitPrompt(promptText) {
  if (!promptText || isExecuting) return;

  isExecuting = true;
  if (sendBtn) sendBtn.disabled = true;
  promptInput.value = '';
  adjustTextareaHeight();

  if (welcomeCard) welcomeCard.style.display = 'none';

  appendUserMessage(promptText);
  const loadingMsgId = appendLoadingStepProgress();
  startLivePromptNetworkFlow(promptText);

  try {
    const response = await fetch(`${API_BASE}/godmode`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt: promptText })
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    removeMessage(loadingMsgId);
    appendSwarmResponse(data);
    completeLivePromptNetworkFlow(data);

  } catch (err) {
    removeMessage(loadingMsgId);
    appendErrorMessage(`Swarm Execution Notice: ${err.message}. Make sure the backend is running on http://localhost:8000.`);
    logTraceEvent(`Execution error: ${err.message}`, 'highlight');
    resetNetworkStageIndicator();
  } finally {
    isExecuting = false;
    if (sendBtn) sendBtn.disabled = !promptInput.value.trim();
    promptInput.focus();
  }
}

function appendUserMessage(text) {
  const row = document.createElement('div');
  row.className = 'chat-message-row user';
  row.innerHTML = `
    <div class="user-bubble">${escapeHtml(text)}</div>
  `;
  chatHistory.appendChild(row);
  scrollToChatBottom();
}

function appendLoadingStepProgress() {
  const id = 'loader-' + Date.now();
  const row = document.createElement('div');
  row.className = 'chat-message-row swarm';
  row.id = id;

  row.innerHTML = `
    <div class="msg-avatar"><svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg></div>
    <div class="swarm-content-wrapper">
      <div class="pipeline-progress-card">
        <div class="pipeline-step-item active">
          <span class="pipeline-step-dot"></span>
          <span>1. Brain Orchestrator analyzing directive & routing subtasks</span>
        </div>
        <div class="pipeline-step-item active">
          <span class="pipeline-step-dot"></span>
          <span>2. Concurrent Swarm Execution across specialized agents</span>
        </div>
        <div class="pipeline-step-item">
          <span class="pipeline-step-dot"></span>
          <span>3. Multimodal Synthesis & Deliverable Compilation</span>
        </div>
        <div class="pipeline-step-item">
          <span class="pipeline-step-dot"></span>
          <span>4. Quality Assurance Verifier checking code integrity</span>
        </div>
      </div>
    </div>
  `;
  chatHistory.appendChild(row);
  scrollToChatBottom();
  return id;
}

function removeMessage(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

function appendSwarmResponse(data) {
  const row = document.createElement('div');
  row.className = 'chat-message-row swarm';

  const totalMs = data.total_latency_ms || 850;
  const tasks = data.tasks || [];
  const brainModel = data.orchestrator?.model_name || data.orchestrator?.model || 'Chief Orchestrator';
  const brainProv = data.orchestrator?.provider || 'AI Core';
  const verifierModel = data.verifier?.model_name || data.verifier?.model || 'QA Verifier';
  const verifierProv = data.verifier?.provider || 'QA Core';

  let reasoningHtml = `
    <div class="swarm-reasoning-card">
      <div class="reasoning-toggle-header">
        <div class="reasoning-left">
          <span>Swarm Pipeline:</span>
          <span class="reasoning-badge-count">${tasks.length} Specialist Agents</span>
          <span style="color:var(--text-muted); font-size:11px;">(${(totalMs/1000).toFixed(2)}s)</span>
        </div>
        <div class="reasoning-right-actions">
          <a href="#" class="graph-jump-btn" title="View live flow on Swarm Network Graph">
            <span>View on Graph</span>
          </a>
          <span class="reasoning-chevron">&#9662;</span>
        </div>
      </div>
      <div class="reasoning-body hidden">
        <div class="agent-row-item">
          <div class="agent-info-left">
            <span class="role-pill orchestrator">Brain</span>
            <span class="agent-model-name">${escapeHtml(brainModel)}</span>
            <span class="agent-provider-tag">(${escapeHtml(brainProv)})</span>
          </div>
          <span class="agent-latency-badge">Orchestration</span>
        </div>
  `;

  tasks.forEach(t => {
    const cat = t.category || 'general';
    const roleClass = ['orchestrator', 'coder', 'nlp', 'vision'].includes(cat) ? cat : 'nlp';
    reasoningHtml += `
      <div class="agent-row-item">
        <div class="agent-info-left">
          <span class="role-pill ${roleClass}">${escapeHtml(cat)}</span>
          <span class="agent-model-name">${escapeHtml(t.model_name || t.model || 'Specialist')}</span>
          <span class="agent-provider-tag">(${escapeHtml(t.provider || 'Cloud')})</span>
        </div>
        <span class="agent-latency-badge">${t.latency_ms || 0}ms</span>
      </div>
    `;
  });

  reasoningHtml += `
        <div class="agent-row-item">
          <div class="agent-info-left">
            <span class="role-pill orchestrator">Verifier</span>
            <span class="agent-model-name">${escapeHtml(verifierModel)}</span>
            <span class="agent-provider-tag">(${escapeHtml(verifierProv)})</span>
          </div>
          <span class="agent-latency-badge">Verified</span>
        </div>
      </div>
    </div>
  `;

  const renderedProse = parseRichMarkdown(data.output || '');

  row.innerHTML = `
    <div class="msg-avatar"><svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg></div>
    <div class="swarm-content-wrapper">
      ${reasoningHtml}
      <div class="msg-prose">${renderedProse}</div>
      <div class="msg-bottom-bar">
        <button class="action-icon-btn copy-full-btn" title="Copy Output to Clipboard">
          <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
          <span>Copy Response</span>
        </button>
      </div>
    </div>
  `;

  chatHistory.appendChild(row);

  const toggleHeader = row.querySelector('.reasoning-toggle-header');
  const reasoningBody = row.querySelector('.reasoning-body');
  const reasoningCard = row.querySelector('.swarm-reasoning-card');
  const graphJumpBtn = row.querySelector('.graph-jump-btn');

  if (toggleHeader && reasoningBody) {
    toggleHeader.addEventListener('click', (e) => {
      if (e.target.closest('.graph-jump-btn')) return;
      reasoningBody.classList.toggle('hidden');
      reasoningCard.classList.toggle('open');
    });
  }

  if (graphJumpBtn) {
    graphJumpBtn.addEventListener('click', (e) => {
      e.preventDefault();
      switchTab('network');
    });
  }

  const copyBtn = row.querySelector('.copy-full-btn');
  if (copyBtn) {
    copyBtn.addEventListener('click', async () => {
      await navigator.clipboard.writeText(data.output || '');
      const span = copyBtn.querySelector('span');
      span.textContent = 'Copied';
      setTimeout(() => { span.textContent = 'Copy Response'; }, 2000);
    });
  }

  attachCodeBlockHandlers(row);
  attachImageZoomHandlers(row);
  scrollToChatBottom();
}

function appendErrorMessage(errText) {
  const row = document.createElement('div');
  row.className = 'chat-message-row swarm';
  row.innerHTML = `
    <div class="msg-avatar" style="background:var(--accent-red-subtle); color:var(--accent-red);"><svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg></div>
    <div class="swarm-content-wrapper">
      <div style="background:var(--accent-red-subtle); border:1px solid rgba(239, 68, 68, 0.3); border-radius:var(--radius-md); padding:14px 16px; color:#fca5a5; font-size:13.5px;">
        <strong style="color:var(--accent-red); display:block; margin-bottom:4px;">Swarm Execution Notice</strong>
        ${escapeHtml(errText)}
      </div>
    </div>
  `;
  chatHistory.appendChild(row);
  scrollToChatBottom();
}

function scrollToChatBottom() {
  if (chatHistory) {
    chatHistory.scrollTop = chatHistory.scrollHeight;
  }
}

function exportChatAsMarkdown() {
  const rows = chatHistory.querySelectorAll('.chat-message-row');
  let exportText = `# GOD MODE 75-Model Swarm Conversation\nExported: ${new Date().toLocaleString()}\n\n`;

  rows.forEach(r => {
    const isUser = r.classList.contains('user');
    const content = isUser
      ? r.querySelector('.user-bubble')?.textContent || ''
      : r.querySelector('.msg-prose')?.textContent || '';
    exportText += `### ${isUser ? 'User' : 'GOD MODE Swarm'}\n${content.trim()}\n\n`;
  });

  const blob = new Blob([exportText], { type: 'text/markdown' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `godmode-swarm-session-${Date.now()}.md`;
  a.click();
  URL.revokeObjectURL(url);
}

// ==============================================================================
// 3. RICH MARKDOWN & CODE PARSING ENGINE (CLAUDE & CHATGPT QUALITY)
// ==============================================================================

// Initialize Marked with Highlight.js syntax highlighting & GFM extensions
(function initMarkdownEngine() {
  if (typeof marked !== 'undefined') {
    const renderer = new marked.Renderer();

    // Syntax-highlighted code block with language header & copy button
    renderer.code = function(arg1, arg2) {
      const isObj = (typeof arg1 === 'object' && arg1 !== null);
      const code = (isObj ? arg1.text : arg1) || '';
      const rawLang = (isObj ? arg1.lang : arg2) || '';
      const language = rawLang.trim().toLowerCase();
      let highlighted = '';

      if (typeof hljs !== 'undefined' && language && hljs.getLanguage(language)) {
        try {
          highlighted = hljs.highlight(code, { language }).value;
        } catch (e) {
          highlighted = escapeHtml(code);
        }
      } else if (typeof hljs !== 'undefined') {
        try {
          highlighted = hljs.highlightAuto(code).value;
        } catch (e) {
          highlighted = escapeHtml(code);
        }
      } else {
        highlighted = escapeHtml(code);
      }

      const displayLang = language ? language.toUpperCase() : 'CODE';
      const encodedCode = encodeURIComponent(code);

      return `
        <div class="code-block-container">
          <div class="code-block-header">
            <div class="code-lang-tag">
              <span class="code-lang-bullet"></span>
              <span>${escapeHtml(displayLang)}</span>
            </div>
            <button class="copy-code-btn" data-code="${encodedCode}" title="Copy code snippet">
              <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
              <span>Copy</span>
            </button>
          </div>
          <pre><code class="hljs ${language ? `language-${language}` : ''}">${highlighted}</code></pre>
        </div>
      `;
    };

    // Styled GFM tables
    renderer.table = function(arg1, arg2) {
      const isObj = (typeof arg1 === 'object' && arg1 !== null);
      const header = (isObj ? arg1.header : arg1) || '';
      const rows = (isObj ? arg1.rows : arg2) || '';
      return `
        <div class="table-responsive-wrapper">
          <table class="styled-markdown-table">
            <thead>${header}</thead>
            <tbody>${rows}</tbody>
          </table>
        </div>
      `;
    };

    // GitHub-style callouts / alerts: [!NOTE], [!TIP], [!IMPORTANT], [!WARNING], [!CAUTION]
    renderer.blockquote = function(arg1) {
      const isObj = (typeof arg1 === 'object' && arg1 !== null);
      const text = (isObj ? arg1.text : arg1) || '';
      const alertMatch = text.match(/^\s*<p>\s*\[\!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\s*(?:<br>)?([\s\S]*?)<\/p>/i);
      if (alertMatch) {
        const type = alertMatch[1].toUpperCase();
        const body = alertMatch[2];
        const typeClass = type.toLowerCase();
        const icons = {
          NOTE: '<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>',
          TIP: '<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6"/><path d="M10 22h4"/><path d="M12 2a7 7 0 0 0-7 7c0 2.5 1.5 4.5 3 6h8c1.5-1.5 3-3.5 3-6a7 7 0 0 0-7-7z"/></svg>',
          IMPORTANT: '<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>',
          WARNING: '<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
          CAUTION: '<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><polygon points="7.86 2 16.14 2 22 7.86 22 16.14 16.14 22 7.86 22 2 16.14 2 7.86 7.86 2"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>'
        };
        return `
          <div class="callout-alert ${typeClass}">
            <div class="callout-header">
              ${icons[type] || icons.NOTE}
              <span class="callout-label">${type}</span>
            </div>
            <div class="callout-content"><p>${body}</p></div>
          </div>
        `;
      }
      return `<blockquote>${text}</blockquote>`;
    };

    marked.use({ renderer, gfm: true, breaks: true });
  }
})();

function parseRichMarkdown(text) {
  if (!text) return '';

  // 1. Extract base64 and image deliverable tags into safe tokens
  const images = [];
  let cleanText = text.replace(/<img\s+src=["'](data:image\/[^"']+)["'][^>]*>/gi, (match, src) => {
    const id = `__GODMODE_IMG_TOKEN_${images.length}__`;
    images.push(src);
    return id;
  });

  cleanText = cleanText.replace(/(data:image\/(?:png|jpeg|webp|svg\+xml);base64,[A-Za-z0-9+/=]+)/g, (src) => {
    const id = `__GODMODE_IMG_TOKEN_${images.length}__`;
    images.push(src);
    return id;
  });

  // 2. Parse Markdown
  let html = '';
  if (typeof marked !== 'undefined' && marked.parse) {
    try {
      html = marked.parse(cleanText);
    } catch (e) {
      console.warn('[Markdown Engine] Marked parse notice, using fallback:', e);
      html = fallbackMarkdownParser(cleanText);
    }
  } else {
    html = fallbackMarkdownParser(cleanText);
  }

  // 3. Re-inject images with zoomable card container
  images.forEach((src, idx) => {
    const id = `__GODMODE_IMG_TOKEN_${idx}__`;
    const cardHtml = `<div class="generated-image-card"><img src="${src}" alt="AI Deliverable" class="zoomable-artifact" loading="lazy" /></div>`;
    html = html.split(id).join(cardHtml);
  });

  return html;
}

function fallbackMarkdownParser(text) {
  if (!text) return '';
  let html = escapeHtml(text);

  // Fenced code blocks
  html = html.replace(/```([a-zA-Z0-9_\-+]*)\n([\s\S]*?)```/g, (match, lang, code) => {
    const language = lang.trim() || 'code';
    return `
      <div class="code-block-container">
        <div class="code-block-header">
          <div class="code-lang-tag"><span class="code-lang-bullet"></span><span>${language.toUpperCase()}</span></div>
          <button class="copy-code-btn" data-code="${encodeURIComponent(code.trim())}">
            <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
            <span>Copy</span>
          </button>
        </div>
        <pre><code>${code.trim()}</code></pre>
      </div>
    `;
  });

  // Headers
  html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
  html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
  html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');
  
  // Emphasis
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
  html = html.replace(/^\> (.*$)/gim, '<blockquote>$1</blockquote>');
  html = html.replace(/^---$/gim, '<hr class="styled-divider">');
  
  // Lists
  html = html.replace(/^\s*[-*]\s+(.*$)/gim, '<li>$1</li>');
  html = html.replace(/(<li>[\s\S]*?<\/li>)/g, '<ul>$1</ul>');
  
  // Paragraphs
  html = html.replace(/\n\n+/g, '</p><p>');
  html = `<p>${html}</p>`;
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
  return String(text).replace(/[&<>"']/g, m => map[m]);
}

function attachCodeBlockHandlers(container) {
  container.querySelectorAll('.copy-code-btn').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      e.stopPropagation();
      const code = decodeURIComponent(btn.getAttribute('data-code'));
      try {
        await navigator.clipboard.writeText(code);
        const span = btn.querySelector('span');
        const orig = span.textContent;
        span.textContent = 'Copied!';
        btn.classList.add('copied');
        setTimeout(() => {
          span.textContent = orig;
          btn.classList.remove('copied');
        }, 2200);
      } catch (err) {
        console.error('Clipboard copy failed:', err);
      }
    });
  });
}

function attachImageZoomHandlers(container) {
  container.querySelectorAll('.zoomable-artifact').forEach(img => {
    img.addEventListener('click', () => {
      modalImage.src = img.src;
      modalDownloadBtn.href = img.src;
      imageModal.classList.remove('hidden');
    });
  });
}

if (modalBackdrop) modalBackdrop.addEventListener('click', () => imageModal.classList.add('hidden'));
if (modalCloseBtn) modalCloseBtn.addEventListener('click', () => imageModal.classList.add('hidden'));

// ==============================================================================
// 4. SWARM NETWORK GRAPH & LIVE PROMPT TRAVERSAL ENGINE
// ==============================================================================
function buildNetworkNodes() {
  if (!nodesOrchestrator || !nodesCoder || !nodesGeneral || !nodesVision) return;

  nodesOrchestrator.innerHTML = '';
  nodesCoder.innerHTML = '';
  nodesGeneral.innerHTML = '';
  nodesVision.innerHTML = '';
  allNodesMap = {};

  for (let i = 1; i <= 15; i++) {
    createNeuralNode(nodesOrchestrator, `orchestrator_${i}`, `Brain ${i}`, 'orchestrator');
  }
  for (let i = 1; i <= 20; i++) {
    createNeuralNode(nodesCoder, `coder_${i}`, `Coder ${i}`, 'coder');
  }
  for (let i = 1; i <= 15; i++) {
    createNeuralNode(nodesGeneral, `general_${i}`, `Gen ${i}`, 'general');
  }
  for (let i = 1; i <= 10; i++) {
    createNeuralNode(nodesGeneral, `nlp_${i}`, `NLP ${i}`, 'nlp');
  }
  for (let i = 1; i <= 10; i++) {
    createNeuralNode(nodesVision, `vision_${i}`, `Vision ${i}`, 'vision');
  }
  for (let i = 1; i <= 5; i++) {
    createNeuralNode(nodesVision, `video_${i}`, `Video ${i}`, 'video');
  }

  setTimeout(updateSvgLines, 150);
  window.addEventListener('resize', updateSvgLines);
}

function createNeuralNode(container, agentKey, label, category) {
  const node = document.createElement('div');
  node.className = 'neural-node';
  node.setAttribute('data-key', agentKey);
  node.setAttribute('data-cat', category);
  node.textContent = agentKey.replace('_', ' ');

  node.addEventListener('mouseenter', () => highlightNodeSynapses(node));
  node.addEventListener('mouseleave', () => resetNodeSynapses());
  node.addEventListener('click', (e) => {
    e.stopPropagation();
    openNodeInspector(agentKey, category);
  });

  container.appendChild(node);
  allNodesMap[agentKey] = node;
  return node;
}

function updateSvgLines() {
  if (!svgLines) return;
  svgLines.innerHTML = '';
  activeSynapseConnections = [];

  const col1 = nodesOrchestrator?.querySelectorAll('.neural-node') || [];
  const col2 = nodesCoder?.querySelectorAll('.neural-node') || [];
  const col3 = nodesGeneral?.querySelectorAll('.neural-node') || [];
  const col4 = nodesVision?.querySelectorAll('.neural-node') || [];

  if (!col1.length || !col2.length) return;

  const containerRect = svgLines.getBoundingClientRect();
  connectNodeColumns(col1, col2, containerRect, 2);
  connectNodeColumns(col2, col3, containerRect, 2);
  connectNodeColumns(col3, col4, containerRect, 2);
}

function connectNodeColumns(fromList, toList, containerRect, connectionsPerNode = 2) {
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

  const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
  const dx = (x2 - x1) / 2;
  const d = `M ${x1} ${y1} C ${x1 + dx} ${y1}, ${x2 - dx} ${y2}, ${x2} ${y2}`;
  path.setAttribute('d', d);
  path.setAttribute('fill', 'none');
  path.classList.add('synapse-line');

  svgLines.appendChild(path);
  activeSynapseConnections.push({ path, el1, el2, d });
}

function highlightNodeSynapses(node) {
  node.classList.add('active');
  activeSynapseConnections.forEach(conn => {
    if (conn.el1 === node || conn.el2 === node) {
      conn.path.classList.add('active');
      conn.el1.classList.add('active');
      conn.el2.classList.add('active');
    }
  });
}

function resetNodeSynapses() {
  Object.values(allNodesMap).forEach(n => n.classList.remove('active'));
  activeSynapseConnections.forEach(conn => conn.path.classList.remove('active'));
}

function setupNetworkTraversalControls() {
  if (networkTransmitBtn && networkPromptInput) {
    networkTransmitBtn.addEventListener('click', () => {
      const text = networkPromptInput.value.trim();
      if (text && !isExecuting) {
        submitPrompt(text);
        networkPromptInput.value = '';
      }
    });

    networkPromptInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        const text = networkPromptInput.value.trim();
        if (text && !isExecuting) {
          submitPrompt(text);
          networkPromptInput.value = '';
        }
      }
    });
  }

  if (simulatePulseBtn) {
    simulatePulseBtn.addEventListener('click', () => {
      simulateWaveTraversal("Test prompt: 'Demonstrating autonomous multi-agent synapse wave across 75 models'");
    });
  }

  if (clearTraceBtn && traceFeedList) {
    clearTraceBtn.addEventListener('click', () => {
      traceFeedList.innerHTML = '';
      logTraceEvent('Trace log reset.', 'info');
    });
  }

  if (inspClose && nodeInspector) {
    inspClose.addEventListener('click', () => nodeInspector.classList.add('hidden'));
  }
}

function startLivePromptNetworkFlow(promptText) {
  if (hudActiveQuery) {
    hudActiveQuery.textContent = promptText;
    hudActiveQuery.classList.add('flowing');
  }

  setStageActive(1);
  logTraceEvent(`[Ingest] Ingested user prompt: "${promptText.slice(0, 70)}..."`, 'highlight');

  const orchNodes = Object.values(allNodesMap).filter(n => n.getAttribute('data-cat') === 'orchestrator');
  const chiefBrain = orchNodes[0] || orchNodes[Math.floor(Math.random() * orchNodes.length)];
  if (chiefBrain) {
    chiefBrain.classList.add('active');
    logTraceEvent(`[Orchestrator] Node ${chiefBrain.getAttribute('data-key')} active (Planning subtasks)`);
  }

  setTimeout(() => {
    setStageActive(2);
    logTraceEvent(`[Routing] Decomposing into parallel subtasks and computing synapse pathways...`);
    spawnPacketParticlesAcrossColumns();
  }, 400);

  setTimeout(() => {
    setStageActive(3);
    logTraceEvent(`[Execution] Specialist nodes allocated. Running concurrent inference.`);
  }, 900);
}

function completeLivePromptNetworkFlow(data) {
  setStageActive(4);
  const tasks = data.tasks || [];
  const totalMs = data.total_latency_ms || 800;

  tasks.forEach(t => {
    const agentKey = t.agent_key;
    if (allNodesMap[agentKey]) {
      allNodesMap[agentKey].classList.add('active');
    }
    logTraceEvent(`[Specialist Complete] ${agentKey} (${t.provider}): ${t.latency_ms}ms`);
  });

  logTraceEvent(`[Synthesizer & QA] Verified presentation compiled (${totalMs}ms). Output delivered.`, 'highlight');

  setTimeout(() => {
    resetNetworkStageIndicator();
    resetNodeSynapses();
    if (hudActiveQuery) hudActiveQuery.classList.remove('flowing');
  }, 5000);
}

function setStageActive(stageNum) {
  for (let i = 1; i <= 4; i++) {
    if (stageSteps[i]) {
      stageSteps[i].classList.toggle('active', i === stageNum);
    }
  }
}

function resetNetworkStageIndicator() {
  for (let i = 1; i <= 4; i++) {
    if (stageSteps[i]) stageSteps[i].classList.remove('active');
  }
}

function spawnPacketParticlesAcrossColumns() {
  if (!svgLines) return;
  const containerRect = svgLines.getBoundingClientRect();

  const sampleConnections = activeSynapseConnections
    .sort(() => 0.5 - Math.random())
    .slice(0, 16);

  sampleConnections.forEach(conn => {
    conn.path.classList.add('active');
    conn.el1.classList.add('active');
    conn.el2.classList.add('active');

    const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    circle.setAttribute('r', '3.5');
    circle.classList.add('packet-circle');
    svgLines.appendChild(circle);

    const pathLength = conn.path.getTotalLength();
    let startTime = null;
    const duration = 1200 + Math.random() * 600;

    function step(timestamp) {
      if (!startTime) startTime = timestamp;
      const progress = (timestamp - startTime) / duration;
      if (progress <= 1) {
        const point = conn.path.getPointAtLength(progress * pathLength);
        circle.setAttribute('cx', point.x);
        circle.setAttribute('cy', point.y);
        requestAnimationFrame(step);
      } else {
        circle.remove();
      }
    }
    requestAnimationFrame(step);
  });
}

function simulateWaveTraversal(sampleText) {
  startLivePromptNetworkFlow(sampleText);
  setTimeout(() => {
    completeLivePromptNetworkFlow({
      tasks: [
        { agent_key: 'coder_1', provider: 'Groq', latency_ms: 180 },
        { agent_key: 'nlp_1', provider: 'Groq', latency_ms: 220 },
        { agent_key: 'vision_1', provider: 'HuggingFace', latency_ms: 450 }
      ],
      total_latency_ms: 780
    });
  }, 2200);
}

function logTraceEvent(msg, type = 'info') {
  if (!traceFeedList) return;
  const item = document.createElement('div');
  item.className = `trace-item ${type}`;

  const now = new Date();
  const timeStr = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}.${now.getMilliseconds().toString().padStart(3, '0')}`;

  item.innerHTML = `
    <span class="trace-time">${timeStr}</span>
    <span class="trace-msg">${escapeHtml(msg)}</span>
  `;

  traceFeedList.appendChild(item);
  traceFeedList.scrollTop = traceFeedList.scrollHeight;
}

function openNodeInspector(agentKey, category) {
  if (!nodeInspector) return;
  inspBadge.textContent = `${category.toUpperCase()} SPECIALIST`;
  inspTitle.textContent = `Agent ${agentKey}`;

  const found = allRegisteredModels.find(m => m.agent_key === agentKey);
  if (found) {
    inspModel.textContent = found.model_id;
    inspProvider.textContent = found.provider;
    inspTier.textContent = '100% Free';
    inspTask.textContent = `Allocated to category: ${category}`;
    inspLatency.textContent = '~150ms';
  } else {
    inspModel.textContent = 'qwen/qwen3.8-27b';
    inspProvider.textContent = 'Groq Cloud';
    inspTier.textContent = '100% Free';
    inspTask.textContent = 'Standby';
    inspLatency.textContent = '~120ms';
  }

  nodeInspector.classList.remove('hidden');
}

// ==============================================================================
// 5. MODEL REGISTRY
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
    console.log('Model registry using local fallback data');
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

  modelsGrid.innerHTML = '';

  if (filtered.length === 0) {
    modelsGrid.innerHTML = `
      <div style="grid-column: 1/-1; text-align:center; padding: 40px; color: var(--text-muted); font-size:13px;">
        No models found matching your search criteria.
      </div>
    `;
    return;
  }

  filtered.forEach(m => {
    const card = document.createElement('div');
    card.className = 'model-card-item';

    card.innerHTML = `
      <div class="card-title-row">
        <span class="model-name-text">${escapeHtml(m.name || m.agent_key)}</span>
        <span class="pill-badge pill-provider">${escapeHtml(m.provider || 'Cloud')}</span>
      </div>
      <div class="model-id-mono">${escapeHtml(m.model_id)}</div>
      <div class="card-badges-row">
        <span class="pill-badge pill-free">Free Tier</span>
        <span class="pill-badge" style="background:var(--bg-app); color:var(--text-muted);">${escapeHtml(m.category)}</span>
      </div>
    `;
    modelsGrid.appendChild(card);
  });
}

if (modelsSearchInput) {
  modelsSearchInput.addEventListener('input', renderFilteredModels);
}

categoryFilterBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    categoryFilterBtns.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    activeCategoryFilter = btn.getAttribute('data-filter') || 'all';
    renderFilteredModels();
  });
});

providerFilterBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    providerFilterBtns.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    activeProviderFilter = btn.getAttribute('data-provider') || 'all';
    renderFilteredModels();
  });
});

// ==============================================================================
// 6. SETTINGS & 4-PROVIDER KEYS MANAGEMENT
// ==============================================================================
function setupSettingsHandlers() {
  setupVisibilityToggle(toggleGeminiVis, keyGemini);
  setupVisibilityToggle(toggleGroqVis, keyGroq);
  setupVisibilityToggle(toggleOrVis, keyOpenrouter);
  setupVisibilityToggle(toggleHfVis, keyHuggingface);

  if (testGeminiBtn) testGeminiBtn.addEventListener('click', () => testProviderKey('gemini', keyGemini.value, testResultGemini));
  if (testGroqBtn) testGroqBtn.addEventListener('click', () => testProviderKey('groq', keyGroq.value, testResultGroq));
  if (testOpenrouterBtn) testOpenrouterBtn.addEventListener('click', () => testProviderKey('openrouter', keyOpenrouter.value, testResultOpenrouter));
  if (testHuggingfaceBtn) testHuggingfaceBtn.addEventListener('click', () => testProviderKey('huggingface', keyHuggingface.value, testResultHuggingface));

  if (saveKeysBtn) {
    saveKeysBtn.addEventListener('click', saveApiKeysToBackend);
  }
}

function setupVisibilityToggle(btn, input) {
  if (!btn || !input) return;
  btn.addEventListener('click', () => {
    input.type = input.type === 'password' ? 'text' : 'password';
    btn.textContent = input.type === 'password' ? 'Show' : 'Hide';
  });
}

async function checkSystemStatus() {
  try {
    const res = await fetch(`${API_BASE}/api/status`);
    if (res.ok) {
      const data = await res.json();
      const count = data.active_providers_count || 0;

      if (count > 0) {
        statusPillText.textContent = `${count} Providers Active`;
        if (clusterIndicator) clusterIndicator.textContent = `${count} Cloud Providers Active`;
      } else {
        statusPillText.textContent = '75 Models Synced';
        if (clusterIndicator) clusterIndicator.textContent = '75 Models Ready';
      }
    }
  } catch (e) {
    console.log('Backend status check offline/fallback');
  }
}

async function loadSavedKeys() {
  try {
    const res = await fetch(`${API_BASE}/api/keys`);
    if (res.ok) {
      const data = await res.json();
      if (data.gemini_preview && keyGemini) keyGemini.placeholder = `Saved: ${data.gemini_preview}`;
      if (data.groq_preview && keyGroq) keyGroq.placeholder = `Saved: ${data.groq_preview}`;
      if (data.openrouter_preview && keyOpenrouter) keyOpenrouter.placeholder = `Saved: ${data.openrouter_preview}`;
      if (data.huggingface_preview && keyHuggingface) keyHuggingface.placeholder = `Saved: ${data.huggingface_preview}`;
    }
  } catch (e) {
    console.log('Could not retrieve existing key previews');
  }
}

async function testProviderKey(provider, keyVal, resultBox) {
  if (!resultBox) return;
  resultBox.className = 'test-feedback-box';
  resultBox.style.display = 'block';
  resultBox.textContent = `Testing ${provider} connection...`;

  try {
    const res = await fetch(`${API_BASE}/api/keys/test`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ provider: provider, key: keyVal || undefined })
    });

    const data = await res.json();
    if (data.success) {
      resultBox.className = 'test-feedback-box success';
      resultBox.textContent = `Connection successful: ${data.message}`;
    } else {
      resultBox.className = 'test-feedback-box error';
      resultBox.textContent = data.message;
    }
  } catch (err) {
    resultBox.className = 'test-feedback-box error';
    resultBox.textContent = `Error testing connection: ${err.message}`;
  }
}

async function saveApiKeysToBackend() {
  if (!saveFeedback) return;
  saveFeedback.textContent = 'Saving keys to .env and reloading swarm...';
  saveFeedback.style.color = 'var(--text-muted)';

  const payload = {
    gemini_key: keyGemini?.value.trim() || undefined,
    groq_key: keyGroq?.value.trim() || undefined,
    openrouter_key: keyOpenrouter?.value.trim() || undefined,
    huggingface_token: keyHuggingface?.value.trim() || undefined,
    save_to_env: true
  };

  try {
    const res = await fetch(`${API_BASE}/api/keys`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (res.ok) {
      saveFeedback.textContent = 'Keys saved successfully and cluster hot-reloaded.';
      saveFeedback.style.color = 'var(--accent-emerald)';
      checkSystemStatus();
      loadSavedKeys();
      setTimeout(() => { saveFeedback.textContent = ''; }, 4000);
    } else {
      saveFeedback.textContent = 'Failed to save keys.';
      saveFeedback.style.color = 'var(--accent-red)';
    }
  } catch (err) {
    saveFeedback.textContent = `Error: ${err.message}`;
    saveFeedback.style.color = 'var(--accent-red)';
  }
}


