# GOD MODE: 75-Model Autonomous AI Swarm System

GOD MODE is an autonomous multi-agent swarm platform that orchestrates **75 AI models** simultaneously to decompose complex user prompts into parallel specialist subtasks, execute them concurrently across zero-cost cloud providers, synthesize deliverables, and certify output integrity via automated QA verification.

The platform features a clean **Anthropic Claude and OpenAI ChatGPT inspired user interface** paired with a **real-time prompt traversal engine** that visualizes data packet flows and neural routing across the swarm mesh with millisecond telemetry.

---

## Key Features

### 1. Claude & ChatGPT Inspired Professional Interface
* **Refined Design System**: Zinc and charcoal dark mode with warm linen light mode, crisp borders, and subtle terracotta and emerald accents.
* **Segmented Navigation**: Seamless switching between **Chat**, **Swarm Network**, **Model Registry**, and **API Keys & Settings**.
* **Centered Conversational Feed**: Clean chat column with starter directive cards, structured prose, syntax-highlighted code blocks with 1-click copy, and a floating composer capsule.
* **Collapsible Reasoning Drawer**: Step-by-step transparency into the multi-agent pipeline displaying agent roles, model IDs, cloud providers, and individual execution latencies.

### 2. Real-Time Swarm Network & Prompt Traversal Engine
* **Interactive 75-Node Mesh**: 4-column neural layout with dynamic bezier curves connecting Orchestrators, Coders, General/NLP specialists, and Vision/Media agents.
* **4-Stage Traversal Monitor**:
  * **Stage 1: Orchestrator Ingest** — Highlights the active Brain Orchestrator node decomposing the user's directive.
  * **Stage 2: Neural Synapse Route** — Launches glowing SVG packet particles across calculated synapse pathways.
  * **Stage 3: Specialist Execution** — Illuminates the exact coder, NLP, vision, and reasoning specialist nodes assigned to parallel subtasks.
  * **Stage 4: Synthesis & QA** — Validates the final verified presentation and logs latency telemetry.
* **Live Synapse Stream**: Millisecond-precision telemetry feed logging ingestion, subtask allocation, execution latencies, and verification status.
* **Interactive Transmit Bar**: Direct prompt transmission bar inside the network canvas to test neural routing in real time.
* **Bidirectional Sync**: Prompts submitted in either the Chat tab or Network tab run through the swarm, animate on the network mesh, and record deliverables in the chat session.

### 3. 100% Zero-Cost Cloud Provider Integrations
GOD MODE connects to 4 free API providers with zero subscription fees required:
* **Google Gemini API** (`aistudio.google.com`): Flagship reasoning, 1M token context, and orchestration with Gemini 2.5 Flash and Gemma 4 (15 RPM / 1,500 RPD free).
* **Groq Cloud API** (`console.groq.com`): High-speed LPU inference running Qwen 2.5 Coder, Llama 3.3 70B, and Compound MoE (30 RPM free).
* **OpenRouter API** (`openrouter.ai`): Access to 70+ free open-source models including DeepSeek R1, Minimax M3, and Mistral.
* **Hugging Face Token** (`huggingface.co`): Multimodal diffusion image generation (FLUX.1 Schnell, Stable Diffusion XL) and BERT NLP transformers.

### 4. Smart Cross-Provider Cascading Fallback
* If any provider encounters quota limits or rate throttling (HTTP 429), the swarm dispatcher automatically failovers across available providers in sub-seconds without interrupting the user request.

---

## Multi-Agent Swarm Pipeline

```
[ User Prompt ]
       │
       ▼
┌─────────────────────────────────────────┐
│  Stage 1: Chief Brain Orchestrator      │
│  - Analyzes directive & context         │
│  - Decomposes into 1-4 modular subtasks │
└─────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  Stage 2: Parallel Specialist Execution │
│  ├── Agent 1: Coder Specialist          │
│  ├── Agent 2: NLP & Translation         │
│  ├── Agent 3: Creative & Narrative      │
│  └── Agent 4: Multimodal AI Vision      │
└─────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  Stage 3: Presentation Synthesizer      │
│  - Compiles raw specialist outputs      │
│  - Preserves full syntax & code blocks  │
│  - Rehydrates visual artifacts          │
└─────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  Stage 4: QA Verifier & Auditor         │
│  - Audits answer completeness           │
│  - Validates code integrity & formatting│
└─────────────────────────────────────────┘
       │
       ▼
[ Final Verified Deliverable ]
```

