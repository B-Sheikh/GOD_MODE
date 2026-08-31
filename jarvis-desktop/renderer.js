const { ipcRenderer } = require('electron');

const chatHistory = document.getElementById('chat-history');
const promptInput = document.getElementById('prompt-input');
const sendBtn = document.getElementById('send-btn');

// Tabs
const tabTerminal = document.getElementById('tab-terminal');
const tabNetwork = document.getElementById('tab-network');
const viewTerminal = document.getElementById('view-terminal');
const viewNetwork = document.getElementById('view-network');

const colInput = document.getElementById('col-input');
const colHidden1 = document.getElementById('col-hidden-1');
const colHidden2 = document.getElementById('col-hidden-2');
const colOutput = document.getElementById('col-output');
const svgLines = document.getElementById('network-lines');

let inputNodes = [];
let hidden1Nodes = [];
let hidden2Nodes = [];
let outputNodes = [];
let drawnLines = [];

function initNetwork() {
  for (let i = 1; i <= 15; i++) inputNodes.push(createNode(colInput));
  for (let i = 1; i <= 60; i++) hidden1Nodes.push(createNode(colHidden1));
  for (let i = 1; i <= 120; i++) hidden2Nodes.push(createNode(colHidden2));
  for (let i = 1; i <= 15; i++) outputNodes.push(createNode(colOutput));
}

function createNode(container) {
  const node = document.createElement('div');
  node.className = 'dense-node';
  container.appendChild(node);
  return node;
}
initNetwork();

// Tab Switching
function switchTab(tab) {
  if (tab === 'terminal') {
    tabTerminal.classList.add('active');
    tabNetwork.classList.remove('active');
    viewTerminal.classList.add('active');
    viewNetwork.classList.remove('active');
  } else {
    tabNetwork.classList.add('active');
    tabTerminal.classList.remove('active');
    viewNetwork.classList.add('active');
    viewTerminal.classList.remove('active');
  }
}
tabTerminal.addEventListener('click', () => switchTab('terminal'));
tabNetwork.addEventListener('click', () => switchTab('network'));

// Window Controls
document.getElementById('close-btn').addEventListener('click', () => {
  ipcRenderer.send('close-window');
});
document.getElementById('min-btn').addEventListener('click', () => {
  ipcRenderer.send('min-window');
});

// Messaging Logic
function appendMessage(role, text) {
  const msgDiv = document.createElement('div');
  msgDiv.classList.add('message', role);
  
  const avatar = document.createElement('div');
  avatar.classList.add('avatar');
  avatar.textContent = role === 'user' ? 'U' : '🧠';
  
  const content = document.createElement('div');
  content.classList.add('content');
  
  let formattedText = text;
  
  if (formattedText.includes('data:image')) {
    let imgMatches = formattedText.match(/(data:image\/[a-zA-Z]*;base64,[^\s]+)/g);
    if(imgMatches) {
      imgMatches.forEach(img => {
          formattedText = formattedText.replace(img, `<img src="${img}" alt="Generated Image" />`);
      });
    }
  }
  
  formattedText = formattedText.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
  formattedText = formattedText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  formattedText = formattedText.replace(/\n/g, '<br>');
  
  content.innerHTML = formattedText;
  
  msgDiv.appendChild(avatar);
  msgDiv.appendChild(content);
  chatHistory.appendChild(msgDiv);
  chatHistory.scrollTop = chatHistory.scrollHeight;
}

function showLoading() {
  const loadingId = 'loading-' + Date.now();
  const msgDiv = document.createElement('div');
  msgDiv.classList.add('message', 'system');
  msgDiv.id = loadingId;
  msgDiv.innerHTML = `
    <div class="avatar">⚙️</div>
    <div class="content loading-indicator">
      <span>Deploying 75+ Agents & Verifying...</span>
      <div class="dot"></div><div class="dot"></div><div class="dot"></div>
    </div>
  `;
  chatHistory.appendChild(msgDiv);
  chatHistory.scrollTop = chatHistory.scrollHeight;
  return loadingId;
}

