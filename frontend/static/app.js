/**
 * DocuForge AI - Studio Frontend Controller
 */

let currentTab = 'dashboard';
let projects = [];
let budgetData = null;
let selectedProjectId = null;

// Tab Titles and Subtitles
const tabHeaders = {
  dashboard: { title: "Studio Dashboard", subtitle: "Autonomous 13-agent documentary production pipeline" },
  projects: { title: "Documentary Projects", subtitle: "All active and completed production packages" },
  topics: { title: "Topic Discovery System", subtitle: "AI-researched topic candidates with 100-point validation" },
  research: { title: "Deep Research & Evidence Dossier", subtitle: "Source verification, primary records, and classified claims" },
  script: { title: "Script Studio", subtitle: "10-beat narrative structure & sentence-level visual planning" },
  'visual-director': { title: "Documentary Creative Director", subtitle: "Visual identity, scene pacing, and shot manifest" },
  footage: { title: "Real Footage Library", subtitle: "Permitted assets from free archives (NASA, LOC, Archives, Pexels)" },
  approval: { title: "Mandatory Asset Approval Dashboard", subtitle: "Hard human approval gate for all footage and imagery" },
  storyboard: { title: "Scene Storyboard", subtitle: "Synchronized visual and narration timeline review" },
  animation: { title: "Cinematic Animation Studio", subtitle: "Animated maps, data charts, and document text reveals" },
  audio: { title: "Narration & Sound Design", subtitle: "Segmented natural TTS, atmospheric audio & ducking" },
  rendering: { title: "Video Rendering Pipeline", subtitle: "Local FFmpeg 1080p multi-track compositing worker" },
  qc: { title: "Quality Control Center", subtitle: "Automated checks for black frames, audio clipping, and sync" },
  thumbnails: { title: "Thumbnail Studio", subtitle: "Dual 1280x720 concepts with mobile scale readability" },
  completed: { title: "Completed Documentaries", subtitle: "Ready-to-upload YouTube packages and production reports" },
  budget: { title: "Budget & API Usage", subtitle: "Strict $50.00 monthly ceiling & per-agent cost tracking" },
  settings: { title: "Studio Settings", subtitle: "API keys, storage configuration, and render limits" }
};

document.addEventListener("DOMContentLoaded", () => {
  refreshStudioData();
});

async function refreshStudioData() {
  await Promise.all([loadBudget(), loadProjects()]);
  renderCurrentTab();
}

async function loadBudget() {
  try {
    const res = await fetch("/api/budget/status");
    const json = await res.json();
    if (json.status === "success") {
      budgetData = json.budget;
      updateBudgetWidget(budgetData);
    }
  } catch (err) {
    console.error("Failed to load budget:", err);
  }
}

function updateBudgetWidget(b) {
  if (!b) return;
  document.getElementById("budget-ceiling-text").innerText = `$${b.budget_ceiling_usd.toFixed(2)}`;
  document.getElementById("budget-spent-text").innerText = `$${b.total_spent_usd.toFixed(2)}`;
  document.getElementById("budget-remaining-text").innerText = `$${b.remaining_usd.toFixed(2)} remaining`;

  const pct = Math.min(100, (b.total_spent_usd / b.budget_ceiling_usd) * 100);
  const bar = document.getElementById("budget-bar");
  bar.style.width = `${pct}%`;

  const badge = document.getElementById("budget-status-badge");
  if (b.is_locked) {
    badge.innerText = "LOCKED";
    badge.style.color = "var(--accent-rose)";
    bar.style.background = "var(--accent-rose)";
  } else if (b.is_warning) {
    badge.innerText = "WARNING";
    badge.style.color = "var(--accent-gold)";
    bar.style.background = "var(--accent-gold)";
  } else {
    badge.innerText = "NORMAL";
    badge.style.color = "var(--accent-emerald)";
    bar.style.background = "linear-gradient(90deg, #10b981, #f59e0b)";
  }
}

async function loadProjects() {
  try {
    const res = await fetch("/api/projects");
    const json = await res.json();
    if (json.status === "success") {
      projects = json.projects;
      const countEl = document.getElementById("sidebar-proj-count");
      if (countEl) countEl.innerText = projects.length;
    }
  } catch (err) {
    console.error("Failed to load projects:", err);
  }
}

function switchTab(tabId) {
  currentTab = tabId;
  document.querySelectorAll(".nav-item").forEach(item => {
    item.classList.remove("active");
  });
  
  const activeLink = Array.from(document.querySelectorAll(".nav-item")).find(el => 
    el.getAttribute("onclick") && el.getAttribute("onclick").includes(`'${tabId}'`)
  );
  if (activeLink) activeLink.classList.add("active");

  const header = tabHeaders[tabId] || { title: "Studio View", subtitle: "" };
  document.getElementById("view-title").innerText = header.title;
  document.getElementById("view-subtitle").innerText = header.subtitle;

  renderCurrentTab();
}

function renderCurrentTab() {
  const container = document.getElementById("main-content");
  if (!container) return;

  switch (currentTab) {
    case 'dashboard':
      renderDashboard(container);
      break;
    case 'projects':
      renderProjects(container);
      break;
    case 'budget':
      renderBudgetView(container);
      break;
    case 'topics':
      renderTopicDiscovery(container);
      break;
    case 'research':
      renderEvidenceDossier(container);
      break;
    case 'script':
      renderScriptStudio(container);
      break;
    case 'visual-director':
      renderVisualDirector(container);
      break;
    case 'footage':
    case 'approval':
      renderAssetApprovalDashboard(container);
      break;
    case 'storyboard':
      renderStoryboardCanvas(container);
      break;
    case 'animation':
      renderAnimationStudio(container);
      break;
    case 'audio':
      renderAudioDeck(container);
      break;
    case 'rendering':
      renderVideoRenderingConsole(container);
      break;
    case 'qc':
      renderQualityControlCenter(container);
      break;
    case 'thumbnails':
      renderThumbnailStudio(container);
      break;
    case 'completed':
      renderCompletedDocumentariesDeck(container);
      break;
    case 'settings':
      renderSettingsView(container);
      break;
    default:
      container.innerHTML = `<div class="section-panel"><p>Select a section from the navigation sidebar.</p></div>`;
  }
}

function getStatusBadge(status) {
  const map = {
    'TOPIC_SELECTION': { text: '1. Topic Selection', class: 'badge-topic-sel' },
    'RESEARCH_IN_PROGRESS': { text: '2. Researching', class: 'badge-research' },
    'FACT_CHECKING': { text: '3. Fact Checking', class: 'badge-research' },
    'SCRIPTING': { text: '4. Scripting', class: 'badge-script' },
    'SCRIPT_REVIEW': { text: '5. Script Review [GATE]', class: 'badge-review' },
    'VISUAL_PLANNING': { text: '6. Visual Planning', class: 'badge-assets' },
    'FOOTAGE_DISCOVERY': { text: '7. Footage Discovery', class: 'badge-assets' },
    'ASSETS_PENDING_APPROVAL': { text: '8. Asset Approval [MANDATORY]', class: 'badge-review' },
    'STORYBOARD_REVIEW': { text: '9. Storyboard Review [GATE]', class: 'badge-review' },
    'NARRATION_GENERATION': { text: '10. Narration & Audio', class: 'badge-render' },
    'ANIMATION_SYNTHESIS': { text: '11. Animation Synthesis', class: 'badge-render' },
    'EDITING_RENDERING': { text: '12. Rendering Video', class: 'badge-render' },
    'QUALITY_CONTROL': { text: '13. QC Analysis', class: 'badge-review' },
    'THUMBNAIL_GENERATION': { text: '14. Thumbnails', class: 'badge-assets' },
    'EXPORT_READY': { text: '15. Export Ready', class: 'badge-completed' },
    'COMPLETED': { text: 'Completed', class: 'badge-completed' },
    'FAILED': { text: 'Failed / Needs Repair', class: 'badge-review' }
  };
  const item = map[status] || { text: status, class: 'badge-topic-sel' };
  return `<span class="badge ${item.class}">${item.text}</span>`;
}

function renderDashboard(container) {
  const activeCount = projects.filter(p => p.status !== 'COMPLETED').length;
  const completedCount = projects.filter(p => p.status === 'COMPLETED').length;
  const totalBudgetSpent = budgetData ? budgetData.total_spent_usd.toFixed(2) : "0.00";
  const remainingBudget = budgetData ? budgetData.remaining_usd.toFixed(2) : "50.00";

  container.innerHTML = `
    <div class="grid-cols-4">
      <div class="stat-card">
        <div class="stat-label">Monthly Target</div>
        <div class="stat-value">7 Docs</div>
        <div class="stat-desc">~20 min duration each</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Active Productions</div>
        <div class="stat-value">${activeCount}</div>
        <div class="stat-desc">${completedCount} completed this month</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Monthly Budget Spent</div>
        <div class="stat-value">$${totalBudgetSpent}</div>
        <div class="stat-desc">Hard ceiling: $50.00</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Remaining Budget</div>
        <div class="stat-value" style="color: var(--accent-emerald)">$${remainingBudget}</div>
        <div class="stat-desc">Free footage & local rendering</div>
      </div>
    </div>

    <div class="section-panel">
      <div class="section-panel-header">
        <h3>Active Documentary Productions</h3>
        <button class="btn btn-primary" onclick="openNewProjectModal()">+ New Project</button>
      </div>
      ${renderProjectsTable(projects.slice(0, 5))}
    </div>

    <div class="section-panel">
      <div class="section-panel-header">
        <h3>Autonomous Pipeline Architecture</h3>
      </div>
      <p style="font-size: 13px; color: var(--text-muted); line-height: 1.6;">
        DocuForge AI operates with 13 specialized autonomous agents across 20 distinct production steps.
        Hard human approval checkpoints are enforced at <strong>Script Review</strong>, 
        <strong>Asset Approval Dashboard</strong>, and <strong>Storyboard Review</strong>.
        Renderings are executed locally via FFmpeg with zero cloud GPU fees.
      </p>
    </div>
  `;
}

function renderProjects(container) {
  container.innerHTML = `
    <div class="section-panel">
      <div class="section-panel-header">
        <h3>All Documentary Projects (${projects.length})</h3>
        <button class="btn btn-primary" onclick="openNewProjectModal()">+ New Documentary</button>
      </div>
      ${renderProjectsTable(projects)}
    </div>
  `;
}

function renderProjectsTable(list) {
  if (!list || list.length === 0) {
    return `<div style="padding: 30px; text-align: center; color: var(--text-muted);">
      No documentary projects created yet. Click "+ New Documentary" to launch one.
    </div>`;
  }

  const rows = list.map(p => `
    <tr>
      <td style="font-weight: 600;">${escapeHtml(p.title)}</td>
      <td><span class="badge badge-topic-sel">${p.pillar}</span></td>
      <td>${p.target_duration_mins} mins</td>
      <td>${getStatusBadge(p.status)}</td>
      <td>$${(p.budget_spent_usd || 0).toFixed(2)}</td>
      <td>
        <button class="btn btn-secondary" style="padding: 4px 8px; font-size: 11px;" onclick="viewProjectDetails('${p.id}')">Open Studio</button>
        <button class="btn btn-danger" style="padding: 4px 8px; font-size: 11px; margin-left: 4px;" onclick="deleteProject('${p.id}')">Delete</button>
      </td>
    </tr>
  `).join("");

  return `
    <table class="data-table">
      <thead>
        <tr>
          <th>Documentary Title</th>
          <th>Pillar</th>
          <th>Target Duration</th>
          <th>Current Pipeline Stage</th>
          <th>Cost</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        ${rows}
      </tbody>
    </table>
  `;
}

function renderBudgetView(container) {
  const b = budgetData || { budget_ceiling_usd: 50, total_spent_usd: 0, remaining_usd: 50 };
  container.innerHTML = `
    <div class="grid-cols-4">
      <div class="stat-card">
        <div class="stat-label">Monthly Ceiling</div>
        <div class="stat-value">$${b.budget_ceiling_usd.toFixed(2)}</div>
        <div class="stat-desc">Hard spending limit</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Total Spent</div>
        <div class="stat-value">$${b.total_spent_usd.toFixed(2)}</div>
        <div class="stat-desc">API operations ledger</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Remaining</div>
        <div class="stat-value" style="color: var(--accent-emerald);">$${b.remaining_usd.toFixed(2)}</div>
        <div class="stat-desc">Available for production</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Status</div>
        <div class="stat-value" style="font-size: 18px;">${b.is_locked ? "LOCKED" : (b.is_warning ? "WARNING" : "OPERATIONAL")}</div>
        <div class="stat-desc">${b.is_locked ? "Spending blocked" : "Automatic cost tracking active"}</div>
      </div>
    </div>

    <div class="section-panel">
      <div class="section-panel-header">
        <h3>Budget Allocation & Optimization Strategy</h3>
      </div>
      <p style="font-size: 13px; color: var(--text-muted); line-height: 1.6; margin-bottom: 16px;">
        DocuForge AI targets ~$30/month across 7 documentaries (~$4.20 per 20-minute video):
      </p>
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; font-size: 12px;">
        <div style="padding: 12px; background: var(--bg-card); border-radius: 6px;">
          <strong>Research & Discovery:</strong> $3.00/mo (cached queries)
        </div>
        <div style="padding: 12px; background: var(--bg-card); border-radius: 6px;">
          <strong>Scriptwriting:</strong> $2.00/mo (10-beat prompts)
        </div>
        <div style="padding: 12px; background: var(--bg-card); border-radius: 6px;">
          <strong>Fact-Checking:</strong> $2.00/mo (cross-verifications)
        </div>
        <div style="padding: 12px; background: var(--bg-card); border-radius: 6px;">
          <strong>Narration:</strong> $12.00/mo (Edge-TTS / ElevenLabs)
        </div>
        <div style="padding: 12px; background: var(--bg-card); border-radius: 6px;">
          <strong>Thumbnails & Visuals:</strong> $5.00/mo
        </div>
        <div style="padding: 12px; background: var(--bg-card); border-radius: 6px;">
          <strong>Footage & Music:</strong> $0.00 (Public domain & free archives)
        </div>
        <div style="padding: 12px; background: var(--bg-card); border-radius: 6px;">
          <strong>1080p Rendering:</strong> $0.00 (Local FFmpeg worker)
        </div>
      </div>
    </div>
  `;
}

let studioSettingsData = null;
let liveDiagnosticsData = null;
let isTestingConnections = false;