---

## 75-Model Registry Matrix

| Specialist Column | Agent Count | Primary Model IDs | Core Responsibilities |
| :--- | :--- | :--- | :--- |
| **1. Orchestration** | 15 Models | `gemini-2.5-flash`, `groq/compound`, `allam-2-7b`, `gemini-3.6-flash`, `minimax-m3` | Directive decomposition, subtask planning, cross-agent coordination |
| **2. Coding** | 20 Models | `qwen-2.5-coder-32b`, `qwen3.8-27b`, `north-mini-code`, `laguna-s-2.1`, `gpt-oss-20b` | Production-grade software engineering, API design, debugging, algorithms |
| **3. Reasoning & NLP** | 25 Models | `llama-3.3-70b`, `gemma-4-31b`, `deepseek-r1`, `glm-5.2`, `ling-3.0-flash` | Multilingual translation, sentiment analysis, mathematics, deep reasoning |
| **4. Vision & Media** | 15 Models | `black-forest-labs/FLUX.1-schnell`, `stabilityai/sdxl`, `fal-ai/fast-svd` | Multimodal artwork generation, visual diagramming, video prompt direction |

---

## Installation & Setup

### Prerequisites
* Python 3.10 or higher
* Node.js 18+ (Optional, for Electron desktop app)

### 1. Clone the Repository
```bash
git clone https://github.com/B-Sheikh/GOD_MODE.git
cd GOD_MODE
```

### 2. Set Up Virtual Environment & Dependencies
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux / macOS
# or: venv\Scriptsctivate  # Windows

# Install required dependencies
pip install -r requirements.txt
```

### 3. Configure API Credentials (Zero-Cost)
Create a `.env` file from the provided example:
```bash
cp .env.example .env
```
Edit `.env` and add at least one free API key (or enter keys directly inside the Settings tab in the UI):
```ini
GEMINI_API_KEY=your_gemini_key_here
GROQ_API_KEY=your_groq_key_here
OPENROUTER_API_KEY=your_openrouter_key_here
HUGGINGFACE_API_TOKEN=your_hf_token_here
```

### 4. Run the Application

#### Option A: Web Browser Mode (FastAPI)
```bash
python main.py
```
Open `http://localhost:8000` in your web browser.

#### Option B: Electron Desktop App
```bash
# In terminal 1: Start backend
python main.py

# In terminal 2: Start Electron desktop client
cd jarvis-desktop
npm install
npm start
```

---

## API Endpoints Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/godmode` | Main swarm orchestrator. Accepts `{"prompt": "..."}` and returns verified deliverable with full task telemetry. |
| `GET` | `/api/status` | Returns system diagnostic status, provider connectivity, and masked key states. |
| `GET` | `/api/models` | Returns the complete catalog of 75 registered AI models with category and provider tags. |
| `GET` | `/api/keys` | Returns key configuration status and preview values. |
| `POST` | `/api/keys` | Updates API credentials, writes to `.env`, and hot-reloads the active swarm cluster. |
| `POST` | `/api/keys/test` | Verifies live connectivity for a specific provider (`gemini`, `groq`, `openrouter`, `huggingface`). |

---

## Project Structure

```
GOD_MODE/
├── api_clients.py          # Unified API dispatcher & cross-provider cascading fallback router
├── main.py                 # FastAPI backend, static asset server, and REST API routes
├── models_registry.py      # Registry mapping 75 models across 4 specialist columns
├── orchestrator.py         # Chief Brain Orchestrator prompt decomposition & parallel task runner
├── synthesizer.py          # Multimodal presentation synthesizer & code assembler
├── verifier.py             # QA verification agent & output compliance auditor
├── test_run.py             # End-to-end integration test script
├── requirements.txt        # Python package dependencies
├── .env.example            # Sample zero-cost environment configuration template
├── .gitignore              # Git ignore rules for virtual environments and credentials
├── LICENSE                 # MIT License
└── jarvis-desktop/         # Frontend user interface (Web & Electron Desktop)
    ├── index.html          # Semantic HTML structure, tabs, live HUD, and modals
    ├── styles.css          # Claude & ChatGPT design tokens, typography, and SVG synapse animations
    ├── renderer.js         # Real-time prompt traversal engine, network graph, and chat handlers
    ├── main.js             # Electron main process & IPC window handlers
    └── package.json        # Electron package definition
```

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