// SVG Line Drawing Logic for Dense Visualization
function drawLine(el1, el2) {
  const rect1 = el1.getBoundingClientRect();
  const rect2 = el2.getBoundingClientRect();
  const containerRect = svgLines.getBoundingClientRect();
  
  const x1 = rect1.left + rect1.width/2 - containerRect.left;
  const y1 = rect1.top + rect1.height/2 - containerRect.top;
  const x2 = rect2.left + rect2.width/2 - containerRect.left;
  const y2 = rect2.top + rect2.height/2 - containerRect.top;
  
  const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
  line.setAttribute('x1', x1);
  line.setAttribute('y1', y1);
  line.setAttribute('x2', x2);
  line.setAttribute('y2', y2);
  line.classList.add('synapse-line', 'active');
  
  svgLines.appendChild(line);
  drawnLines.push(line);
}

function simulateMassiveDensity() {
  deactivateAllNodes();
  
  // Connect L1 to L2
  const activeL1 = getRandomSubset(inputNodes, 4, 8);
  const activeL2 = getRandomSubset(hidden1Nodes, 25, 40);
  drawConnections(activeL1, activeL2);
  
  // Connect L2 to L3
  const activeL3 = getRandomSubset(hidden2Nodes, 80, 100);
  drawConnections(activeL2, activeL3);
  
  // Connect L3 to L4
  const activeL4 = getRandomSubset(outputNodes, 2, 5);
  drawConnections(activeL3, activeL4);
}

function getRandomSubset(arr, min, max) {
  const count = Math.floor(Math.random() * (max - min + 1)) + min;
  const result = [];
  while(result.length < count && result.length < arr.length) {
    const item = arr[Math.floor(Math.random() * arr.length)];
    if(result.indexOf(item) === -1) result.push(item);
  }
  return result;
}

function drawConnections(fromNodes, toNodes) {
  fromNodes.forEach(n => n.classList.add('active'));
  toNodes.forEach(n => n.classList.add('active'));
  
  fromNodes.forEach(fromNode => {
    const toSubset = getRandomSubset(toNodes, 5, 20);
    toSubset.forEach(toNode => {
      drawLine(fromNode, toNode);
    });
  });
}

function deactivateAllNodes() {
  inputNodes.forEach(n => n.classList.remove('active'));
  hidden1Nodes.forEach(n => n.classList.remove('active'));
  hidden2Nodes.forEach(n => n.classList.remove('active'));
  outputNodes.forEach(n => n.classList.remove('active'));
  drawnLines.forEach(l => l.remove());
  drawnLines = [];
}

async function sendPrompt() {
  const prompt = promptInput.value.trim();
  if (!prompt) return;
  
  promptInput.value = '';
  promptInput.style.height = '60px';
  
  appendMessage('user', prompt);
  const loadingId = showLoading();

  switchTab('network');
  simulateMassiveDensity();

  try {
    const res = await fetch('http://localhost:8000/godmode', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt: prompt })
    });

    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    const data = await res.json();
    
    document.getElementById(loadingId).remove();
    appendMessage('jarvis', data.output || "Error: No output received.");

  } catch (error) {
    document.getElementById(loadingId).remove();
    appendMessage('system', `System Failure: ${error.message}. Ensure backend is running.`);
  } finally {
    setTimeout(() => {
        switchTab('terminal');
        deactivateAllNodes();
    }, 3000); // Wait 3 seconds so user can admire the network before it switches back
  }
}

sendBtn.addEventListener('click', sendPrompt);
promptInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendPrompt();
  }
});
promptInput.addEventListener('input', function() {
  this.style.height = '60px';
  this.style.height = (this.scrollHeight) + 'px';
});

promptInput.focus();