async function renderSettingsView(container) {
  try {
    const res = await fetch("/api/settings");
    const json = await res.json();
    if (json.status === "success") {
      studioSettingsData = json.settings;
    }
  } catch (e) {
    console.error("Failed to load settings:", e);
  }

  const s = studioSettingsData || {};
  const flags = s.status_flags || {};

  container.innerHTML = `
    <div class="section-panel">
      <div class="section-panel-header">
        <div>
          <h3>Live Production Connectors, API Keys & Free Cloud Deployment</h3>
          <p style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">
            Configure Claude Sonnet 5.5, ElevenLabs Documentary Narrator, and Live Public Domain Archives (NASA, Wikimedia, Internet Archive)
          </p>
        </div>
        <div style="display: flex; gap: 10px;">
          <button class="btn btn-secondary" onclick="handleTestLiveConnections()" ${isTestingConnections ? 'disabled' : ''}>
            ${isTestingConnections ? 'Pinging APIs...' : '🔌 Test Live Connections'}
          </button>
          <button class="btn btn-primary" onclick="handleSaveStudioSettings()">
            💾 Save Live Configuration
          </button>
        </div>
      </div>

      <!-- Connection Status Banner -->
      <div class="script-metrics-bar" style="margin-bottom: 24px;">
        <div class="script-metric-item">
          <span class="script-metric-val" style="color: ${flags.anthropic_connected ? '#34d399' : '#fbbf24'}; font-size: 15px;">
            ${flags.anthropic_connected ? '● LIVE' : '○ FALLBACK'}
          </span>
          <span class="script-metric-lbl">Claude Sonnet 5.5 LLM</span>
        </div>
        <div class="script-metric-item">
          <span class="script-metric-val" style="color: ${flags.elevenlabs_connected ? '#34d399' : '#38bdf8'}; font-size: 15px;">
            ${flags.elevenlabs_connected ? '● ELEVENLABS HD' : '● LOCAL EBU R128'}
          </span>
          <span class="script-metric-lbl">Documentary Narration TTS</span>
        </div>
        <div class="script-metric-item">
          <span class="script-metric-val" style="color: #34d399; font-size: 15px;">● CONNECTED ($0)</span>
          <span class="script-metric-lbl">NASA / Wikimedia / Internet Archive</span>
        </div>
        <div class="script-metric-item">
          <span class="script-metric-val" style="color: ${flags.pexels_connected || flags.pixabay_connected ? '#34d399' : '#94a3b8'}; font-size: 15px;">
            ${flags.pexels_connected || flags.pixabay_connected ? '● ACTIVE' : '○ OPTIONAL'}
          </span>
          <span class="script-metric-lbl">Pexels / Pixabay Stock API</span>
        </div>
      </div>

      ${liveDiagnosticsData ? renderDiagnosticsResultBox(liveDiagnosticsData) : ''}

      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(380px, 1fr)); gap: 20px;">
        <!-- 1. Claude Sonnet 5.5 & LLM Engine -->
        <div style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 8px; padding: 18px;">
          <h4 style="font-size: 14px; font-weight: 700; color: #fff; margin-bottom: 12px;">
            🧠 1. Deep Research & 3,000-Word Script Engine (Claude Sonnet 5.5)
          </h4>
          <div class="form-group">
            <label class="form-label">Primary LLM Provider</label>
            <select id="set-llm-provider" class="form-select">
              <option value="anthropic" ${s.llm_provider === 'anthropic' ? 'selected' : ''}>Anthropic Claude (Sonnet 5.5 / 4.5 — Recommended)</option>
              <option value="openai" ${s.llm_provider === 'openai' ? 'selected' : ''}>OpenAI (GPT-4o)</option>
              <option value="gemini" ${s.llm_provider === 'gemini' ? 'selected' : ''}>Google Gemini (2.5 Flash / Pro)</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Claude Model Identifier / Alias</label>
            <input type="text" id="set-custom-model" class="form-input" value="${escapeHtml(s.custom_model_alias || 'claude-sonnet-5.5')}" placeholder="claude-sonnet-5.5">
          </div>
          <div class="form-group">
            <label class="form-label">Anthropic API Key (sk-ant-...)</label>
            <input type="password" id="set-anthropic-key" class="form-input" value="${escapeHtml(s.anthropic_api_key || '')}" placeholder="sk-ant-api03-...">
          </div>
          <div class="form-group">
            <label class="form-label">Target Documentary Script Length (Words)</label>
            <input type="number" id="set-target-words" class="form-input" value="${s.script_target_words || 2800}">
          </div>
        </div>

        <!-- 2. Documentary Voiceover TTS Engine -->
        <div style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 8px; padding: 18px;">
          <h4 style="font-size: 14px; font-weight: 700; color: #fff; margin-bottom: 12px;">
            🎙️ 2. Broadcast Documentary Voiceover (ElevenLabs Multilingual v2)
          </h4>
          <div class="form-group">
            <label class="form-label">Voiceover Synthesis Engine</label>
            <select id="set-tts-provider" class="form-select">
              <option value="elevenlabs" ${s.tts_provider === 'elevenlabs' ? 'selected' : ''}>ElevenLabs Multilingual v2 (Best Documentary Quality)</option>
              <option value="openai_tts" ${s.tts_provider === 'openai_tts' ? 'selected' : ''}>OpenAI TTS-1-HD (Onyx Documentary Narrator)</option>
              <option value="local_flite" ${s.tts_provider === 'local_flite' ? 'selected' : ''}>Local FFmpeg Libflite ($0 Offline Fallback)</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">ElevenLabs API Key</label>
            <input type="password" id="set-elevenlabs-key" class="form-input" value="${escapeHtml(s.elevenlabs_api_key || '')}" placeholder="Paste ElevenLabs API Key...">
          </div>
          <div class="form-group">
            <label class="form-label">ElevenLabs Documentary Voice Profile</label>
            <select id="set-elevenlabs-voice" class="form-select">
              <option value="JBFqnCBsd6RMkjVDRZzb" ${s.elevenlabs_voice_id === 'JBFqnCBsd6RMkjVDRZzb' ? 'selected' : ''}>George — Deep Investigative Narrator (MagnatesMedia style)</option>
              <option value="pNInz6obpgDQGcFmaJgB" ${s.elevenlabs_voice_id === 'pNInz6obpgDQGcFmaJgB' ? 'selected' : ''}>Adam — Authoritative Documentary Narrator</option>
              <option value="nPczCjzI2devNBz1zQrb" ${s.elevenlabs_voice_id === 'nPczCjzI2devNBz1zQrb' ? 'selected' : ''}>Brian — Deep Cinematic Storyteller (Fern style)</option>
              <option value="onwK4e9ZLuTAKqWW03F9" ${s.elevenlabs_voice_id === 'onwK4e9ZLuTAKqWW03F9' ? 'selected' : ''}>Daniel — British Geopolitical Narrator (Johnny Harris style)</option>
            </select>
          </div>
          <div style="font-size: 11px; color: var(--text-muted); margin-top: 8px;">
            All voice tracks are automatically mastered through FFmpeg EBU R128 (-14.0 LUFS) with -16 dB ambient BGM ducking.
          </div>
        </div>

        <!-- 3. Public Domain & Free Stock Archives -->
        <div style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 8px; padding: 18px;">
          <h4 style="font-size: 14px; font-weight: 700; color: #fff; margin-bottom: 12px;">
            🎞️ 3. Free Public Archives & Optional Stock Keys
          </h4>
          <div style="font-size: 12px; color: #34d399; background: rgba(16,185,129,0.1); padding: 10px; border-radius: 6px; margin-bottom: 14px;">
            ✓ <strong>NASA Images & Video API</strong>, <strong>Wikimedia Commons</strong>, and <strong>Internet Archive</strong> are connected natively with zero API keys required.
          </div>
          <div class="form-group">
            <label class="form-label">Pexels Free API Key (Optional — pexels.com/api)</label>
            <input type="password" id="set-pexels-key" class="form-input" value="${escapeHtml(s.pexels_api_key || '')}" placeholder="Optional free Pexels key...">
          </div>
          <div class="form-group">
            <label class="form-label">Pixabay Free API Key (Optional — pixabay.com/api/docs)</label>
            <input type="password" id="set-pixabay-key" class="form-input" value="${escapeHtml(s.pixabay_api_key || '')}" placeholder="Optional free Pixabay key...">
          </div>
          <div class="form-group">
            <label class="form-label">Optional OpenAI / Gemini Backup Key</label>
            <input type="password" id="set-openai-key" class="form-input" value="${escapeHtml(s.openai_api_key || '')}" placeholder="sk-proj-... (Optional backup)">
          </div>
        </div>

        <!-- 4. Free Cloud Deployment Blueprint -->
        <div style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 8px; padding: 18px;">
          <h4 style="font-size: 14px; font-weight: 700; color: #fff; margin-bottom: 12px;">
            ☁️ 4. Free Cloud Deployment Ready (Hugging Face Spaces + Render)
          </h4>
          <p style="font-size: 12px; color: #cbd5e1; line-height: 1.5; margin-bottom: 10px;">
            This repository includes pre-configured production files for <strong>100% Free Cloud Hosting</strong> with FFmpeg 1080p rendering:
          </p>
          <ul style="font-size: 12px; color: var(--text-muted); padding-left: 18px; line-height: 1.6;">
            <li><strong>Hugging Face Spaces (Recommended Free Tier)</strong>: 16 GB RAM, 2 vCPU, free Docker container running on Port 7860 with full FFmpeg + OpenCV.</li>
            <li><strong>Render.com Free Web Service</strong>: Automated deployment via included <code>render.yaml</code> and <code>Dockerfile</code>.</li>
            <li><strong>Monthly Budget Hard Cap</strong>: Strictly locked at <strong>$50.00/month</strong> ($40.00 warning threshold, $0.00 local/container FFmpeg rendering).</li>
          </ul>
        </div>
      </div>
    </div>
  `;
}

function renderDiagnosticsResultBox(diag) {
  const llm = diag.llm || {};
  const arch = diag.public_archives || {};
  const tts = diag.tts || {};
  return `
    <div style="background: rgba(56, 189, 248, 0.08); border: 1px solid rgba(56, 189, 248, 0.35); border-radius: 8px; padding: 16px; margin-bottom: 20px; font-size: 12px;">
      <h4 style="color: #38bdf8; font-size: 13px; margin-bottom: 8px;">🔌 Live Connection Diagnostic Results</h4>
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 12px;">
        <div>
          <strong>LLM (${escapeHtml(llm.model || 'Claude')}):</strong>
          <div style="color: ${llm.connected ? '#34d399' : '#fbbf24'}; margin-top: 2px;">${escapeHtml(llm.message || '')}</div>
        </div>
        <div>
          <strong>Voiceover (${escapeHtml(tts.provider || 'TTS')}):</strong>
          <div style="color: #34d399; margin-top: 2px;">${escapeHtml(tts.message || '')}</div>
        </div>
        <div>
          <strong>Public Archives:</strong>
          <div style="color: #34d399; margin-top: 2px;">${escapeHtml(arch.message || '')}</div>
        </div>
      </div>
    </div>
  `;
}

async function handleSaveStudioSettings() {
  const payload = {
    llm_provider: document.getElementById("set-llm-provider").value,
    custom_model_alias: document.getElementById("set-custom-model").value.trim(),
    llm_model: document.getElementById("set-custom-model").value.trim() || "claude-sonnet-4-5-20250929",
    anthropic_api_key: document.getElementById("set-anthropic-key").value.trim(),
    script_target_words: parseInt(document.getElementById("set-target-words").value) || 2800,
    tts_provider: document.getElementById("set-tts-provider").value,
    elevenlabs_api_key: document.getElementById("set-elevenlabs-key").value.trim(),
    elevenlabs_voice_id: document.getElementById("set-elevenlabs-voice").value,
    pexels_api_key: document.getElementById("set-pexels-key").value.trim(),
    pixabay_api_key: document.getElementById("set-pixabay-key").value.trim(),
    openai_api_key: document.getElementById("set-openai-key").value.trim()
  };

  try {
    const res = await fetch("/api/settings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const json = await res.json();
    if (json.status === "success") {
      studioSettingsData = json.settings;
      alert("Live Studio Settings & API Keys saved!");
      renderSettingsView(document.getElementById("main-content"));
    } else {
      alert("Error saving settings: " + json.message);
    }
  } catch (err) {
    alert("Network error: " + err.message);
  }
}

async function handleTestLiveConnections() {
  isTestingConnections = true;
  renderSettingsView(document.getElementById("main-content"));
  try {
    const res = await fetch("/api/settings/test-connection", { method: "POST" });
    const json = await res.json();
    if (json.status === "success") {
      liveDiagnosticsData = json.diagnostics;
    }
  } catch (err) {
    alert("Diagnostic error: " + err.message);
  } finally {
    isTestingConnections = false;
    renderSettingsView(document.getElementById("main-content"));
  }
}

function renderPhasePlaceholder(container, title, description) {
  container.innerHTML = `
    <div class="section-panel">
      <div class="section-panel-header">
        <h3>${title}</h3>
      </div>
      <div style="padding: 24px 12px; text-align: center;">
        <div style="font-size: 32px; margin-bottom: 12px;">🎬</div>
        <h4 style="font-size: 16px; margin-bottom: 8px;">Pipeline Stage Ready</h4>
        <p style="font-size: 13px; color: var(--text-muted); max-width: 500px; margin: 0 auto 16px;">
          ${description}
        </p>
        <button class="btn btn-secondary" onclick="switchTab('projects')">Select Project to Inspect</button>
      </div>
    </div>
  `;
}

// Modal handling
function openNewProjectModal() {
  document.getElementById("new-project-modal").style.display = "flex";
}

function closeNewProjectModal() {
  document.getElementById("new-project-modal").style.display = "none";
}

async function handleCreateProject(e) {
  e.preventDefault();
  const rawTitle = document.getElementById("proj-title").value.trim();
  const title = rawTitle || "Autonomous Topic Discovery Session";
  const pillar = document.getElementById("proj-pillar").value;
  const duration = parseInt(document.getElementById("proj-duration").value);

  try {
    const res = await fetch("/api/projects", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, pillar, target_duration_mins: duration })
    });
    const json = await res.json();
    if (json.status === "success") {
      closeNewProjectModal();
      document.getElementById("new-project-form").reset();
      selectedProjectId = json.project.id;
      await refreshStudioData();
      switchTab("topics");
      if (!rawTitle) {
        triggerTopicDiscovery(json.project.id);
      }
    } else {
      alert("Error creating project: " + json.message);
    }
  } catch (err) {
    alert("Network error: " + err.message);
  }
}

async function handleAutoStartTopicDiscovery() {
  try {
    const res = await fetch("/api/projects", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        title: "Autonomous Topic Discovery Session",
        pillar: "BUSINESS",
        target_duration_mins: 20
      })
    });
    const json = await res.json();
    if (json.status === "success") {
      selectedProjectId = json.project.id;
      await refreshStudioData();
      await triggerTopicDiscovery(json.project.id);
    }
  } catch (err) {
    alert("Error starting discovery: " + err.message);
  }
}

async function deleteProject(id) {
  if (!confirm("Are you sure you want to delete this documentary project?")) return;
  try {
    const res = await fetch(`/api/projects/${id}`, { method: "DELETE" });
    const json = await res.json();
    if (json.status === "success") {
      await refreshStudioData();
    }
  } catch (err) {
    alert("Error deleting project: " + err.message);
  }
}

function viewProjectDetails(id) {
  selectedProjectId = id;
  switchTab("topics");
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/[&<>"']/g, m => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  })[m]);
}

// --- Phase 2: Topic Discovery Logic ---

let projectTopics = [];
let rejectedTopics = [];
let isDiscovering = false;

async function renderTopicDiscovery(container) {
  if (projects.length === 0) {
    container.innerHTML = `
      <div class="section-panel" style="text-align: center; padding: 40px;">
        <h3>Autonomous Topic Discovery Agent</h3>
        <p style="color: var(--text-muted); font-size: 13px; margin: 12px 0 20px;">
          Let the AI Topic Discovery Agent scan trends, score candidates on a 100-point matrix, and present 5 vetted documentary topics for you to choose from.
        </p>
        <button class="btn btn-primary" onclick="handleAutoStartTopicDiscovery()">🔍 Find 5 Documentary Topics Automatically</button>
      </div>
    `;
    return;
  }

  if (!selectedProjectId) {
    selectedProjectId = projects[0].id;
  }

  const currentProj = projects.find(p => p.id === selectedProjectId) || projects[0];

  // Fetch topics from server for this project
  try {
    const res = await fetch(`/api/topics/project/${currentProj.id}`);
    const json = await res.json();
    if (json.status === "success") {
      projectTopics = json.topics;
    }
  } catch (e) {
    console.error("Failed to load project topics:", e);
  }

  const projOptions = projects.map(p => `
    <option value="${p.id}" ${p.id === currentProj.id ? 'selected' : ''}>${escapeHtml(p.title)} (${p.pillar})</option>
  `).join("");

  container.innerHTML = `
    <div class="section-panel">
      <div class="section-panel-header">
        <div>
          <h3>Topic Discovery Intelligence Engine</h3>
          <p style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">
            Targeting 100-point scored candidates across Business (30%), Geopolitics (25%), Tech (25%), and History (20%)
          </p>
        </div>
        <div style="display: flex; gap: 10px; align-items: center;">
          <select class="form-select" style="width: auto; min-width: 250px;" onchange="handleSelectProjectChange(this.value)">
            ${projOptions}
          </select>
          <button class="btn btn-primary" id="btn-discover-topics" onclick="triggerTopicDiscovery('${currentProj.id}')" ${isDiscovering ? 'disabled' : ''}>
            ${isDiscovering ? 'Analyzing Trends...' : '⚡ Discover 5 Scored Topics'}
          </button>
        </div>
      </div>

      <div style="font-size: 13px; margin-bottom: 20px; color: #94a3b8; background: rgba(0,0,0,0.2); padding: 12px; border-radius: 6px;">
        <strong>Current Production:</strong> ${escapeHtml(currentProj.title)} | 
        <strong>Pillar:</strong> ${currentProj.pillar} | 
        <strong>Stage:</strong> ${getStatusBadge(currentProj.status)}
      </div>

      <div id="topics-list-container">
        ${renderCandidateTopics(projectTopics, currentProj)}
      </div>

      ${rejectedTopics.length > 0 ? renderRejectedPanel(rejectedTopics) : ''}
    </div>
  `;
}

function handleSelectProjectChange(projId) {
  selectedProjectId = projId;
  renderTopicDiscovery(document.getElementById("main-content"));
}

async function safeParseResponse(res) {
  const txt = await res.text();
  if (!txt || !txt.trim()) {
    throw new Error(`Server returned empty response (HTTP ${res.status})`);
  }
  try {
    return JSON.parse(txt);
  } catch (e) {
    throw new Error(`Invalid server response (HTTP ${res.status})`);
  }
}

async function waitForBackgroundJob(jobId) {
  for (let i = 0; i < 120; i++) {
    await new Promise(r => setTimeout(r, 1500));
    const res = await fetch(`/api/jobs/${jobId}`);
    const json = await safeParseResponse(res);
    if (json.status === "success" && json.job) {
      if (json.job.status === "COMPLETED") {
        return json.job;
      }
      if (json.job.status === "FAILED") {
        throw new Error(json.job.error_message || "Background job failed");
      }
    }
  }
  throw new Error("Background job timed out");
}

async function triggerTopicDiscovery(projId) {
  isDiscovering = true;
  renderTopicDiscovery(document.getElementById("main-content"));
  try {
    const res = await fetch("/api/topics/discover", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ project_id: projId, async: true })
    });
    const json = await safeParseResponse(res);
    if (json.status === "queued" && json.job_id) {
      await waitForBackgroundJob(json.job_id);
      const listRes = await fetch(`/api/topics/project/${projId}`);
      const listJson = await safeParseResponse(listRes);
      projectTopics = listJson.topics || [];
      rejectedTopics = [];
      await refreshStudioData();
    } else if (json.status === "success") {
      projectTopics = json.result.candidates;
      rejectedTopics = json.result.rejected_log || [];
      await refreshStudioData();
    } else {
      alert("Topic discovery error: " + (json.message || "Unknown error"));
    }
  } catch (err) {
    alert("Network error: " + err.message);
  } finally {
    isDiscovering = false;
    renderTopicDiscovery(document.getElementById("main-content"));
  }
}

function renderCandidateTopics(list, project) {
  if (!list || list.length === 0) {
    return `
      <div style="text-align: center; padding: 40px; color: var(--text-muted);">
        <p style="font-size: 14px; margin-bottom: 12px;">No candidate topics generated yet for this project.</p>
        <p style="font-size: 12px; margin-bottom: 20px;">
          Click "⚡ Discover 5 Scored Topics" to execute multi-source trend analysis and 100-point validation.
        </p>
      </div>
    `;
  }

  return list.map((t, idx) => {
    const isSelected = project.selected_topic_id === t.id || t.status === 'SELECTED';
    const scoreColor = t.total_score >= 80 ? '#34d399' : (t.total_score >= 70 ? '#facc15' : '#f87171');
    const hooksHtml = (t.hooks || []).map(h => `
      <div class="hook-preview-box">
        <h5>Hook #${h.hook_number}: ${escapeHtml(h.strategy)}</h5>
        <p><strong>Narration:</strong> "${escapeHtml(h.narration_script)}"</p>
        <p style="color: var(--accent-blue); margin-top: 4px;"><strong>Visual:</strong> ${escapeHtml(h.visual_direction)}</p>
        <p style="color: #94a3b8; font-size: 11px; margin-top: 2px;"><strong>Sound:</strong> ${escapeHtml(h.sound_direction)}</p>
        <p style="color: var(--accent-gold); font-size: 11px; margin-top: 2px;"><strong>Curiosity Gap:</strong> ${escapeHtml(h.curiosity_gap)}</p>
      </div>
    `).join("");

    const titlesHtml = (t.title_variants || []).map(title => `
      <li style="margin-bottom: 4px; color: #cbd5e1;">${escapeHtml(title)}</li>
    `).join("");

    return `
      <div class="topic-card ${isSelected ? 'selected' : ''}">
        <div class="topic-card-header">
          <div>
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
              <span class="badge badge-topic-sel">${t.pillar}</span>
              ${isSelected ? '<span class="badge badge-completed">SELECTED FOR PRODUCTION</span>' : ''}
            </div>
            <div class="topic-title">#${idx + 1}. ${escapeHtml(t.title)}</div>
          </div>
          <div class="score-badge" style="border-color: ${scoreColor}; color: ${scoreColor}">
            <span class="score-val">${t.total_score}</span>
            <span class="score-lbl">/ 100 PTS</span>
          </div>
        </div>

        <div class="topic-angle"><strong>Angle:</strong> ${escapeHtml(t.angle)}</div>

        <div class="topic-meta-row">
          <div class="topic-meta-item">⚔️ <strong>Conflict:</strong> ${escapeHtml(t.central_conflict || 'N/A')}</div>
          <div class="topic-meta-item">🎯 <strong>Audience:</strong> ${escapeHtml(t.target_audience || 'Global English')}</div>
        </div>

        <!-- 100-Point Score Grid -->
        <div class="score-grid">
          <div class="score-grid-item">
            <span class="score-grid-name">Audience (20)</span>
            <span class="score-grid-val">${t.score_audience_interest}/20</span>
          </div>
          <div class="score-grid-item">
            <span class="score-grid-name">Storytelling (20)</span>
            <span class="score-grid-val">${t.score_storytelling}/20</span>
          </div>
          <div class="score-grid-item">
            <span class="score-grid-name">Originality (15)</span>
            <span class="score-grid-val">${t.score_originality}/15</span>
          </div>
          <div class="score-grid-item">
            <span class="score-grid-name">Visuals (15)</span>
            <span class="score-grid-val">${t.score_visual_availability}/15</span>
          </div>
          <div class="score-grid-item">
            <span class="score-grid-name">Research (15)</span>
            <span class="score-grid-val">${t.score_research_depth}/15</span>
          </div>
          <div class="score-grid-item">
            <span class="score-grid-name">Competition (10)</span>
            <span class="score-grid-val">${t.score_competition}/10</span>
          </div>
          <div class="score-grid-item">
            <span class="score-grid-name">Feasibility (5)</span>
            <span class="score-grid-val">${t.score_feasibility}/5</span>
          </div>
        </div>

        <div style="font-size: 12px; color: #94a3b8; margin-bottom: 14px;">
          <strong>Evidence Grounding:</strong> ${escapeHtml(t.scoring_explanation)}
        </div>

        <!-- Opening Hooks Accordion Preview -->
        <details style="margin-bottom: 14px; font-size: 13px;">
          <summary style="cursor: pointer; color: var(--accent-indigo); font-weight: 600;">
            View 3 Evidence-Backed Opening Hooks & Titles
          </summary>
          <div style="margin-top: 10px;">
            <div style="font-size: 12px; font-weight: 700; margin-bottom: 4px; color: #e2e8f0;">Curiosity Title Concepts:</div>
            <ul style="padding-left: 20px; font-size: 12px; margin-bottom: 12px;">
              ${titlesHtml}
            </ul>
            <div style="font-size: 12px; font-weight: 700; margin-bottom: 4px; color: #e2e8f0;">Three Opening Hook Concepts:</div>
            ${hooksHtml}
          </div>
        </details>

        <div style="display: flex; justify-content: flex-end; gap: 10px;">
          ${isSelected 
            ? `<button class="btn btn-secondary" disabled>✓ Active Production Topic</button>`
            : `<button class="btn btn-primary" onclick="handleSelectTopic('${project.id}', '${t.id}')">Select This Topic For Production →</button>`
          }
        </div>
      </div>
    `;
  }).join("");
}

function renderRejectedPanel(list) {
  const rows = list.map(r => `
    <li style="margin-bottom: 8px;">
      <strong style="color: #fda4af;">${escapeHtml(r.title)}</strong> (${r.pillar}) - Score: ${r.total_score}/100<br>
      <span style="color: var(--text-muted); font-size: 11px;">${r.reasons.join(" ")}</span>
    </li>
  `).join("");

  return `
    <div class="rejection-panel">
      <h4 style="color: #f43f5e; font-size: 14px; margin-bottom: 8px;">Mandatory Rejection Log (Evidence Filters)</h4>
      <p style="font-size: 12px; color: var(--text-muted); margin-bottom: 10px;">
        Topics failing factual verification, lacking authentic free archival visuals, or having ungrounded claims are automatically filtered out.
      </p>
      <ul style="font-size: 12px; padding-left: 18px;">
        ${rows}
      </ul>
    </div>
  `;
}

async function handleSelectTopic(projId, topicId) {
  try {
    const res = await fetch("/api/topics/select", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ project_id: projId, topic_id: topicId })
    });
    const json = await res.json();
    if (json.status === "success") {
      alert("Topic Selected! Project transitioned to Stage 2: Deep Research & Evidence Dossier.");
      await refreshStudioData();
      switchTab("research");
    } else {
      alert("Error selecting topic: " + json.message);
    }
  } catch (err) {
    alert("Network error: " + err.message);
  }
}

// --- Phase 3: Evidence Dossier & Fact Checking Logic ---

let currentDossier = null;
let isBuildingDossier = false;
let isFactChecking = false;

async function renderEvidenceDossier(container) {
  if (projects.length === 0) {
    container.innerHTML = `
      <div class="section-panel" style="text-align: center; padding: 40px;">
        <h3>No Project Selected</h3>
        <p style="color: var(--text-muted); font-size: 13px; margin: 12px 0 20px;">
          Create a project and select a topic candidate first.
        </p>
        <button class="btn btn-primary" onclick="openNewProjectModal()">+ Create Project</button>
      </div>
    `;
    return;
  }

  if (!selectedProjectId) {
    selectedProjectId = projects[0].id;
  }

  const currentProj = projects.find(p => p.id === selectedProjectId) || projects[0];

  // Fetch dossier for this project
  try {
    const res = await fetch(`/api/research/dossier/${currentProj.id}`);
    const json = await res.json();
    if (json.status === "success") {
      currentDossier = json.dossier;
    } else {
      currentDossier = null;
    }
  } catch (e) {
    currentDossier = null;
  }

  const projOptions = projects.map(p => `
    <option value="${p.id}" ${p.id === currentProj.id ? 'selected' : ''}>${escapeHtml(p.title)} (${p.pillar})</option>
  `).join("");

  container.innerHTML = `
    <div class="section-panel">
      <div class="section-panel-header">
        <div>
          <h3>Evidence Dossier & Claims Verification</h3>
          <p style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">
            Primary sources, verified claims, government records, and audit reports
          </p>
        </div>
        <div style="display: flex; gap: 10px; align-items: center;">
          <select class="form-select" style="width: auto; min-width: 250px;" onchange="handleSelectProjectDossier(this.value)">
            ${projOptions}
          </select>
          <button class="btn btn-primary" onclick="triggerBuildDossier('${currentProj.id}')" ${isBuildingDossier ? 'disabled' : ''}>
            ${isBuildingDossier ? 'Synthesizing...' : '⚡ Assemble Evidence Dossier'}
          </button>
        </div>
      </div>

      <div style="font-size: 13px; margin-bottom: 20px; color: #94a3b8; background: rgba(0,0,0,0.2); padding: 12px; border-radius: 6px;">
        <strong>Documentary:</strong> ${escapeHtml(currentProj.title)} | 
        <strong>Pillar:</strong> ${currentProj.pillar} | 
        <strong>Pipeline Stage:</strong> ${getStatusBadge(currentProj.status)}
      </div>

      <div id="dossier-body">
        ${renderDossierContent(currentDossier, currentProj)}
      </div>
    </div>
  `;
}

function handleSelectProjectDossier(projId) {
  selectedProjectId = projId;
  renderEvidenceDossier(document.getElementById("main-content"));
}

async function triggerBuildDossier(projId) {
  isBuildingDossier = true;
  renderEvidenceDossier(document.getElementById("main-content"));
  try {
    const res = await fetch("/api/research/build-dossier", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ project_id: projId, async: true })
    });
    const json = await safeParseResponse(res);
    if (json.status === "queued" && json.job_id) {
      await waitForBackgroundJob(json.job_id);
      const dRes = await fetch(`/api/research/dossier/${projId}`);
      const dJson = await safeParseResponse(dRes);
      currentDossier = dJson.dossier;
      await refreshStudioData();
    } else if (json.status === "success") {
      currentDossier = json.dossier;
      await refreshStudioData();
    } else {
      alert("Error assembling dossier: " + (json.message || "Unknown error"));
    }
  } catch (err) {
    alert("Network error: " + err.message);
  } finally {
    isBuildingDossier = false;
    renderEvidenceDossier(document.getElementById("main-content"));
  }
}

async function triggerFactCheck(projId) {
  isFactChecking = true;
  renderEvidenceDossier(document.getElementById("main-content"));
  try {
    const res = await fetch("/api/research/fact-check", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ project_id: projId })
    });
    const json = await res.json();
    if (json.status === "success") {
      alert(`Fact-Checking Complete: ${json.report.outcome}! (${json.report.metrics.verified_claims} verified claims, ${json.report.metrics.disputed_claims} disputed accounts framed). Project advanced to Script Studio.`);
      await refreshStudioData();
      switchTab("script");
    } else {
      alert("Fact-checking failed: " + json.message);
    }
  } catch (err) {
    alert("Network error: " + err.message);
  } finally {
    isFactChecking = false;
    renderEvidenceDossier(document.getElementById("main-content"));
  }
}

function renderDossierContent(d, project) {
  if (!d) {
    return `
      <div style="text-align: center; padding: 40px; color: var(--text-muted);">
        <p style="font-size: 14px; margin-bottom: 12px;">No evidence dossier generated yet for this project.</p>
        <p style="font-size: 12px; margin-bottom: 20px;">
          Click "⚡ Assemble Evidence Dossier" to extract primary sources, classify claims, and prepare fact-checking dossiers.
        </p>
      </div>
    `;
  }

  const claimRows = (d.claims || []).map(c => {
    let badgeClass = 'badge-claim-fact';
    if (c.classification === 'ESTIMATE') badgeClass = 'badge-claim-est';
    else if (c.classification === 'ALLEGATION') badgeClass = 'badge-claim-alleg';
    else if (c.classification === 'DISPUTED_CLAIM') badgeClass = 'badge-claim-disp';

    return `
      <tr>
        <td style="font-weight: 600; color: #94a3b8; font-size: 11px;">${c.claim_id}</td>
        <td>${escapeHtml(c.statement)}</td>
        <td><span class="badge ${badgeClass}">${c.classification}</span></td>
        <td style="color: var(--accent-blue);">${c.source_ref}</td>
        <td style="font-weight: 700; color: #34d399;">${(c.confidence * 100).toFixed(0)}%</td>
      </tr>
    `;
  }).join("");

  const sourcesList = (d.sources || []).map(s => `
    <div class="source-item">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
        <strong style="color: #fff;">[${s.source_id}] ${escapeHtml(s.title)}</strong>
        <span class="badge badge-topic-sel">${s.source_type}</span>
      </div>
      <div style="color: var(--text-muted); font-size: 11px;">
        Publisher: <strong>${escapeHtml(s.publisher)}</strong> | Date: ${s.publication_date} | Credibility: ${s.credibility}
      </div>
      <a href="${s.url}" target="_blank" style="color: var(--accent-blue); font-size: 11px; text-decoration: underline; margin-top: 4px; display: inline-block;">
        View Source Document ↗
      </a>
    </div>
  `).join("");

  const timelineRows = (d.timeline_events || []).map(t => `
    <div class="timeline-item">
      <div class="timeline-date">${escapeHtml(t.date)}</div>
      <div style="color: #cbd5e1;">${escapeHtml(t.event)}</div>
    </div>
  `).join("");

  const figuresList = (d.key_figures || []).map(f => `
    <div style="padding: 10px; background: var(--bg-card); border-radius: 6px; border: 1px solid var(--border-color);">
      <strong style="color: #fff; font-size: 13px;">${escapeHtml(f.name)}</strong>
      <div style="color: var(--accent-gold); font-size: 11px; margin: 2px 0;">${escapeHtml(f.role)}</div>
      <div style="color: var(--text-muted); font-size: 11px;">${escapeHtml(f.notes)}</div>
    </div>
  `).join("");

  return `
    <!-- Central Question Hero -->
    <div class="dossier-hero">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
        <h4>Central Investigative Question</h4>
        <div style="display: flex; gap: 8px;">
          <span class="badge badge-completed">Evidence Confidence: ${(d.confidence_score * 100).toFixed(0)}%</span>
          <span class="badge ${d.status === 'VERIFIED' ? 'badge-completed' : 'badge-review'}">Status: ${d.status}</span>
        </div>
      </div>
      <div class="question-text">"${escapeHtml(d.central_question)}"</div>
      <p style="font-size: 13px; color: #cbd5e1; line-height: 1.6;">${escapeHtml(d.background_summary)}</p>
    </div>

    <!-- Key Figures & Organizations -->
    <div style="margin-bottom: 24px;">
      <h4 style="font-size: 14px; font-weight: 700; margin-bottom: 12px;">Key Figures & Decision Makers</h4>
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px;">
        ${figuresList}
      </div>
    </div>

    <!-- Chronological Timeline -->
    <div style="margin-bottom: 24px;">
      <h4 style="font-size: 14px; font-weight: 700; margin-bottom: 12px;">Chronological Event Sequence</h4>
      <div style="background: var(--bg-card); border-radius: 8px; padding: 14px; border: 1px solid var(--border-color);">
        ${timelineRows}
      </div>
    </div>

    <!-- Verified & Classified Claims -->
    <div style="margin-bottom: 24px;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
        <h4 style="font-size: 14px; font-weight: 700;">Classified Claims Matrix (${(d.claims || []).length})</h4>
        <div style="font-size: 11px; color: var(--text-muted);">
          Every claim traceable to primary records or credible investigations
        </div>
      </div>
      <table class="claims-table">
        <thead>
          <tr>
            <th style="width: 100px;">Claim ID</th>
            <th>Factual Statement</th>
            <th style="width: 140px;">Classification</th>
            <th style="width: 90px;">Source</th>
            <th style="width: 80px;">Confidence</th>
          </tr>
        </thead>
        <tbody>
          ${claimRows}
        </tbody>
      </table>
    </div>

    <!-- Primary Sources -->
    <div style="margin-bottom: 24px;">
      <h4 style="font-size: 14px; font-weight: 700; margin-bottom: 12px;">Primary Sources & Public Records (${(d.sources || []).length})</h4>
      ${sourcesList}
    </div>

    <!-- Action Bar -->
    <div style="display: flex; justify-content: flex-end; gap: 12px; margin-top: 24px; padding-top: 16px; border-top: 1px solid var(--border-color);">
      <button class="btn btn-secondary" onclick="triggerFactCheck('${project.id}')" ${isFactChecking ? 'disabled' : ''}>
        ${isFactChecking ? 'Auditing...' : '🛡️ Run Agent 5 Fact-Check Audit'}
      </button>
      <button class="btn btn-primary" onclick="switchTab('script')">
        Proceed to Script Studio →
      </button>
    </div>
  `;
}

// --- Phase 4: Script Studio Logic ---

let currentScript = null;
let isGeneratingScript = false;
let isApprovingScript = false;

async function renderScriptStudio(container) {
  if (projects.length === 0) {
    container.innerHTML = `
      <div class="section-panel" style="text-align: center; padding: 40px;">
        <h3>No Project Selected</h3>
        <p style="color: var(--text-muted); font-size: 13px; margin: 12px 0 20px;">
          Create a project, choose a topic, and assemble research before scripting.
        </p>
        <button class="btn btn-primary" onclick="openNewProjectModal()">+ Create Project</button>
      </div>
    `;
    return;
  }

  if (!selectedProjectId) {
    selectedProjectId = projects[0].id;
  }

  const currentProj = projects.find(p => p.id === selectedProjectId) || projects[0];

  // Fetch script from server
  try {
    const res = await fetch(`/api/script/${currentProj.id}`);
    const json = await res.json();
    if (json.status === "success") {
      currentScript = json.script;
    } else {
      currentScript = null;
    }
  } catch (e) {
    currentScript = null;
  }

  const projOptions = projects.map(p => `
    <option value="${p.id}" ${p.id === currentProj.id ? 'selected' : ''}>${escapeHtml(p.title)} (${p.pillar})</option>
  `).join("");

  container.innerHTML = `
    <div class="section-panel">
      <div class="section-panel-header">
        <div>
          <h3>Script Studio — 10-Beat Narrative Engine</h3>
          <p style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">
            Professional documentary storytelling crafted by Agent 4 Master Storyteller
          </p>
        </div>
        <div style="display: flex; gap: 10px; align-items: center;">
          <select class="form-select" style="width: auto; min-width: 250px;" onchange="handleSelectProjectScript(this.value)">
            ${projOptions}
          </select>
          <button class="btn btn-primary" onclick="triggerGenerateScript('${currentProj.id}')" ${isGeneratingScript ? 'disabled' : ''}>
            ${isGeneratingScript ? 'Writing Script...' : '⚡ Generate 10-Beat Script'}
          </button>
        </div>
      </div>

      <div style="font-size: 13px; margin-bottom: 20px; color: #94a3b8; background: rgba(0,0,0,0.2); padding: 12px; border-radius: 6px;">
        <strong>Documentary:</strong> ${escapeHtml(currentProj.title)} | 
        <strong>Pillar:</strong> ${currentProj.pillar} | 
        <strong>Pipeline Stage:</strong> ${getStatusBadge(currentProj.status)}
      </div>

      <div id="script-content-body">
        ${renderScriptContent(currentScript, currentProj)}
      </div>
    </div>
  `;
}

function handleSelectProjectScript(projId) {
  selectedProjectId = projId;
  renderScriptStudio(document.getElementById("main-content"));
}

async function triggerGenerateScript(projId) {
  isGeneratingScript = true;
  renderScriptStudio(document.getElementById("main-content"));
  try {
    const res = await fetch("/api/script/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ project_id: projId, async: true })
    });
    const json = await safeParseResponse(res);
    if (json.status === "queued" && json.job_id) {
      await waitForBackgroundJob(json.job_id);
      const sRes = await fetch(`/api/script/${projId}`);
      const sJson = await safeParseResponse(sRes);
      currentScript = sJson.script;
      await refreshStudioData();
    } else if (json.status === "success") {
      currentScript = json.script;
      await refreshStudioData();
    } else {
      alert("Script generation error: " + (json.message || "Unknown error"));
    }
  } catch (err) {
    alert("Network error: " + err.message);
  } finally {
    isGeneratingScript = false;
    renderScriptStudio(document.getElementById("main-content"));
  }
}

async function handleSaveScene(projId, sceneNum) {
  const el = document.getElementById(`scene-narration-${sceneNum}`);
  if (!el) return;
  const newText = el.value.trim();

  try {
    const res = await fetch(`/api/script/${projId}/update-scene`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ scene_number: sceneNum, narration: newText })
    });
    const json = await res.json();
    if (json.status === "success") {
      currentScript = json.script;
      alert(`Scene #${sceneNum} narration saved successfully!`);
      renderScriptStudio(document.getElementById("main-content"));
    } else {
      alert("Error saving scene: " + json.message);
    }
  } catch (err) {
    alert("Network error: " + err.message);
  }
}

async function handleApproveScript(projId) {
  if (!confirm("Confirm Script Approval: This will lock narration and advance to Stage 5: Visual Director. Proceed?")) return;
  isApprovingScript = true;
  try {
    const res = await fetch(`/api/script/${projId}/approve`, {
      method: "POST",
      headers: { "Content-Type": "application/json" }
    });
    const json = await res.json();
    if (json.status === "success") {
      alert("Script Approved! Project transitioned to Stage 5: Visual Director & Manifest.");
      await refreshStudioData();
      switchTab("visual-director");
    } else {
      alert("Approval error: " + json.message);
    }
  } catch (err) {
    alert("Network error: " + err.message);
  } finally {
    isApprovingScript = false;
  }
}

function renderScriptContent(script, project) {
  if (!script) {
    return `
      <div style="text-align: center; padding: 40px; color: var(--text-muted);">
        <p style="font-size: 14px; margin-bottom: 12px;">No script drafted yet for this project.</p>
        <p style="font-size: 12px; margin-bottom: 20px;">
          Click "⚡ Generate 10-Beat Script" to synthesize evidence, structure pacing, and craft scene directions.
        </p>
      </div>
    `;
  }

  const durationMins = (script.estimated_duration_sec / 60).toFixed(1);
  const isApproved = script.approval_status === 'APPROVED';

  const scenesHtml = (script.scenes || []).map(sc => `
    <div class="scene-card">
      <div class="scene-card-header">
        <div class="scene-card-title">
          <span>🎬 ${escapeHtml(sc.scene_title)}</span>
          <span class="badge badge-topic-sel">${sc.narrative_beat}</span>
        </div>
        <div style="display: flex; align-items: center; gap: 10px;">
          <span class="badge badge-script">⏱️ ~${sc.approx_duration_sec}s</span>
          <span class="badge badge-research">📝 ${sc.word_count} words</span>
          <span class="badge badge-review">${escapeHtml(sc.emotional_intention)}</span>
        </div>
      </div>

      <textarea id="scene-narration-${sc.scene_number}" class="scene-narration-area">${escapeHtml(sc.narration)}</textarea>

      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
        <div style="font-size: 11px; color: var(--text-muted);">
          Evidence Grounding: ${(sc.evidence_refs || []).map(ref => `<span class="badge badge-claim-fact" style="margin-right: 4px;">${ref}</span>`).join("")}
        </div>
        <button class="btn btn-secondary" style="font-size: 11px; padding: 4px 10px;" onclick="handleSaveScene('${project.id}', ${sc.scene_number})">
          💾 Save Scene Edits
        </button>
      </div>

      <div class="scene-meta-grid">
        <div class="scene-meta-box">
          <strong style="color: var(--accent-blue);">Visual Direction</strong>
          <p style="color: #cbd5e1; font-size: 11px;">${escapeHtml(sc.visual_direction)}</p>
        </div>
        <div class="scene-meta-box">
          <strong style="color: var(--accent-gold);">Sound & Audio Cues</strong>
          <p style="color: #cbd5e1; font-size: 11px;">${escapeHtml(sc.sound_direction)}</p>
        </div>
        <div class="scene-meta-box">
          <strong style="color: #a855f7;">Transition Intention</strong>
          <p style="color: #cbd5e1; font-size: 11px;">${escapeHtml(sc.transition_intention)}</p>
        </div>
      </div>
    </div>
  `).join("");

  return `
    <!-- Script Metrics Bar -->
    <div class="script-metrics-bar">
      <div class="script-metric-item">
        <span class="script-metric-val">${script.word_count}</span>
        <span class="script-metric-lbl">Total Words</span>
      </div>
      <div class="script-metric-item">
        <span class="script-metric-val">~${durationMins} mins</span>
        <span class="script-metric-lbl">Estimated Duration</span>
      </div>
      <div class="script-metric-item">
        <span class="script-metric-val">${(script.scenes || []).length}</span>
        <span class="script-metric-lbl">Narrative Scenes</span>
      </div>
      <div class="script-metric-item">
        <span class="script-metric-val" style="color: #34d399;">PASSED</span>
        <span class="script-metric-lbl">Fact-Check Status</span>
      </div>
      <div class="script-metric-item" style="margin-left: auto;">
        <span class="badge ${isApproved ? 'badge-completed' : 'badge-review'}" style="font-size: 12px; padding: 6px 12px;">
          ${isApproved ? '✓ APPROVED BY OPERATOR' : 'PENDING HUMAN APPROVAL [GATE 1]'}
        </span>
      </div>
    </div>

    <!-- 10 Scenes List -->
    <div>
      ${scenesHtml}
    </div>

    <!-- Human Checkpoint 1 Approval Bar -->
    <div style="background: rgba(99, 102, 241, 0.1); border: 1px solid var(--accent-indigo); border-radius: 8px; padding: 18px; margin-top: 24px; display: flex; justify-content: space-between; align-items: center;">
      <div>
        <h4 style="color: #fff; font-size: 14px; margin-bottom: 4px;">Human Approval Checkpoint #1 — Script Review</h4>
        <p style="color: var(--text-muted); font-size: 12px;">
          Review and approve the complete documentary narration script before expensive footage discovery and visual planning begin.
        </p>
      </div>
      <div>
        ${isApproved 
          ? `<button class="btn btn-secondary" disabled>✓ Script Approved</button>`
          : `<button class="btn btn-primary" onclick="handleApproveScript('${project.id}')">
              ✓ Approve Script & Advance to Visual Director →
             </button>`
        }
      </div>
    </div>
  `;
}

// --- Phase 5: Visual Director & Manifest Logic ---

let currentManifest = [];
let isGeneratingManifest = false;

async function renderVisualDirector(container) {
  if (projects.length === 0) {
    container.innerHTML = `
      <div class="section-panel" style="text-align: center; padding: 40px;">
        <h3>No Project Selected</h3>
        <p style="color: var(--text-muted); font-size: 13px; margin: 12px 0 20px;">
          Select a project with an approved script to plan the visual manifest.
        </p>
        <button class="btn btn-primary" onclick="openNewProjectModal()">+ Create Project</button>
      </div>
    `;
    return;
  }

  if (!selectedProjectId) {
    selectedProjectId = projects[0].id;
  }

  const currentProj = projects.find(p => p.id === selectedProjectId) || projects[0];

  // Fetch manifest from server
  try {
    const res = await fetch(`/api/visuals/manifest/${currentProj.id}`);
    const json = await res.json();
    if (json.status === "success") {
      currentManifest = json.beats || [];
    } else {
      currentManifest = [];
    }
  } catch (e) {
    currentManifest = [];
  }

  const projOptions = projects.map(p => `
    <option value="${p.id}" ${p.id === currentProj.id ? 'selected' : ''}>${escapeHtml(p.title)} (${p.pillar})</option>
  `).join("");

  container.innerHTML = `
    <div class="section-panel">
      <div class="section-panel-header">
        <div>
          <h3>Documentary Creative Director & Visual Manifest</h3>
          <p style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">
            Sentence-level visual treatments, camera movements, and shot pacing
          </p>
        </div>
        <div style="display: flex; gap: 10px; align-items: center;">
          <select class="form-select" style="width: auto; min-width: 250px;" onchange="handleSelectProjectVisuals(this.value)">
            ${projOptions}
          </select>
          <button class="btn btn-primary" onclick="triggerGenerateManifest('${currentProj.id}')" ${isGeneratingManifest ? 'disabled' : ''}>
            ${isGeneratingManifest ? 'Generating Manifest...' : '⚡ Synthesize Visual Manifest'}
          </button>
        </div>
      </div>

      <div style="font-size: 13px; margin-bottom: 20px; color: #94a3b8; background: rgba(0,0,0,0.2); padding: 12px; border-radius: 6px;">
        <strong>Documentary:</strong> ${escapeHtml(currentProj.title)} | 
        <strong>Pillar:</strong> ${currentProj.pillar} | 
        <strong>Pipeline Stage:</strong> ${getStatusBadge(currentProj.status)}
      </div>

      <div id="visual-director-content">
        ${renderManifestContent(currentManifest, currentProj)}
      </div>
    </div>
  `;
}

function handleSelectProjectVisuals(projId) {
  selectedProjectId = projId;
  renderVisualDirector(document.getElementById("main-content"));
}

async function triggerGenerateManifest(projId) {
  isGeneratingManifest = true;
  renderVisualDirector(document.getElementById("main-content"));
  try {
    const res = await fetch("/api/visuals/generate-manifest", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ project_id: projId })
    });
    const json = await res.json();
    if (json.status === "success") {
      currentManifest = json.result.manifest || [];
      await refreshStudioData();
    } else {
      alert("Error generating visual manifest: " + json.message);
    }
  } catch (err) {
    alert("Network error: " + err.message);
  } finally {
    isGeneratingManifest = false;
    renderVisualDirector(document.getElementById("main-content"));
  }
}

async function handleAdvanceToFootage(projId) {
  try {
    const res = await fetch(`/api/visuals/${projId}/advance`, {
      method: "POST",
      headers: { "Content-Type": "application/json" }
    });
    const json = await res.json();
    if (json.status === "success") {
      alert("Visual Manifest Locked! Advancing to Stage 6: Real Footage Discovery.");
      await refreshStudioData();
      switchTab("footage");
    } else {
      alert("Error advancing: " + json.message);
    }
  } catch (err) {
    alert("Network error: " + err.message);
  }
}

function renderManifestContent(beats, project) {
  if (!beats || beats.length === 0) {
    return `
      <div style="text-align: center; padding: 40px; color: var(--text-muted);">
        <p style="font-size: 14px; margin-bottom: 12px;">No visual manifest generated yet for this project.</p>
        <p style="font-size: 12px; margin-bottom: 20px;">
          Click "⚡ Synthesize Visual Manifest" to segment the approved script into 4–8 second visual beats and assign cinematic treatments.
        </p>
      </div>
    `;
  }

  // Pacing and mode statistics
  const totalDuration = beats.reduce((acc, b) => acc + (b.target_duration_sec || 0), 0);
  const avgDuration = (totalDuration / beats.length).toFixed(1);
  const investigativeCount = beats.filter(b => b.visual_mode === 'INVESTIGATIVE').length;
  const cinematicCount = beats.filter(b => b.visual_mode === 'CINEMATIC').length;
  const explainerCount = beats.filter(b => b.visual_mode === 'EXPLAINER').length;

  const beatsListHtml = beats.map(b => {
    let modeClass = 'badge-mode-cinematic';
    if (b.visual_mode === 'INVESTIGATIVE') modeClass = 'badge-mode-investigative';
    else if (b.visual_mode === 'EXPLAINER') modeClass = 'badge-mode-explainer';

    const startMin = Math.floor(b.start_timestamp_sec / 60);
    const startSec = Math.floor(b.start_timestamp_sec % 60).toString().padStart(2, '0');
    const endTimestamp = b.start_timestamp_sec + b.target_duration_sec;
    const endMin = Math.floor(endTimestamp / 60);
    const endSec = Math.floor(endTimestamp % 60).toString().padStart(2, '0');

    return `
      <div class="manifest-beat-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
          <div style="display: flex; align-items: center; gap: 8px;">
            <strong style="color: var(--accent-gold); font-size: 12px;">Scene ${b.scene_number} • Beat ${b.beat_number}</strong>
            <span class="badge ${modeClass}">${b.visual_mode}</span>
            <span class="badge-asset-type">${b.target_asset_type}</span>
          </div>
          <div style="font-size: 11px; color: var(--text-muted); font-family: monospace;">
            ⏱️ ${startMin}:${startSec} – ${endMin}:${endSec} (${b.target_duration_sec}s)
          </div>
        </div>

        <p style="font-size: 13px; color: #f1f5f9; font-style: italic; margin-bottom: 10px;">
          "${escapeHtml(b.narration_segment)}"
        </p>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 10px; font-size: 11px; background: rgba(0,0,0,0.2); padding: 10px; border-radius: 6px;">
          <div>
            <strong style="color: var(--accent-blue); display: block; margin-bottom: 2px;">Visual Concept</strong>
            <span style="color: #cbd5e1;">${escapeHtml(b.visual_concept)}</span>
          </div>
          <div>
            <strong style="color: #a855f7; display: block; margin-bottom: 2px;">Camera Movement</strong>
            <span style="color: #cbd5e1;">${escapeHtml(b.motion_direction)}</span>
          </div>
          <div>
            <strong style="color: #34d399; display: block; margin-bottom: 2px;">Audio Cue & Transition</strong>
            <span style="color: #cbd5e1;">${escapeHtml(b.sound_cue)} | ${escapeHtml(b.transition_in)}</span>
          </div>
        </div>
      </div>
    `;
  }).join("");

  return `
    <!-- Visual Pacing Metrics -->
    <div class="script-metrics-bar">
      <div class="script-metric-item">
        <span class="script-metric-val">${beats.length}</span>
        <span class="script-metric-lbl">Total Visual Beats</span>
      </div>
      <div class="script-metric-item">
        <span class="script-metric-val">${avgDuration}s</span>
        <span class="script-metric-lbl">Avg Shot Duration</span>
      </div>
      <div class="script-metric-item">
        <span class="script-metric-val">~${(totalDuration / 60).toFixed(1)} mins</span>
        <span class="script-metric-lbl">Total Timeline</span>
      </div>
      <div class="script-metric-item">
        <span class="script-metric-val" style="color: #c084fc;">${investigativeCount}</span>
        <span class="script-metric-lbl">Investigative</span>
      </div>
      <div class="script-metric-item">
        <span class="script-metric-val" style="color: #fbbf24;">${cinematicCount}</span>
        <span class="script-metric-lbl">Cinematic</span>
      </div>
      <div class="script-metric-item">
        <span class="script-metric-val" style="color: #38bdf8;">${explainerCount}</span>
        <span class="script-metric-lbl">Explainer</span>
      </div>
    </div>

    <!-- Beats List -->
    <div>
      ${beatsListHtml}
    </div>

    <!-- Advance Action Bar -->
    <div style="display: flex; justify-content: flex-end; gap: 12px; margin-top: 24px; padding-top: 16px; border-top: 1px solid var(--border-color);">
      <button class="btn btn-primary" onclick="handleAdvanceToFootage('${project.id}')">
        Advance to Real Footage Discovery →
      </button>
    </div>
  `;
}

// --- Phase 6: Footage Discovery & Mandatory Visual Approval Logic ---

let projectAssets = [];
let isDiscoveringAssets = false;

async function renderAssetApprovalDashboard(container) {
  if (projects.length === 0) {
    container.innerHTML = `
      <div class="section-panel" style="text-align: center; padding: 40px;">
        <h3>No Project Selected</h3>
        <p style="color: var(--text-muted); font-size: 13px; margin: 12px 0 20px;">
          Create a project, approve script, and plan the visual manifest first.
        </p>
        <button class="btn btn-primary" onclick="openNewProjectModal()">+ Create Project</button>
      </div>
    `;
    return;
  }

  if (!selectedProjectId) {
    selectedProjectId = projects[0].id;
  }

  const currentProj = projects.find(p => p.id === selectedProjectId) || projects[0];

  // Fetch assets for project
  try {
    const res = await fetch(`/api/assets/project/${currentProj.id}`);
    const json = await res.json();
    if (json.status === "success") {
      projectAssets = json.assets || [];
    } else {
      projectAssets = [];
    }
  } catch (e) {
    projectAssets = [];
  }

  const projOptions = projects.map(p => `
    <option value="${p.id}" ${p.id === currentProj.id ? 'selected' : ''}>${escapeHtml(p.title)} (${p.pillar})</option>
  `).join("");

  container.innerHTML = `
    <div class="section-panel">
      <div class="section-panel-header">
        <div>
          <h3>Mandatory Visual Approval Dashboard [CHECKPOINT 2]</h3>
          <p style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">
            Free archive harvesting (NASA, US Archives, LOC, Wikimedia, Pexels) & human approval gate
          </p>
        </div>
        <div style="display: flex; gap: 10px; align-items: center;">
          <select class="form-select" style="width: auto; min-width: 250px;" onchange="handleSelectProjectAssets(this.value)">
            ${projOptions}
          </select>
          <button class="btn btn-secondary" onclick="handleBulkApproveAssets('${currentProj.id}')" ${projectAssets.length === 0 ? 'disabled' : ''}>
            ✓ Bulk Approve All
          </button>
          <button class="btn btn-primary" onclick="triggerDiscoverAssets('${currentProj.id}')" ${isDiscoveringAssets ? 'disabled' : ''}>
            ${isDiscoveringAssets ? 'Harvesting Free Archives...' : '⚡ Discover Free Assets'}
          </button>
        </div>
      </div>

      <div style="font-size: 13px; margin-bottom: 20px; color: #94a3b8; background: rgba(0,0,0,0.2); padding: 12px; border-radius: 6px;">
        <strong>Documentary:</strong> ${escapeHtml(currentProj.title)} | 
        <strong>Pillar:</strong> ${currentProj.pillar} | 
        <strong>Pipeline Stage:</strong> ${getStatusBadge(currentProj.status)}
      </div>

      <!-- Custom AI Media & Footage Uploader Zone -->
      <div style="background: rgba(30, 41, 59, 0.6); border: 2px dashed #3b82f6; border-radius: 8px; padding: 24px; margin-bottom: 24px; text-align: center;">
        <h4 style="color: #60a5fa; font-size: 16px; margin-bottom: 8px;">📤 Upload Custom AI Clips & Footage</h4>
        <p style="font-size: 13px; color: #94a3b8; margin-bottom: 16px;">
          Upload your generated videos or photos here (Runway, Kling, Midjourney, Pexels, etc.). They will be color-graded and locked into the timeline.
        </p>
        <div style="display: flex; justify-content: center; align-items: center; gap: 14px; flex-wrap: wrap;">
          <select id="upload-shot-slot" class="form-select" style="max-width: 340px; background: #0f172a; color: #f8fafc;">
            <option value="SHOT_05">Shot 05: Emergency Fuel Cutoff (0:15 - 0:20)</option>
            <option value="SHOT_08">Shot 08: Split-Flap Departure Board (0:26 - 0:31)</option>
            <option value="SHOT_16">Shot 16: Grounded Fleet at Dusk (0:59 - 1:02)</option>
            <option value="general_broll">General B-Roll / Archival Clip</option>
          </select>
          <input type="file" id="custom-clip-file" accept="video/*,image/*" style="display: none;" onchange="handleDirectFileUpload(this)">
          <button class="btn btn-primary" onclick="document.getElementById('custom-clip-file').click()">
            📁 Choose Video / Image File
          </button>
        </div>
        <div id="upload-status-msg" style="margin-top: 12px; font-size: 13px; display: none;"></div>
      </div>

      <div id="assets-dashboard-content">
        ${renderAssetsGrid(projectAssets, currentProj)}
      </div>
    </div>
  `;
}

function handleSelectProjectAssets(projId) {
  selectedProjectId = projId;
  renderAssetApprovalDashboard(document.getElementById("main-content"));
}

async function triggerDiscoverAssets(projId) {
  isDiscoveringAssets = true;
  renderAssetApprovalDashboard(document.getElementById("main-content"));
  try {
    const res = await fetch("/api/assets/discover", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ project_id: projId, async: true })
    });
    const json = await safeParseResponse(res);
    if (json.status === "queued" && json.job_id) {
      await waitForBackgroundJob(json.job_id);
      const listRes = await fetch(`/api/assets/project/${projId}`);
      const listJson = await safeParseResponse(listRes);
      alert(`Harvested ${(listJson.assets || []).length} free permitted assets! Mandatory approval required.`);
      await refreshStudioData();
    } else if (json.status === "success") {
      alert(`Harvested ${json.result.total_assets} free permitted assets! Mandatory approval required.`);
      await refreshStudioData();
    } else {
      alert("Error harvesting assets: " + json.message);
    }
  } catch (err) {
    alert("Network error: " + err.message);
  } finally {
    isDiscoveringAssets = false;
    renderAssetApprovalDashboard(document.getElementById("main-content"));
  }
}

async function handleDirectFileUpload(inputElement) {
  const file = inputElement.files[0];
  if (!file) return;

  const shotSlot = document.getElementById("upload-shot-slot").value;
  const statusMsg = document.getElementById("upload-status-msg");
  statusMsg.style.display = "block";
  statusMsg.style.color = "#38bdf8";
  statusMsg.innerText = `⏳ Uploading ${file.name} (${(file.size / (1024 * 1024)).toFixed(2)} MB)...`;

  const formData = new FormData();
  formData.append("file", file);
  formData.append("shot_slot", shotSlot);
  formData.append("project_id", selectedProjectId || "swiss-air-grounding-prod");

  try {
    const res = await fetch("/api/assets/upload", {
      method: "POST",
      body: formData
    });
    const json = await res.json();
    if (json.status === "success") {
      statusMsg.style.color = "#4ade80";
      statusMsg.innerText = `✓ Successfully uploaded: ${json.filename}! Slot updated.`;
      setTimeout(() => {
        renderAssetApprovalDashboard(document.getElementById("main-content"));
      }, 1500);
    } else {
      statusMsg.style.color = "#f87171";
      statusMsg.innerText = `❌ Error uploading: ${json.message}`;
    }
  } catch (err) {
    statusMsg.style.color = "#f87171";
    statusMsg.innerText = `❌ Upload failed: ${err.message}`;
  }
}

async function handleApproveAsset(assetId) {
  try {
    const res = await fetch(`/api/assets/${assetId}/approve`, { method: "POST" });
    const json = await res.json();
    if (json.status === "success") {
      renderAssetApprovalDashboard(document.getElementById("main-content"));
    }
  } catch (e) {
    alert("Error approving asset: " + e.message);
  }
}

async function handleRejectAsset(assetId) {
  const reason = prompt("Enter reason for rejecting this visual asset (e.g., 'Irrelevant subject', 'Poor quality'):");
  if (!reason) return;

  try {
    const res = await fetch(`/api/assets/${assetId}/reject`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ reason })
    });
    const json = await res.json();
    if (json.status === "success") {
      renderAssetApprovalDashboard(document.getElementById("main-content"));
    }
  } catch (e) {
    alert("Error rejecting asset: " + e.message);
  }
}

async function handleReplaceAsset(assetId) {
  try {
    const res = await fetch(`/api/assets/${assetId}/replace`, { method: "POST" });
    const json = await res.json();
    if (json.status === "success") {
      alert("Asset replaced with alternate free candidate!");
      renderAssetApprovalDashboard(document.getElementById("main-content"));
    }
  } catch (e) {
    alert("Error replacing asset: " + e.message);
  }
}

async function handleBulkApproveAssets(projId) {
  if (!confirm("Approve all currently pending visual assets?")) return;
  try {
    const res = await fetch("/api/assets/bulk-approve", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ project_id: projId })
    });
    const json = await res.json();
    if (json.status === "success") {
      renderAssetApprovalDashboard(document.getElementById("main-content"));
    }
  } catch (e) {
    alert("Error bulk approving: " + e.message);
  }
}

async function handleFinalizeApprovals(projId) {
  try {
    const res = await fetch(`/api/assets/${projId}/finalize`, { method: "POST" });
    const json = await res.json();
    if (json.status === "success") {
      alert("All assets approved! Checkpoint #2 passed. Advanced to Stage 7: Storyboard Engine.");
      await refreshStudioData();
      switchTab("storyboard");
    } else {
      alert(json.message);
    }
  } catch (e) {
    alert("Error finalizing: " + e.message);
  }
}

function renderAssetsGrid(assets, project) {
  if (!assets || assets.length === 0) {
    return `
      <div style="text-align: center; padding: 40px; color: var(--text-muted);">
        <p style="font-size: 14px; margin-bottom: 12px;">No visual assets gathered yet for this project.</p>
        <p style="font-size: 12px; margin-bottom: 20px;">
          Click "⚡ Discover Free Assets" to harvest public domain & CC-licensed footage from NASA, LOC, Wikimedia, and Pexels.
        </p>
      </div>
    `;
  }

  const approvedCount = assets.filter(a => a.approval_status === 'APPROVED').length;
  const pendingCount = assets.filter(a => a.approval_status === 'PENDING').length;
  const rejectedCount = assets.filter(a => a.approval_status === 'REJECTED').length;
  const pct = Math.round((approvedCount / assets.length) * 100);

  const cardsHtml = assets.map(a => {
    let cardClass = '';
    let statusBadge = '<span class="badge badge-topic-sel">PENDING REVIEW</span>';
    if (a.approval_status === 'APPROVED') {
      cardClass = 'approved';
      statusBadge = '<span class="badge badge-completed">✓ APPROVED</span>';
    } else if (a.approval_status === 'REJECTED') {
      cardClass = 'rejected';
      statusBadge = '<span class="badge badge-review">✕ REJECTED</span>';
    }

    return `
      <div class="asset-card ${cardClass}">
        <div class="asset-thumb-box">
          <img src="${a.preview_url}" class="asset-thumb-img" alt="${escapeHtml(a.title)}" loading="lazy">
          <span class="asset-duration-tag">⏱️ ${a.duration_sec}s</span>
        </div>
        <div class="asset-card-body">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <span class="badge-asset-type">${a.authenticity_class}</span>
            ${statusBadge}
          </div>
          <div class="asset-card-title">${escapeHtml(a.title)}</div>
          
          <div style="font-size: 11px; color: var(--text-muted); margin-bottom: 6px;">
            Source: <strong>${a.source_name}</strong> | License: <strong>${a.license_type}</strong>
          </div>

          <p style="font-size: 11px; color: #94a3b8; font-style: italic; margin-bottom: 10px; background: rgba(0,0,0,0.2); padding: 6px; border-radius: 4px;">
            "${escapeHtml(a.narration_segment || '')}"
          </p>

          ${a.rejection_reason ? `<div style="color: #f43f5e; font-size: 11px; margin-bottom: 6px;">Rejection: ${escapeHtml(a.rejection_reason)}</div>` : ''}

          <div class="asset-action-row">
            ${a.approval_status !== 'APPROVED' 
              ? `<button class="btn btn-primary" style="font-size: 11px; padding: 4px 8px; flex: 1;" onclick="handleApproveAsset('${a.id}')">✓ Approve</button>`
              : `<button class="btn btn-secondary" style="font-size: 11px; padding: 4px 8px; flex: 1;" disabled>Approved</button>`
            }
            <button class="btn btn-danger" style="font-size: 11px; padding: 4px 8px;" onclick="handleRejectAsset('${a.id}')">✕ Reject</button>
            <button class="btn btn-secondary" style="font-size: 11px; padding: 4px 8px;" onclick="handleReplaceAsset('${a.id}')">🔄 Replace</button>
          </div>
        </div>
      </div>
    `;
  }).join("");

  return `
    <!-- Approval Gate Status Banner -->
    <div class="script-metrics-bar">
      <div class="script-metric-item">
        <span class="script-metric-val">${assets.length}</span>
        <span class="script-metric-lbl">Harvested Assets</span>
      </div>
      <div class="script-metric-item">
        <span class="script-metric-val" style="color: #34d399;">${approvedCount}</span>
        <span class="script-metric-lbl">Approved</span>
      </div>
      <div class="script-metric-item">
        <span class="script-metric-val" style="color: #38bdf8;">${pendingCount}</span>
        <span class="script-metric-lbl">Pending Review</span>
      </div>
      <div class="script-metric-item">
        <span class="script-metric-val" style="color: #f43f5e;">${rejectedCount}</span>
        <span class="script-metric-lbl">Rejected</span>
      </div>
      <div class="script-metric-item" style="margin-left: auto;">
        <span class="badge ${pct === 100 ? 'badge-completed' : 'badge-review'}" style="font-size: 12px; padding: 6px 12px;">
          ${pct === 100 ? '✓ 100% GATE CLEARED' : `GATE PROGRESS: ${pct}%`}
        </span>
      </div>
    </div>

    <!-- Asset Cards Grid -->
    <div class="asset-grid">
      ${cardsHtml}
    </div>

    <!-- Hard Approval Checkpoint #2 Action Bar -->
    <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid var(--accent-emerald); border-radius: 8px; padding: 18px; margin-top: 24px; display: flex; justify-content: space-between; align-items: center;">
      <div>
        <h4 style="color: #fff; font-size: 14px; margin-bottom: 4px;">Human Approval Checkpoint #2 — Mandatory Visual Approval</h4>
        <p style="color: var(--text-muted); font-size: 12px;">
          Hard production gate: Every single visual asset must be approved by the human operator before editing and local FFmpeg rendering can begin.
        </p>
      </div>
      <div>
        <button class="btn btn-primary" onclick="handleFinalizeApprovals('${project.id}')">
          🛡️ Lock Asset Approvals & Proceed to Storyboard →
        </button>
      </div>
    </div>
  `;
}

// --- Phase 7: Storyboard Engine Logic ---

let projectStoryboard = [];
let isCompilingStoryboard = false;

async function renderStoryboardCanvas(container) {
  if (projects.length === 0) {
    container.innerHTML = `
      <div class="section-panel" style="text-align: center; padding: 40px;">
        <h3>No Project Selected</h3>
        <p style="color: var(--text-muted); font-size: 13px; margin: 12px 0 20px;">
          Select a project with approved assets to compile the scene storyboard.
        </p>
        <button class="btn btn-primary" onclick="openNewProjectModal()">+ Create Project</button>
      </div>
    `;
    return;
  }

  if (!selectedProjectId) {
    selectedProjectId = projects[0].id;
  }

  const currentProj = projects.find(p => p.id === selectedProjectId) || projects[0];

  // Fetch storyboard from server
  try {
    const res = await fetch(`/api/storyboard/${currentProj.id}`);
    const json = await res.json();
    if (json.status === "success") {
      projectStoryboard = json.storyboard || [];
    } else {
      projectStoryboard = [];
    }
  } catch (e) {
    projectStoryboard = [];
  }

  const projOptions = projects.map(p => `
    <option value="${p.id}" ${p.id === currentProj.id ? 'selected' : ''}>${escapeHtml(p.title)} (${p.pillar})</option>
  `).join("");

  container.innerHTML = `
    <div class="section-panel">
      <div class="section-panel-header">
        <div>
          <h3>Scene-by-Scene Storyboard Engine [CHECKPOINT 3]</h3>
          <p style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">
            Synchronized visual assets, camera motions, transitions, and sound cues in narration order
          </p>
        </div>
        <div style="display: flex; gap: 10px; align-items: center;">
          <select class="form-select" style="width: auto; min-width: 250px;" onchange="handleSelectProjectStoryboard(this.value)">
            ${projOptions}
          </select>
          <button class="btn btn-primary" onclick="triggerCompileStoryboard('${currentProj.id}')" ${isCompilingStoryboard ? 'disabled' : ''}>
            ${isCompilingStoryboard ? 'Sequencing...' : '⚡ Compile Storyboard Timeline'}
          </button>
        </div>
      </div>

      <div style="font-size: 13px; margin-bottom: 20px; color: #94a3b8; background: rgba(0,0,0,0.2); padding: 12px; border-radius: 6px;">
        <strong>Documentary:</strong> ${escapeHtml(currentProj.title)} | 
        <strong>Pillar:</strong> ${currentProj.pillar} | 
        <strong>Pipeline Stage:</strong> ${getStatusBadge(currentProj.status)}
      </div>

      <div id="storyboard-content-body">
        ${renderStoryboardTimeline(projectStoryboard, currentProj)}
      </div>
    </div>
  `;
}

function handleSelectProjectStoryboard(projId) {
  selectedProjectId = projId;
  renderStoryboardCanvas(document.getElementById("main-content"));
}

async function triggerCompileStoryboard(projId) {
  isCompilingStoryboard = true;
  renderStoryboardCanvas(document.getElementById("main-content"));
  try {
    const res = await fetch("/api/storyboard/compile", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ project_id: projId })
    });
    const json = await res.json();
    if (json.status === "success") {
      projectStoryboard = json.result.storyboard || [];
      await refreshStudioData();
    } else {
      alert("Error compiling storyboard: " + json.message);
    }
  } catch (err) {
    alert("Network error: " + err.message);
  } finally {
    isCompilingStoryboard = false;
    renderStoryboardCanvas(document.getElementById("main-content"));
  }
}

async function handleApproveStoryboard(projId) {
  if (!confirm("Confirm Storyboard Approval: This advances the documentary into automated audio synthesis and video rendering. Proceed?")) return;
  try {
    const res = await fetch(`/api/storyboard/${projId}/approve`, {
      method: "POST",
      headers: { "Content-Type": "application/json" }
    });
    const json = await res.json();
    if (json.status === "success") {
      alert("Storyboard Approved! Advanced to Stage 8: Narration & Sound Production.");
      await refreshStudioData();
      switchTab("audio");
    } else {
      alert("Approval error: " + json.message);
    }
  } catch (err) {
    alert("Network error: " + err.message);
  }
}

function renderStoryboardTimeline(items, project) {
  if (!items || items.length === 0) {
    return `
      <div style="text-align: center; padding: 40px; color: var(--text-muted);">
        <p style="font-size: 14px; margin-bottom: 12px;">No storyboard compiled yet for this project.</p>
        <p style="font-size: 12px; margin-bottom: 20px;">
          Click "⚡ Compile Storyboard Timeline" to synthesize approved visuals, narration, camera movements, and audio cues.
        </p>
      </div>
    `;
  }

  const totalSec = items.reduce((acc, it) => acc + (it.duration_sec || 0), 0);
  const totalMins = (totalSec / 60).toFixed(1);
  const isApproved = project.status !== 'STORYBOARD_REVIEW';

  const cellsHtml = items.map(it => {
    const startMin = Math.floor(it.start_timestamp_sec / 60);
    const startSec = Math.floor(it.start_timestamp_sec % 60).toString().padStart(2, '0');
    const endTimestamp = it.start_timestamp_sec + it.duration_sec;
    const endMin = Math.floor(endTimestamp / 60);
    const endSec = Math.floor(endTimestamp % 60).toString().padStart(2, '0');

    return `
      <div class="storyboard-cell">
        <div class="storyboard-cell-thumb">
          <img src="${it.preview_url || 'https://images.unsplash.com/photo-1542296332-2e4473faf563?auto=format&fit=crop&w=600&q=80'}" alt="${escapeHtml(it.visual_summary || '')}">
          <span class="storyboard-time-badge">${startMin}:${startSec} - ${endMin}:${endSec}</span>
        </div>
        <div class="storyboard-cell-body">
          <div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
              <div style="display: flex; align-items: center; gap: 8px;">
                <span class="badge badge-topic-sel">#${it.order_index} • Scene ${it.scene_number}.${it.beat_number}</span>
                <span class="badge-asset-type">${it.asset_type || 'VISUAL'}</span>
              </div>
              <span class="badge badge-script">⏱️ ${it.duration_sec}s</span>
            </div>

            <p style="font-size: 13px; color: #f1f5f9; font-style: italic; margin-bottom: 10px; line-height: 1.5;">
              "${escapeHtml(it.narration_text)}"
            </p>
          </div>

          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 8px; font-size: 11px; background: rgba(0,0,0,0.25); padding: 10px 12px; border-radius: 6px;">
            <div>
              <strong style="color: #f43f5e; display: block; margin-bottom: 2px;">1. Narrative Purpose</strong>
              <span style="color: #cbd5e1;">${escapeHtml(it.narrative_purpose || 'Advance central investigative arc')}</span>
            </div>
            <div>
              <strong style="color: #fb923c; display: block; margin-bottom: 2px;">2. Emotional Intention</strong>
              <span style="color: #cbd5e1;">${escapeHtml(it.emotional_intention || 'Sustained dramatic tension')}</span>
            </div>
            <div>
              <strong style="color: #38bdf8; display: block; margin-bottom: 2px;">3. Shot Composition</strong>
              <span style="color: #cbd5e1;">${escapeHtml(it.shot_composition || 'Balanced cinematic rule-of-thirds')}</span>
            </div>
            <div>
              <strong style="color: var(--accent-blue); display: block; margin-bottom: 2px;">4. Camera Movement</strong>
              <span style="color: #cbd5e1;">${escapeHtml(it.camera_movement)}</span>
            </div>
            <div>
              <strong style="color: #818cf8; display: block; margin-bottom: 2px;">5. Animation & Motion</strong>
              <span style="color: #cbd5e1;">${escapeHtml(it.animation_instructions || 'Smooth 60fps keyframe easing')}</span>
            </div>
            <div>
              <strong style="color: #a855f7; display: block; margin-bottom: 2px;">6. Transition In / Out</strong>
              <span style="color: #cbd5e1;">In: ${escapeHtml(it.transition_in || it.transition)} | Out: ${escapeHtml(it.transition_out || 'Motivated cut')}</span>
            </div>
            <div>
              <strong style="color: var(--accent-gold); display: block; margin-bottom: 2px;">7. Sound Effect & Mix</strong>
              <span style="color: #cbd5e1;">${escapeHtml(it.sfx_cue)}</span>
            </div>
            <div>
              <strong style="color: #34d399; display: block; margin-bottom: 2px;">8. Music Progression</strong>
              <span style="color: #cbd5e1;">${escapeHtml(it.bgm_mood)}</span>
            </div>
            <div style="grid-column: 1 / -1; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 6px; margin-top: 2px;">
              <strong style="color: #94a3b8; display: inline; margin-right: 6px;">9. Continuity & Color Standard:</strong>
              <span style="color: #cbd5e1;">${escapeHtml(it.continuity_requirements || 'Maintain consistent lighting temperature and eye-trace alignment.')}</span>
            </div>
          </div>
        </div>
      </div>
    `;
  }).join("");

  return `
    <!-- Storyboard Metrics -->
    <div class="script-metrics-bar">
      <div class="script-metric-item">
        <span class="script-metric-val">${items.length}</span>
        <span class="script-metric-lbl">Storyboard Cells</span>
      </div>
      <div class="script-metric-item">
        <span class="script-metric-val">~${totalMins} mins</span>
        <span class="script-metric-lbl">Total Runtime</span>
      </div>
      <div class="script-metric-item">
        <span class="script-metric-val" style="color: #34d399;">100%</span>
        <span class="script-metric-lbl">Asset Alignment</span>
      </div>
      <div class="script-metric-item" style="margin-left: auto;">
        <span class="badge ${isApproved ? 'badge-completed' : 'badge-review'}" style="font-size: 12px; padding: 6px 12px;">
          ${isApproved ? '✓ STORYBOARD APPROVED' : 'PENDING OPERATOR APPROVAL [GATE 3]'}
        </span>
      </div>
    </div>

    <!-- Timeline Cells -->
    <div class="storyboard-timeline">
      ${cellsHtml}
    </div>

    <!-- Checkpoint #3 Action Bar -->
    <div style="background: rgba(99, 102, 241, 0.1); border: 1px solid var(--accent-indigo); border-radius: 8px; padding: 18px; margin-top: 24px; display: flex; justify-content: space-between; align-items: center;">
      <div>
        <h4 style="color: #fff; font-size: 14px; margin-bottom: 4px;">Human Approval Checkpoint #3 — Storyboard Review</h4>
        <p style="color: var(--text-muted); font-size: 12px;">
          Final creative checkpoint: Inspect the synchronized visual rhythm, transitions, and audio cues before rendering.
        </p>
      </div>
      <div>
        ${isApproved 
          ? `<button class="btn btn-secondary" disabled>✓ Storyboard Approved</button>`
          : `<button class="btn btn-primary" onclick="handleApproveStoryboard('${project.id}')">
              ✓ Approve Storyboard & Begin Production →
             </button>`
        }
      </div>
    </div>
  `;
}

// --- Phase 8: Narration & Sound Design Logic ---

let audioStoryboardItems = [];
let isSynthesizingAudio = false;

async function renderAudioDeck(container) {
  if (projects.length === 0) {
    container.innerHTML = `
      <div class="section-panel" style="text-align: center; padding: 40px;">
        <h3>No Project Selected</h3>
        <p style="color: var(--text-muted); font-size: 13px; margin: 12px 0 20px;">
          Approve storyboard sequence before synthesizing narration and background audio.
        </p>
        <button class="btn btn-primary" onclick="openNewProjectModal()">+ Create Project</button>
      </div>
    `;
    return;
  }

  if (!selectedProjectId) {
    selectedProjectId = projects[0].id;
  }

  const currentProj = projects.find(p => p.id === selectedProjectId) || projects[0];

  try {
    const res = await fetch(`/api/storyboard/${currentProj.id}`);
    const json = await res.json();
    if (json.status === "success") {
      audioStoryboardItems = json.storyboard || [];
    } else {
      audioStoryboardItems = [];
    }
  } catch (e) {
    audioStoryboardItems = [];
  }

  const projOptions = projects.map(p => `
    <option value="${p.id}" ${p.id === currentProj.id ? 'selected' : ''}>${escapeHtml(p.title)} (${p.pillar})</option>
  `).join("");

  container.innerHTML = `
    <div class="section-panel">
      <div class="section-panel-header">
        <div>
          <h3>Narration & Sound Design Studio</h3>
          <p style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">
            Segmented speech synthesis, mood-based atmospheric audio, ducking, and EBU R128 loudness normalization
          </p>
        </div>
        <div style="display: flex; gap: 10px; align-items: center;">
          <select class="form-select" style="width: auto; min-width: 250px;" onchange="handleSelectProjectAudio(this.value)">
            ${projOptions}
          </select>
          <select id="voice-select" class="form-select" style="width: auto;">
            <option value="kal" selected>Voice: Authoritative Investigative (kal)</option>
            <option value="rms">Voice: Crisp Analytical (rms)</option>
            <option value="slt">Voice: Warm Storytelling (slt)</option>
            <option value="awb">Voice: Clear Expository (awb)</option>
          </select>
          <button class="btn btn-primary" onclick="triggerSynthesizeAllAudio('${currentProj.id}')" ${isSynthesizingAudio ? 'disabled' : ''}>
            ${isSynthesizingAudio ? 'Synthesizing Narration...' : '⚡ Synthesize All Audio'}
          </button>
        </div>
      </div>

      <div style="font-size: 13px; margin-bottom: 20px; color: #94a3b8; background: rgba(0,0,0,0.2); padding: 12px; border-radius: 6px;">
        <strong>Documentary:</strong> ${escapeHtml(currentProj.title)} | 
        <strong>Pillar:</strong> ${currentProj.pillar} | 
        <strong>Pipeline Stage:</strong> ${getStatusBadge(currentProj.status)}
      </div>

      <div id="audio-deck-content">
        ${renderAudioTracksList(audioStoryboardItems, currentProj)}
      </div>
    </div>
  `;
}

function handleSelectProjectAudio(projId) {
  selectedProjectId = projId;
  renderAudioDeck(document.getElementById("main-content"));
}

async function triggerSynthesizeAllAudio(projId) {
  const voice = document.getElementById("voice-select").value;
  isSynthesizingAudio = true;
  renderAudioDeck(document.getElementById("main-content"));
  try {
    const res = await fetch("/api/audio/synthesize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ project_id: projId, voice: voice, async: true })
    });
    const json = await safeParseResponse(res);
    if (json.status === "queued" && json.job_id) {
      await waitForBackgroundJob(json.job_id);
      alert("Synthesized all narration and background audio tracks!");
      await refreshStudioData();
    } else if (json.status === "success") {
      alert(`Synthesized ${json.result.total_beats} narration tracks (${json.result.total_audio_duration_sec}s total audio)!`);
      await refreshStudioData();
    } else {
      alert("Audio synthesis error: " + json.message);
    }
  } catch (err) {
    alert("Network error: " + err.message);
  } finally {
    isSynthesizingAudio = false;
    renderAudioDeck(document.getElementById("main-content"));
  }
}

async function handleRegenBeatAudio(projId, orderIndex) {
  const voice = document.getElementById("voice-select") ? document.getElementById("voice-select").value : "kal";
  try {
    const res = await fetch("/api/audio/synthesize-beat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ project_id: projId, order_index: orderIndex, voice: voice })
    });
    const json = await res.json();
    if (json.status === "success") {
      alert(`Beat #${orderIndex} audio regenerated successfully!`);
      renderAudioDeck(document.getElementById("main-content"));
    } else {
      alert("Error regenerating beat: " + json.message);
    }
  } catch (err) {
    alert("Network error: " + err.message);
  }
}

async function handleAdvanceToAnimation(projId) {
  try {
    const res = await fetch(`/api/audio/${projId}/advance`, {
      method: "POST",
      headers: { "Content-Type": "application/json" }
    });
    const json = await res.json();
    if (json.status === "success") {
      alert("Narration & audio tracks locked! Advancing to Stage 9: Animation Studio.");
      await refreshStudioData();
      switchTab("animation");
    } else {
      alert("Error advancing: " + json.message);
    }
  } catch (err) {
    alert("Network error: " + err.message);
  }
}

function renderAudioTracksList(items, project) {
  if (!items || items.length === 0) {
    return `
      <div style="text-align: center; padding: 40px; color: var(--text-muted);">
        <p style="font-size: 14px; margin-bottom: 12px;">No storyboard items available for audio synthesis.</p>
        <p style="font-size: 12px; margin-bottom: 20px;">
          Approve the storyboard sequence in Stage 7 before generating audio tracks.
        </p>
      </div>
    `;
  }

  const tracksHtml = items.map(it => {
    const audioUrl = `/media/audio/${project.id}/beat_${it.order_index}.wav`;

    return `
      <div class="audio-card">
        <div style="min-width: 140px;">
          <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 4px;">
            <strong style="color: var(--accent-gold); font-size: 12px;">Beat #${it.order_index}</strong>
            <span class="badge badge-topic-sel">Scene ${it.scene_number}.${it.beat_number}</span>
          </div>
          <div style="font-size: 11px; color: var(--text-muted); font-family: monospace;">
            ⏱️ ${it.duration_sec}s
          </div>
        </div>

        <div style="flex: 1;">
          <p style="font-size: 12px; color: #f1f5f9; font-style: italic; line-height: 1.4; margin-bottom: 6px;">
            "${escapeHtml(it.narration_text)}"
          </p>
          <div style="font-size: 10px; color: var(--text-muted);">
            BGM Bed: <strong style="color: #34d399;">${escapeHtml(it.bgm_mood)}</strong> (-16dB ducked)
          </div>
        </div>

        <audio controls class="audio-player-custom" preload="none">
          <source src="${audioUrl}" type="audio/wav">
        </audio>

        <button class="btn btn-secondary" style="font-size: 11px; padding: 6px 10px;" onclick="handleRegenBeatAudio('${project.id}', ${it.order_index})">
          🔄 Regen Beat
        </button>
      </div>
    `;
  }).join("");

  return `
    <!-- Audio Standards Status Deck -->
    <div class="script-metrics-bar">
      <div class="script-metric-item">
        <span class="script-metric-val">${items.length}</span>
        <span class="script-metric-lbl">Speech Segments</span>
      </div>
      <div class="script-metric-item">
        <span class="script-metric-val" style="color: #34d399;">-14 LUFS</span>
        <span class="script-metric-lbl">EBU R128 Loudness</span>
      </div>
      <div class="script-metric-item">
        <span class="script-metric-val" style="color: #38bdf8;">-16 dB</span>
        <span class="script-metric-lbl">Auto BGM Ducking</span>
      </div>
      <div class="script-metric-item">
        <span class="script-metric-val" style="color: #facc15;">$0.00</span>
        <span class="script-metric-lbl">Audio License Fees</span>
      </div>
    </div>

    <!-- Audio Tracks -->
    <div>
      ${tracksHtml}
    </div>

    <!-- Advance Action Bar -->
    <div style="display: flex; justify-content: flex-end; gap: 12px; margin-top: 24px; padding-top: 16px; border-top: 1px solid var(--border-color);">
      <button class="btn btn-primary" onclick="handleAdvanceToAnimation('${project.id}')">
        Advance to Animation Studio →
      </button>
    </div>
  `;
}

// --- Phase 9: Animation Studio Logic ---

let projectAnimClips = [];
let isRenderingAnimations = false;

async function renderAnimationStudio(container) {
  if (projects.length === 0) {
    container.innerHTML = `
      <div class="section-panel" style="text-align: center; padding: 40px;">
        <h3>No Project Selected</h3>
        <p style="color: var(--text-muted); font-size: 13px; margin: 12px 0 20px;">
          Complete audio synthesis before generating motion graphics and animated clips.
        </p>
        <button class="btn btn-primary" onclick="openNewProjectModal()">+ Create Project</button>
      </div>
    `;
    return;
  }

  if (!selectedProjectId) {
    selectedProjectId = projects[0].id;
  }

  const currentProj = projects.find(p => p.id === selectedProjectId) || projects[0];

  try {
    const res = await fetch(`/api/animation/project/${currentProj.id}`);
    const json = await res.json();
    if (json.status === "success") {
      projectAnimClips = json.clips || [];
    } else {
      projectAnimClips = [];
    }
  } catch (e) {
    projectAnimClips = [];
  }

  const projOptions = projects.map(p => `
    <option value="${p.id}" ${p.id === currentProj.id ? 'selected' : ''}>${escapeHtml(p.title)} (${p.pillar})</option>
  `).join("");

  container.innerHTML = `
    <div class="section-panel">
      <div class="section-panel-header">
        <div>
          <h3>Cinematic Animation & Motion Graphics Studio</h3>
          <p style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">
            1080p animated maps, financial data curves, document highlighter reveals, and 2.5D Ken Burns motions
          </p>
        </div>
        <div style="display: flex; gap: 10px; align-items: center;">
          <select class="form-select" style="width: auto; min-width: 250px;" onchange="handleSelectProjectAnim(this.value)">
            ${projOptions}
          </select>
          <button class="btn btn-primary" onclick="triggerRenderAllAnimations('${currentProj.id}')" ${isRenderingAnimations ? 'disabled' : ''}>
            ${isRenderingAnimations ? 'Rendering 1080p Clips...' : '⚡ Synthesize 1080p Animations'}
          </button>
        </div>
      </div>

      <div style="font-size: 13px; margin-bottom: 20px; color: #94a3b8; background: rgba(0,0,0,0.2); padding: 12px; border-radius: 6px;">
        <strong>Documentary:</strong> ${escapeHtml(currentProj.title)} | 
        <strong>Pillar:</strong> ${currentProj.pillar} | 
        <strong>Pipeline Stage:</strong> ${getStatusBadge(currentProj.status)}
      </div>

      <div id="animation-deck-content">
        ${renderAnimationGrid(projectAnimClips, currentProj)}
      </div>
    </div>
  `;
}

function handleSelectProjectAnim(projId) {
  selectedProjectId = projId;
  renderAnimationStudio(document.getElementById("main-content"));
}

async function triggerRenderAllAnimations(projId) {
  isRenderingAnimations = true;
  renderAnimationStudio(document.getElementById("main-content"));
  try {
    const res = await fetch("/api/animation/render-all", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ project_id: projId, async: true })
    });
    const json = await safeParseResponse(res);
    if (json.status === "queued" && json.job_id) {
      await waitForBackgroundJob(json.job_id);
      alert("Rendered all 1080p motion graphics and animated video clips!");
      await refreshStudioData();
    } else if (json.status === "success") {
      alert(`Rendered ${json.result.total_rendered} motion graphics and animated video clips!`);
      await refreshStudioData();
    } else {
      alert("Animation rendering error: " + json.message);
    }
  } catch (err) {
    alert("Network error: " + err.message);
  } finally {
    isRenderingAnimations = false;
    renderAnimationStudio(document.getElementById("main-content"));
  }
}

async function handleAdvanceToEditing(projId) {
  try {
    const res = await fetch(`/api/animation/${projId}/advance`, {
      method: "POST",
      headers: { "Content-Type": "application/json" }
    });
    const json = await res.json();
    if (json.status === "success") {
      alert("Animations locked! Advanced to Stage 10: Video Editing & FFmpeg Rendering.");
      await refreshStudioData();
      switchTab("rendering");
    } else {
      alert("Error advancing: " + json.message);
    }
  } catch (err) {
    alert("Network error: " + err.message);
  }
}

function renderAnimationGrid(clips, project) {
  if (!clips || clips.length === 0) {
    return `
      <div style="text-align: center; padding: 40px; color: var(--text-muted);">
        <p style="font-size: 14px; margin-bottom: 12px;">No motion graphic clips rendered yet for this project.</p>
        <p style="font-size: 12px; margin-bottom: 20px;">
          Click "⚡ Synthesize 1080p Animations" to render animated cartographic maps, debt curves, and document reveals.
        </p>
      </div>
    `;
  }

  const cardsHtml = clips.map(c => `
    <div class="anim-card">
      <div class="anim-video-box">
        <video controls preload="metadata">
          <source src="${c.web_url}" type="video/mp4">
        </video>
      </div>
      <div style="padding: 12px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
          <strong style="color: #fff; font-size: 12px;">${c.filename}</strong>
          <span class="badge badge-completed">1080p 30fps</span>
        </div>
        <div style="font-size: 11px; color: var(--text-muted);">
          Format: H.264 MP4 | Local GPU / CPU Render ($0.00)
        </div>
      </div>
    </div>
  `).join("");

  return `
    <!-- Metrics Deck -->
    <div class="script-metrics-bar">
      <div class="script-metric-item">
        <span class="script-metric-val">${clips.length}</span>
        <span class="script-metric-lbl">Rendered 1080p Clips</span>
      </div>
      <div class="script-metric-item">
        <span class="script-metric-val" style="color: #38bdf8;">1920x1080</span>
        <span class="script-metric-lbl">Resolution</span>
      </div>
      <div class="script-metric-item">
        <span class="script-metric-val" style="color: #34d399;">H.264 / 30 FPS</span>
        <span class="script-metric-lbl">Broadcast Codec</span>
      </div>
      <div class="script-metric-item">
        <span class="script-metric-val" style="color: #facc15;">$0.00</span>
        <span class="script-metric-lbl">Software Fees</span>
      </div>
    </div>

    <!-- Clips Grid -->
    <div class="asset-grid">
      ${cardsHtml}
    </div>

    <!-- Advance Action Bar -->
    <div style="display: flex; justify-content: flex-end; gap: 12px; margin-top: 24px; padding-top: 16px; border-top: 1px solid var(--border-color);">
      <button class="btn btn-primary" onclick="handleAdvanceToEditing('${project.id}')">
        Advance to Video Rendering Pipeline →
      </button>
    </div>
  `;
}

// --- Phase 10: Video Rendering Pipeline Logic ---

let projectExportData = null;
let projectEditingPasses = [];
let isRunningEditingPasses = false;
let activeRenderJobId = null;
let renderPollInterval = null;

async function renderVideoRenderingConsole(container) {
  if (projects.length === 0) {
    container.innerHTML = `
      <div class="section-panel" style="text-align: center; padding: 40px;">
        <h3>No Project Selected</h3>
        <p style="color: var(--text-muted); font-size: 13px; margin: 12px 0 20px;">
          Select an active documentary project to render.
        </p>
        <button class="btn btn-primary" onclick="openNewProjectModal()">+ Create Project</button>
      </div>
    `;
    return;
  }

  if (!selectedProjectId) {
    selectedProjectId = projects[0].id;
  }

  const currentProj = projects.find(p => p.id === selectedProjectId) || projects[0];

  // Fetch export status and 6-pass editing review status
  try {
    const [resExp, resPasses] = await Promise.all([
      fetch(`/api/render/project/${currentProj.id}`),
      fetch(`/api/editing/passes/${currentProj.id}`)
    ]);
    const jsonExp = await resExp.json();
    const jsonPasses = await resPasses.json();
    if (jsonExp.status === "success") {
      projectExportData = jsonExp;
    }
    if (jsonPasses.status === "success") {
      projectEditingPasses = jsonPasses.passes || [];
    } else {
      projectEditingPasses = [];
    }
  } catch (e) {
    projectExportData = null;
    projectEditingPasses = [];
  }

  const projOptions = projects.map(p => `
    <option value="${p.id}" ${p.id === currentProj.id ? 'selected' : ''}>${escapeHtml(p.title)} (${p.pillar})</option>
  `).join("");

  container.innerHTML = `
    <div class="section-panel">
      <div class="section-panel-header">
        <div>
          <h3>6-Pass Professional Creative Editorial Suite & FFmpeg Rendering</h3>
          <p style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">
            Deliberate multi-pass human-level creative editing (Narrative, Visual, Motion, Sound, Polish, Final QC) & 1080p compositing
          </p>
        </div>
        <div style="display: flex; gap: 10px; align-items: center;">
          <select class="form-select" style="width: auto; min-width: 220px;" onchange="handleSelectProjectRender(this.value)">
            ${projOptions}
          </select>
          <button class="btn btn-secondary" onclick="triggerRunEditingPasses('${currentProj.id}')" ${isRunningEditingPasses ? 'disabled' : ''}>
            ${isRunningEditingPasses ? 'Executing 6 Passes...' : '🎨 Run 6-Pass Creative Review'}
          </button>
          <button class="btn btn-primary" id="btn-render-start" onclick="triggerStartRender('${currentProj.id}')" ${activeRenderJobId ? 'disabled' : ''}>
            ${activeRenderJobId ? 'Rendering in Progress...' : '🎬 Start 1080p Documentary Render'}
          </button>
        </div>
      </div>

      <div style="font-size: 13px; margin-bottom: 20px; color: #94a3b8; background: rgba(0,0,0,0.2); padding: 12px; border-radius: 6px;">
        <strong>Documentary:</strong> ${escapeHtml(currentProj.title)} | 
        <strong>Pillar:</strong> ${currentProj.pillar} | 
        <strong>Pipeline Stage:</strong> ${getStatusBadge(currentProj.status)}
      </div>

      <!-- Render Specs Deck -->
      <div class="script-metrics-bar">
        <div class="script-metric-item">
          <span class="script-metric-val" style="color: #38bdf8;">1080p</span>
          <span class="script-metric-lbl">Resolution (1920x1080)</span>
        </div>
        <div class="script-metric-item">
          <span class="script-metric-val">${projectEditingPasses.length}/6</span>
          <span class="script-metric-lbl">Creative Editing Passes</span>
        </div>
        <div class="script-metric-item">
          <span class="script-metric-val" style="color: #34d399;">Multi-Track</span>
          <span class="script-metric-lbl">Audio Ducking Mixed</span>
        </div>
        <div class="script-metric-item">
          <span class="script-metric-val" style="color: #facc15;">$0.00</span>
          <span class="script-metric-lbl">Local FFmpeg Worker</span>
        </div>
      </div>

      <!-- 6-Pass Creative Editorial Review Console -->
      <div id="editing-passes-area" style="margin-top: 20px;">
        ${renderEditingPassesDeck(projectEditingPasses)}
      </div>

      <div id="render-live-status-area">
        ${renderLiveStatusCard()}
      </div>

      <div id="render-theater-area">
        ${renderTheaterContent(projectExportData, currentProj)}
      </div>
    </div>
  `;
}

async function triggerRunEditingPasses(projId) {
  isRunningEditingPasses = true;
  renderVideoRenderingConsole(document.getElementById("main-content"));
  try {
    const res = await fetch("/api/editing/run-passes", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ project_id: projId })
    });
    const json = await res.json();
    if (json.status === "success") {
      alert(
        `Completed all 6 Professional Creative Editing Passes!\n` +
        `Overall Editorial Score: ${json.result.overall_editorial_score}%\n` +
        `Refinements Applied: ${json.result.total_refinements_applied}`
      );
      await refreshStudioData();
    } else {
      alert("Error executing creative passes: " + json.message);
    }
  } catch (err) {
    alert("Network error: " + err.message);
  } finally {
    isRunningEditingPasses = false;
    renderVideoRenderingConsole(document.getElementById("main-content"));
  }
}

function renderEditingPassesDeck(passes) {
  if (!passes || passes.length === 0) {
    return `
      <div style="background: rgba(99, 102, 241, 0.08); border: 1px solid rgba(99, 102, 241, 0.3); border-radius: 8px; padding: 18px; margin-bottom: 20px;">
        <h4 style="font-size: 14px; font-weight: 700; color: #fff; margin-bottom: 6px;">
          Non-Negotiable 6-Pass Professional Creative Editorial Standard
        </h4>
        <p style="font-size: 12px; color: #cbd5e1; line-height: 1.5;">
          DocuForge enforces 6 separate creative review passes before rendering: 
          <strong>Pass 1 (Narrative)</strong>, <strong>Pass 2 (Visual & Framing)</strong>, 
          <strong>Pass 3 (Motion Graphics)</strong>, <strong>Pass 4 (Sound Design)</strong>, 
          <strong>Pass 5 (Cinematic Polish)</strong>, and <strong>Pass 6 (Director's Cut QC)</strong>.
          Click <em>"🎨 Run 6-Pass Creative Review"</em> above (or start rendering to execute automatically).
        </p>
      </div>
    `;
  }

  const cards = passes.map(p => {
    const weaknesses = (p.weaknesses_identified || []).slice(0, 3).map(w => `<li>${escapeHtml(w)}</li>`).join("");
    const refinements = (p.refinements_applied || []).slice(0, 3).map(r => `<li>${escapeHtml(r)}</li>`).join("");
    return `
      <div class="qc-check-card">
        <div class="qc-check-header">
          <span class="qc-check-title">${escapeHtml(p.pass_name)}</span>
          <span class="qc-badge-pass">${p.score}% • ${p.status}</span>
        </div>
        <div style="font-size: 12px; color: #e2e8f0; margin: 4px 0;">
          ${escapeHtml(p.critique_summary)}
        </div>
        <div style="font-size: 11px; color: #fda4af; background: rgba(244,63,94,0.08); padding: 8px; border-radius: 4px;">
          <strong>Weaknesses Identified:</strong>
          <ul style="padding-left: 16px; margin-top: 4px;">${weaknesses}</ul>
        </div>
        <div style="font-size: 11px; color: #6ee7b7; background: rgba(16,185,129,0.08); padding: 8px; border-radius: 4px;">
          <strong>Refinements Applied:</strong>
          <ul style="padding-left: 16px; margin-top: 4px;">${refinements}</ul>
        </div>
      </div>
    `;
  }).join("");

  return `
    <h4 style="font-size: 14px; font-weight: 700; margin-bottom: 12px;">
      ✓ 6-Pass Professional Creative Editorial Review Log
    </h4>
    <div class="qc-checks-grid">
      ${cards}
    </div>
  `;
}

function handleSelectProjectRender(projId) {
  selectedProjectId = projId;
  renderVideoRenderingConsole(document.getElementById("main-content"));
}

function renderLiveStatusCard() {
  if (!activeRenderJobId) return '';
  return `
    <div class="render-progress-card">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
        <strong id="render-stage-txt" style="color: #fff; font-size: 13px;">Assembling multi-track documentary...</strong>
        <span id="render-pct-txt" style="color: var(--accent-emerald); font-weight: 800; font-size: 14px;">10%</span>
      </div>
      <div class="budget-progress-bg">
        <div id="render-progress-bar" class="budget-progress-bar" style="width: 10%; background: linear-gradient(90deg, #6366f1, #10b981);"></div>
      </div>
    </div>
  `;
}

async function triggerStartRender(projId) {
  try {
    const res = await fetch("/api/render/start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ project_id: projId })
    });
    const json = await res.json();
    if (json.status === "success") {
      activeRenderJobId = json.job_id;
      renderVideoRenderingConsole(document.getElementById("main-content"));
      pollRenderProgress(json.job_id, projId);
    } else {
      alert("Error starting render: " + json.message);
    }
  } catch (err) {
    alert("Network error: " + err.message);
  }
}

function pollRenderProgress(jobId, projId) {
  if (renderPollInterval) clearInterval(renderPollInterval);

  renderPollInterval = setInterval(async () => {
    try {
      const res = await fetch(`/api/render/job/${jobId}`);
      const json = await res.json();
      if (json.status === "success") {
        const job = json.job;
        const bar = document.getElementById("render-progress-bar");
        const pctTxt = document.getElementById("render-pct-txt");
        const stageTxt = document.getElementById("render-stage-txt");

        if (bar && pctTxt && stageTxt) {
          bar.style.width = `${job.progress_pct}%`;
          pctTxt.innerText = `${job.progress_pct}%`;
          stageTxt.innerText = job.stage_message || "Compositing video...";
        }

        if (job.status === "COMPLETED") {
          clearInterval(renderPollInterval);
          activeRenderJobId = null;
          alert("1080p Documentary Rendering Completed Successfully!");
          await refreshStudioData();
          renderVideoRenderingConsole(document.getElementById("main-content"));
        } else if (job.status === "FAILED") {
          clearInterval(renderPollInterval);
          activeRenderJobId = null;
          alert("Rendering failed: " + (job.error_message || "Unknown error"));
          renderVideoRenderingConsole(document.getElementById("main-content"));
        }
      }
    } catch (e) {
      console.error("Polling error:", e);
    }
  }, 1200);
}

async function handleAdvanceToQC(projId) {
  try {
    const res = await fetch(`/api/render/${projId}/advance`, {
      method: "POST",
      headers: { "Content-Type": "application/json" }
    });
    const json = await res.json();
    if (json.status === "success") {
      alert("Video Rendering Completed & Locked! Advancing to Stage 11: Quality Control.");
      await refreshStudioData();
      switchTab("qc");
    } else {
      alert("Error advancing: " + json.message);
    }
  } catch (err) {
    alert("Network error: " + err.message);
  }
}

function renderTheaterContent(exp, project) {
  if (!exp || !exp.has_video) {
    return `
      <div style="text-align: center; padding: 40px; color: var(--text-muted);">
        <p style="font-size: 14px; margin-bottom: 12px;">No rendered video found yet for this project.</p>
        <p style="font-size: 12px; margin-bottom: 20px;">
          Click "🎬 Start 1080p Documentary Render" to composite video streams, narration, and background audio beds.
        </p>
      </div>
    `;
  }

  return `
    <div style="margin-top: 24px;">
      <h4 style="font-size: 15px; font-weight: 700; margin-bottom: 12px;">Documentary Preview Theater (1080p Broadcast Quality)</h4>
      <div class="render-theater-box">
        <video controls poster="https://images.unsplash.com/photo-1542296332-2e4473faf563?auto=format&fit=crop&w=1200&q=80">
          <source src="${exp.video_url}" type="video/mp4">
          <track label="English" kind="subtitles" srclang="en" src="${exp.subtitles_url}" default>
        </video>
      </div>

      <div style="display: flex; gap: 12px; align-items: center; margin-top: 14px; font-size: 12px;">
        <a href="${exp.video_url}" download="documentary.mp4" class="btn btn-secondary">
          ⬇️ Download documentary.mp4 (${exp.file_size_mb} MB)
        </a>
        <a href="${exp.subtitles_url}" download="subtitles.srt" class="btn btn-secondary">
          ⬇️ Download subtitles.srt
        </a>
      </div>

      <!-- Advance Action Bar -->
      <div style="display: flex; justify-content: flex-end; gap: 12px; margin-top: 24px; padding-top: 16px; border-top: 1px solid var(--border-color);">
        <button class="btn btn-primary" onclick="handleAdvanceToQC('${project.id}')">
          Advance to Quality Control Agent →
        </button>
      </div>
    </div>
  `;
}

// ========================================================
// --- Phase 11: Thumbnail Studio Logic ---
// ========================================================

let projectThumbnails = [];
let isGeneratingThumbnails = false;

async function renderThumbnailStudio(container) {
  if (projects.length === 0) {
    container.innerHTML = `
      <div class="section-panel" style="text-align: center; padding: 40px;">
        <h3>No Project Selected</h3>
        <p style="color: var(--text-muted); font-size: 13px; margin: 12px 0 20px;">
          Create a documentary project first.
        </p>
        <button class="btn btn-primary" onclick="openNewProjectModal()">+ Create Project</button>
      </div>
    `;
    return;
  }

  if (!selectedProjectId) {
    selectedProjectId = projects[0].id;
  }

  const currentProj = projects.find(p => p.id === selectedProjectId) || projects[0];

  try {
    const res = await fetch(`/api/thumbnails/project/${currentProj.id}`);
    const json = await res.json();
    if (json.status === "success") {
      projectThumbnails = json.thumbnails || [];
    } else {
      projectThumbnails = [];
    }
  } catch (e) {
    projectThumbnails = [];
  }

  const projOptions = projects.map(p => `
    <option value="${p.id}" ${p.id === currentProj.id ? 'selected' : ''}>${escapeHtml(p.title)} (${p.pillar})</option>
  `).join("");

  container.innerHTML = `
    <div class="section-panel">
      <div class="section-panel-header">
        <div>
          <h3>Dual High-Impact Thumbnail Studio</h3>
          <p style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">
            Dual 1280x720 concepts with mobile scale (150px) readability validation
          </p>
        </div>
        <div style="display: flex; gap: 10px; align-items: center;">
          <select class="form-select" style="width: auto; min-width: 250px;" onchange="handleSelectProjectThumbnails(this.value)">
            ${projOptions}
          </select>
          <button class="btn btn-primary" onclick="triggerGenerateThumbnails('${currentProj.id}')" ${isGeneratingThumbnails ? 'disabled' : ''}>
            ${isGeneratingThumbnails ? 'Generating Thumbnails...' : '⚡ Generate Dual A/B Thumbnails'}
          </button>
        </div>
      </div>

      <div style="font-size: 13px; margin-bottom: 20px; color: #94a3b8; background: rgba(0,0,0,0.2); padding: 12px; border-radius: 6px;">
        <strong>Documentary:</strong> ${escapeHtml(currentProj.title)} | 
        <strong>Pillar:</strong> ${currentProj.pillar} | 
        <strong>Pipeline Stage:</strong> ${getStatusBadge(currentProj.status)}
      </div>

      <div id="thumbnails-deck-content">
        ${renderThumbnailsGrid(projectThumbnails, currentProj)}
      </div>
    </div>
  `;
}

function handleSelectProjectThumbnails(projId) {
  selectedProjectId = projId;
  renderThumbnailStudio(document.getElementById("main-content"));
}

async function triggerGenerateThumbnails(projId) {
  isGeneratingThumbnails = true;
  renderThumbnailStudio(document.getElementById("main-content"));
  try {
    const res = await fetch("/api/thumbnails/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ project_id: projId })
    });
    const json = await res.json();
    if (json.status === "success") {
      alert("Generated dual 1280x720 thumbnail concepts with mobile contrast scoring!");
      await refreshStudioData();
    } else {
      alert("Thumbnail generation error: " + json.message);
    }
  } catch (err) {
    alert("Network error: " + err.message);
  } finally {
    isGeneratingThumbnails = false;
    renderThumbnailStudio(document.getElementById("main-content"));
  }
}

function renderThumbnailsGrid(thumbs, project) {
  if (!thumbs || thumbs.length === 0) {
    return `
      <div style="text-align: center; padding: 40px; color: var(--text-muted);">
        <p style="font-size: 14px; margin-bottom: 12px;">No thumbnails generated yet for this documentary.</p>
        <p style="font-size: 12px; margin-bottom: 20px;">
          Click "⚡ Generate Dual A/B Thumbnails" to synthesize Concept #1 (Forensic Evidence) and Concept #2 (Systemic Mystery).
        </p>
      </div>
    `;
  }

  const cardsHtml = thumbs.map(t => {
    const ev = t.mobile_evaluation || {};
    const score = ev.score || 85;
    const isReadable = ev.is_readable !== false;
    return `
      <div class="thumb-card">
        <div class="thumb-preview-box">
          <img src="${t.web_url}" alt="Thumbnail Concept ${t.concept_number}">
        </div>
        <div style="padding: 16px;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <strong style="color: #fff; font-size: 14px;">Concept #${t.concept_number}: ${t.title}</strong>
            <span class="badge badge-completed">1280x720</span>
          </div>

          <div class="mobile-readability-box">
            <div>
              <div style="font-size: 11px; color: var(--text-muted); text-transform: uppercase;">Mobile Readability (150px)</div>
              <div style="font-size: 13px; font-weight: 700; color: ${isReadable ? '#34d399' : '#fbbf24'};">
                ${isReadable ? '✓ High Contrast & Legible' : '⚠ Marginal Contrast'}
              </div>
            </div>
            <div style="font-size: 20px; font-weight: 800; color: ${isReadable ? '#34d399' : '#fbbf24'};">
              ${score}%
            </div>
          </div>

          <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 14px;">
            <a href="${t.web_url}" download="thumbnail-${t.concept_number}.jpg" class="btn btn-secondary" style="font-size: 12px;">
              ⬇️ Download JPG
            </a>
            <span style="font-size: 11px; color: var(--text-muted);">YouTube Recommended: 16:9</span>
          </div>
        </div>
      </div>
    `;
  }).join("");

  return `
    <div class="thumb-grid">
      ${cardsHtml}
    </div>

    <div style="display: flex; justify-content: flex-end; gap: 12px; margin-top: 24px; padding-top: 16px; border-top: 1px solid var(--border-color);">
      <button class="btn btn-primary" onclick="switchTab('qc')">
        Proceed to Quality Control Center →
      </button>
    </div>
  `;
}

// ========================================================
// --- Phase 12: Quality Control Center Logic ---
// ========================================================

let currentQCReport = null;
let isInspectingQC = false;

async function renderQualityControlCenter(container) {
  if (projects.length === 0) {
    container.innerHTML = `
      <div class="section-panel" style="text-align: center; padding: 40px;">
        <h3>No Project Selected</h3>
        <p style="color: var(--text-muted); font-size: 13px; margin: 12px 0 20px;">
          Render documentary video before conducting Quality Control inspection.
        </p>
        <button class="btn btn-primary" onclick="openNewProjectModal()">+ Create Project</button>
      </div>
    `;
    return;
  }

  if (!selectedProjectId) {
    selectedProjectId = projects[0].id;
  }

  const currentProj = projects.find(p => p.id === selectedProjectId) || projects[0];

  try {
    const res = await fetch(`/api/qc/report/${currentProj.id}`);
    const json = await res.json();
    if (json.status === "success") {
      currentQCReport = json.report;
    } else {
      currentQCReport = null;
    }
  } catch (e) {
    currentQCReport = null;
  }

  const projOptions = projects.map(p => `
    <option value="${p.id}" ${p.id === currentProj.id ? 'selected' : ''}>${escapeHtml(p.title)} (${p.pillar})</option>
  `).join("");

  container.innerHTML = `
    <div class="section-panel">
      <div class="section-panel-header">
        <div>
          <h3>Automated Quality Control (QC) Center</h3>
          <p style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">
            Broadcast inspection of 1080p video, audio levels, subtitle sync, and copyright permissions
          </p>
        </div>
        <div style="display: flex; gap: 10px; align-items: center;">
          <select class="form-select" style="width: auto; min-width: 250px;" onchange="handleSelectProjectQC(this.value)">
            ${projOptions}
          </select>
          <button class="btn btn-primary" onclick="triggerRunQCInspection('${currentProj.id}')" ${isInspectingQC ? 'disabled' : ''}>
            ${isInspectingQC ? 'Inspecting Media...' : '🔍 Run Full QC Inspection'}
          </button>
        </div>
      </div>

      <div style="font-size: 13px; margin-bottom: 20px; color: #94a3b8; background: rgba(0,0,0,0.2); padding: 12px; border-radius: 6px;">
        <strong>Documentary:</strong> ${escapeHtml(currentProj.title)} | 
        <strong>Pillar:</strong> ${currentProj.pillar} | 
        <strong>Pipeline Stage:</strong> ${getStatusBadge(currentProj.status)}
      </div>

      <div id="qc-center-content">
        ${renderQCDeck(currentQCReport, currentProj)}
      </div>
    </div>
  `;
}

function handleSelectProjectQC(projId) {
  selectedProjectId = projId;
  renderQualityControlCenter(document.getElementById("main-content"));
}

async function triggerRunQCInspection(projId) {
  isInspectingQC = true;
  renderQualityControlCenter(document.getElementById("main-content"));
  try {
    const res = await fetch("/api/qc/run-inspection", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ project_id: projId })
    });
    const json = await res.json();
    if (json.status === "success") {
      alert(`QC Inspection Complete! Verdict: ${json.report.verdict} (${json.report.overall_score}%)`);
      await refreshStudioData();
    } else {
      alert("QC Inspection error: " + json.message);
    }
  } catch (err) {
    alert("Network error: " + err.message);
  } finally {
    isInspectingQC = false;
    renderQualityControlCenter(document.getElementById("main-content"));
  }
}

async function handleAdvanceFromQC(projId) {
  try {
    const res = await fetch(`/api/qc/${projId}/advance`, {
      method: "POST",
      headers: { "Content-Type": "application/json" }
    });
    const json = await res.json();
    if (json.status === "success") {
      alert("QC Certification Passed! Advanced to Stage 13: Final Export Package.");
      await refreshStudioData();
      switchTab("completed");
    } else {
      const errList = (json.failures || [json.message]).join("\n• ");
      alert(`Mandatory QC Gate Enforced!\n\nDocumentary cannot proceed to export:\n• ${errList}`);
    }
  } catch (err) {
    alert("Network error: " + err.message);
  }
}

async function handleRequestRepair(projId) {
  if (!confirm("Return project to Video Rendering stage to re-composite or adjust media assets?")) return;
  try {
    const res = await fetch(`/api/qc/${projId}/request-repair`, {
      method: "POST",
      headers: { "Content-Type": "application/json" }
    });
    const json = await res.json();
    if (json.status === "success") {
      alert("Project returned to Video Rendering for repair.");
      await refreshStudioData();
      switchTab("rendering");
    } else {
      alert("Error: " + json.message);
    }
  } catch (err) {
    alert("Network error: " + err.message);
  }
}

function renderQCDeck(report, project) {
  if (!report) {
    return `
      <div style="text-align: center; padding: 40px; color: var(--text-muted);">
        <p style="font-size: 14px; margin-bottom: 12px;">No QC report recorded yet for this project.</p>
        <p style="font-size: 12px; margin-bottom: 20px;">
          Click "🔍 Run Full QC Inspection" to inspect resolution, audio levels, subtitle sync, and asset rights.
        </p>
      </div>
    `;
  }

  const passed = report.passed;
  const checks = report.checks || [];

  const checksHtml = checks.map(c => {
    let badgeClass = "qc-badge-pass";
    let badgeText = "PASS";
    if (c.status === "WARN") {
      badgeClass = "qc-badge-warn";
      badgeText = "WARN";
    } else if (c.status === "FAIL") {
      badgeClass = "qc-badge-fail";
      badgeText = "FAIL";
    }

    return `
      <div class="qc-check-card">
        <div class="qc-check-header">
          <span class="qc-check-title">${escapeHtml(c.name)}</span>
          <span class="${badgeClass}">${badgeText}</span>
        </div>
        <div style="font-size: 11px; color: var(--text-muted); text-transform: uppercase;">
          Domain: ${c.category}
        </div>
        <div style="font-size: 12px; color: #cbd5e1; line-height: 1.4;">
          ${escapeHtml(c.details)}
        </div>
      </div>
    `;
  }).join("");

  const recommendationsHtml = (report.repair_recommendations || []).map(r => `
    <li style="margin-bottom: 6px;">${escapeHtml(r)}</li>
  `).join("");

  return `
    <!-- Top Summary Banner -->
    <div class="qc-banner ${passed ? 'passed' : 'failed'}">
      <div>
        <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 700; color: ${passed ? '#34d399' : '#fb7185'};">
          QC Broadcast Verdict
        </div>
        <div style="font-size: 22px; font-weight: 800; color: #fff; margin-top: 4px;">
          ${passed ? '✓ PASSED — BROADCAST CERTIFIED' : '✗ FAILED — REMEDIATION REQUIRED'}
        </div>
        <div style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">
          Inspected: ${new Date(report.inspected_at).toLocaleString()} | Video Duration: ${report.video_duration_sec}s
        </div>
      </div>
      <div style="text-align: right;">
        <div style="font-size: 11px; color: var(--text-muted); text-transform: uppercase;">Quality Score</div>
        <div class="qc-score-gauge" style="color: ${passed ? '#34d399' : '#fb7185'};">
          ${report.overall_score}%
        </div>
      </div>
    </div>

    <!-- Checks Grid -->
    <h4 style="font-size: 14px; font-weight: 700; margin-bottom: 14px;">Automated Inspection Matrix</h4>
    <div class="qc-checks-grid">
      ${checksHtml}
    </div>

    <!-- Repair Recommendations (if any) -->
    ${(report.repair_recommendations && report.repair_recommendations.length > 0) ? `
      <div style="background: rgba(244, 63, 94, 0.08); border: 1px solid rgba(244, 63, 94, 0.3); border-radius: 8px; padding: 16px; margin-top: 20px;">
        <h5 style="color: #fb7185; font-size: 13px; font-weight: 700; margin-bottom: 8px;">Actionable Repair Recommendations:</h5>
        <ul style="padding-left: 20px; font-size: 12px; color: #cbd5e1; line-height: 1.5;">
          ${recommendationsHtml}
        </ul>
      </div>
    ` : ''}

    <!-- Action Bar -->
    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 24px; padding-top: 16px; border-top: 1px solid var(--border-color);">
      <button class="btn btn-secondary" onclick="handleRequestRepair('${project.id}')">
        🛠️ Return to Video Rendering for Repair
      </button>
      <button class="btn btn-primary" onclick="handleAdvanceFromQC('${project.id}')">
        Advance to Final Export Package →
      </button>
    </div>
  `;
}

// ========================================================
// --- Phase 13: Completed Documentaries & Export Package ---
// ========================================================

let completedSummary = null;
let isBuildingPackage = false;

async function renderCompletedDocumentariesDeck(container) {
  if (projects.length === 0) {
    container.innerHTML = `
      <div class="section-panel" style="text-align: center; padding: 40px;">
        <h3>No Project Selected</h3>
        <p style="color: var(--text-muted); font-size: 13px; margin: 12px 0 20px;">
          Create a documentary project first.
        </p>
        <button class="btn btn-primary" onclick="openNewProjectModal()">+ Create Project</button>
      </div>
    `;
    return;
  }

  if (!selectedProjectId) {
    selectedProjectId = projects[0].id;
  }

  const currentProj = projects.find(p => p.id === selectedProjectId) || projects[0];

  try {
    const res = await fetch(`/api/export/summary/${currentProj.id}`);
    const json = await res.json();
    if (json.status === "success") {
      completedSummary = json;
    } else {
      completedSummary = null;
    }
  } catch (e) {
    completedSummary = null;
  }

  const projOptions = projects.map(p => `
    <option value="${p.id}" ${p.id === currentProj.id ? 'selected' : ''}>${escapeHtml(p.title)} (${p.pillar})</option>
  `).join("");

  container.innerHTML = `
    <div class="section-panel">
      <div class="section-panel-header">
        <div>
          <h3>Completed Documentaries & Release Packages</h3>
          <p style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">
            Full release packages with 1080p MP4, dual thumbnails, SRT subtitles, sources dossier, and production audit report
          </p>
        </div>
        <div style="display: flex; gap: 10px; align-items: center;">
          <select class="form-select" style="width: auto; min-width: 250px;" onchange="handleSelectProjectCompleted(this.value)">
            ${projOptions}
          </select>
          <button class="btn btn-primary" onclick="triggerAssemblePackage('${currentProj.id}')" ${isBuildingPackage ? 'disabled' : ''}>
            ${isBuildingPackage ? 'Assembling Package...' : '📦 Assemble Release Package (.ZIP)'}
          </button>
        </div>
      </div>

      <div style="font-size: 13px; margin-bottom: 20px; color: #94a3b8; background: rgba(0,0,0,0.2); padding: 12px; border-radius: 6px;">
        <strong>Documentary:</strong> ${escapeHtml(currentProj.title)} | 
        <strong>Pillar:</strong> ${currentProj.pillar} | 
        <strong>Pipeline Stage:</strong> ${getStatusBadge(currentProj.status)}
      </div>

      <div id="completed-deck-content">
        ${renderCompletedPackageDeck(completedSummary, currentProj)}
      </div>
    </div>
  `;
}

function handleSelectProjectCompleted(projId) {
  selectedProjectId = projId;
  renderCompletedDocumentariesDeck(document.getElementById("main-content"));
}

async function triggerAssemblePackage(projId) {
  isBuildingPackage = true;
  renderCompletedDocumentariesDeck(document.getElementById("main-content"));
  try {
    const res = await fetch("/api/export/package", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ project_id: projId })
    });
    const json = await res.json();
    if (json.status === "success") {
      alert("Release package assembled successfully with all deliverables and audit reports!");
      await refreshStudioData();
    } else {
      alert("Package error: " + json.message);
    }
  } catch (err) {
    alert("Network error: " + err.message);
  } finally {
    isBuildingPackage = false;
    renderCompletedDocumentariesDeck(document.getElementById("main-content"));
  }
}

function renderCompletedPackageDeck(sum, project) {
  if (!sum || !sum.has_package) {
    return `
      <div style="text-align: center; padding: 40px; color: var(--text-muted);">
        <p style="font-size: 14px; margin-bottom: 12px;">No release package assembled yet for this project.</p>
        <p style="font-size: 12px; margin-bottom: 20px;">
          Click "📦 Assemble Release Package (.ZIP)" to generate the final release bundle containing all video, audio, captions, and attribution documents.
        </p>
      </div>
    `;
  }

  const rep = sum.production_report || {};
  const fin = rep.financial_audit || {};
  const narr = rep.narrative_metrics || {};
  const vis = rep.visual_manifest_summary || {};

  return `
    <!-- Hero Download Card -->
    <div class="export-hero-card">
      <div>
        <div style="font-size: 12px; text-transform: uppercase; color: #34d399; font-weight: 700; letter-spacing: 0.05em;">
          ✓ Release Package Ready for Upload
        </div>
        <div style="font-size: 20px; font-weight: 800; color: #fff; margin-top: 4px;">
          docuforge_package.zip (${sum.package_size_mb} MB)
        </div>
        <div style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">
          All 7 deliverables bundled for YouTube upload, archive preservation, and rights documentation
        </div>
      </div>
      <div>
        <a href="${sum.package_url}" class="btn btn-primary" style="font-size: 14px; padding: 12px 20px;">
          ⬇️ Download Release ZIP
        </a>
      </div>
    </div>

    <!-- Deliverables Manifest Table -->
    <h4 style="font-size: 14px; font-weight: 700; margin-bottom: 12px;">Package Contents & Direct Links</h4>
    <div style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 8px; overflow: hidden; margin-bottom: 24px;">
      <table class="deliverables-table">
        <thead>
          <tr>
            <th>Deliverable</th>
            <th>Type</th>
            <th>Specification</th>
            <th>Direct Access</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>documentary.mp4</strong></td>
            <td>Master Video</td>
            <td>1080p Full HD / H.264 / 30 FPS / EBU R128 (-14 LUFS)</td>
            <td><a href="/exports/${project.id}/documentary.mp4" download class="btn btn-secondary" style="padding: 4px 10px; font-size: 11px;">⬇️ MP4</a></td>
          </tr>
          <tr>
            <td><strong>thumbnail-1.jpg</strong></td>
            <td>Thumbnail Concept 1</td>
            <td>1280x720 / Forensic Direct Evidence Drama</td>
            <td><a href="/exports/${project.id}/thumbnail-1.jpg" download class="btn btn-secondary" style="padding: 4px 10px; font-size: 11px;">⬇️ JPG</a></td>
          </tr>
          <tr>
            <td><strong>thumbnail-2.jpg</strong></td>
            <td>Thumbnail Concept 2</td>
            <td>1280x720 / Systemic Financial Mystery Drama</td>
            <td><a href="/exports/${project.id}/thumbnail-2.jpg" download class="btn btn-secondary" style="padding: 4px 10px; font-size: 11px;">⬇️ JPG</a></td>
          </tr>
          <tr>
            <td><strong>subtitles.srt</strong></td>
            <td>Closed Captions</td>
            <td>Broadcast Standard UTF-8 SubRip Closed Captions</td>
            <td><a href="/exports/${project.id}/subtitles.srt" download class="btn btn-secondary" style="padding: 4px 10px; font-size: 11px;">⬇️ SRT</a></td>
          </tr>
          <tr>
            <td><strong>research_sources.txt</strong></td>
            <td>Research Dossier</td>
            <td>Primary Evidence, Declassified Records & Full Bibliography</td>
            <td><a href="/exports/${project.id}/research_sources.txt" target="_blank" class="btn btn-secondary" style="padding: 4px 10px; font-size: 11px;">📄 View</a></td>
          </tr>
          <tr>
            <td><strong>youtube_description.txt</strong></td>
            <td>Video Metadata</td>
            <td>Timestamps, Synopsis & CC-BY Licensing Attributions</td>
            <td><a href="/exports/${project.id}/youtube_description.txt" target="_blank" class="btn btn-secondary" style="padding: 4px 10px; font-size: 11px;">📄 View</a></td>
          </tr>
          <tr>
            <td><strong>production_report.json</strong></td>
            <td>Audit Manifest</td>
            <td>Financial Audit, QC Certification, and Storyboard Metrics</td>
            <td><a href="/exports/${project.id}/production_report.json" target="_blank" class="btn btn-secondary" style="padding: 4px 10px; font-size: 11px;">📊 JSON</a></td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Production Audit Metrics -->
    <h4 style="font-size: 14px; font-weight: 700; margin-bottom: 12px;">Production & Financial Audit Summary</h4>
    <div class="script-metrics-bar">
      <div class="script-metric-item">
        <span class="script-metric-val" style="color: #34d399;">$${(fin.total_production_cost_usd || 0).toFixed(4)}</span>
        <span class="script-metric-lbl">Total Production Cost</span>
      </div>
      <div class="script-metric-item">
        <span class="script-metric-val" style="color: #38bdf8;">$0.00</span>
        <span class="script-metric-lbl">Local GPU Render ($0.00)</span>
      </div>
      <div class="script-metric-item">
        <span class="script-metric-val">${narr.word_count || 0}</span>
        <span class="script-metric-lbl">Script Word Count</span>
      </div>
      <div class="script-metric-item">
        <span class="script-metric-val">${vis.total_assets_licensed || 0}</span>
        <span class="script-metric-lbl">Assets Licensed</span>
      </div>
      <div class="script-metric-item">
        <span class="script-metric-val" style="color: #facc15;">$${(fin.monthly_budget_remaining_usd || 50).toFixed(2)}</span>
        <span class="script-metric-lbl">Monthly Budget Left</span>
      </div>
    </div>
  `;
}

