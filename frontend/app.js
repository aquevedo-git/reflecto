


// --- Debug UI Footer ---
function updateSessionDebugFooter() {
  let footer = document.getElementById('session-debug-footer');
  if (!footer) {
    footer = document.createElement('div');
    footer.id = 'session-debug-footer';
    footer.style.position = 'fixed';
    footer.style.bottom = '0';
    footer.style.left = '0';
    footer.style.width = '100%';
    footer.style.background = '#222';
    footer.style.color = '#43e97b';
    footer.style.fontSize = '14px';
    footer.style.padding = '4px 12px';
    footer.style.zIndex = '9999';
    document.body.appendChild(footer);
  }
  footer.textContent = sessionActive && activeSessionId
    ? `Session Active: ${activeSessionId}`
    : 'No active session.';
}

// === GLOBAL SESSION STATE ===
let activeSessionId = null;
let sseSource = null;
let sessionActive = false;

// Debug log helper (top-level)
function debugLog(...args) {
  console.log('[Reflecto Session]', ...args);
}


// API base detection (moved to top for hoisting)
function detectApiBase() {
  // If running on localhost (dev)
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    return 'http://localhost:8000';
  }
  // If running inside Docker (nginx container)
  if (window.location.hostname === 'reflecto-frontend' || window.location.hostname === 'reflecto-backend') {
    return '/api';
  }
}

// Set API base URL (moved to top for hoisting)
const API_BASE = detectApiBase();

// Loading state UI helper (moved to top for hoisting)
function setLoading(isLoading) {
  const startBtn = document.getElementById('start-session');
  // Accessibility: focus on response area after new output
  function focusResponse() {
    const response = document.getElementById('response');
    if (response && response.focus) response.focus();
  }
  // Add ARIA live and tabindex for streaming output
  ['questions', 'response', 'presence', 'closing'].forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.setAttribute('tabindex', '-1');
      el.setAttribute('aria-live', 'polite');
    }
  });
  startBtn.disabled = isLoading;
  if (isLoading) {
    startBtn.classList.add('loading');
    document.body.classList.add('session-started');
    document.getElementById('session-loading').style.display = 'block';
  } else {
    startBtn.classList.remove('loading');
    document.getElementById('session-loading').style.display = 'none';
  }
}


// Main session start logic (refactored for single session)
async function startSession() {
  debugLog('Start session button clicked');
  let domMsg = document.getElementById('dom-debug-msg');
  if (sessionActive) {
    debugLog('Session already active, ignoring start.');
    if (domMsg) domMsg.textContent = 'Session already active!';
    // Optionally show a warning to user
    return;
  }
  setLoading(true);
  // Clear any previous error
  let errorEl = document.getElementById('session-error');
  if (errorEl) errorEl.style.display = 'none';
  try {
    debugLog('Sending fetch to', `${API_BASE}/session/start`);
    if (domMsg) domMsg.textContent = 'Sending fetch to ' + `${API_BASE}/session/start`;
    const res = await fetch(`${API_BASE}/session/start`, { method: 'POST' });
    debugLog('Fetch response:', res);
    if (domMsg) domMsg.textContent = 'Fetch response: ' + res.status;
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    debugLog('Session started, session_id:', data.session_id);
    if (domMsg) domMsg.textContent = 'Session started, starting SSE stream.';
    activeSessionId = data.session_id;
    sessionActive = true;
    updateSessionDebugFooter();
    setLoading(false);
    startSSEStream(activeSessionId);
  } catch (err) {
    debugLog('Error in startSession:', err);
    if (domMsg) domMsg.textContent = 'Error: ' + (err.message || err);
    setLoading(false);
    // Show error in UI
    if (!errorEl) {
      errorEl = document.createElement('div');
      errorEl.id = 'session-error';
      errorEl.style.color = 'red';
      errorEl.style.margin = '12px 0';
      errorEl.style.fontWeight = 'bold';
      const container = document.getElementById('container') || document.body;
      container.insertBefore(errorEl, container.firstChild);
    }
    errorEl.textContent = 'Failed to start session: ' + (err.message || err);
    errorEl.style.display = 'block';
    sessionActive = false;
    activeSessionId = null;
    updateSessionDebugFooter();
  }
}

// Debug: log when DOM is loaded and attach Start Session event
document.addEventListener('DOMContentLoaded', () => {
  debugLog('DOM fully loaded');
  debugLog('All button elements:', Array.from(document.getElementsByTagName('button')).map(b => b.id));
  debugLog('All IDs in DOM:', Array.from(document.querySelectorAll('[id]')).map(e => e.id));
  debugLog('Full HTML:', document.documentElement.outerHTML);
  let domMsg = document.getElementById('dom-debug-msg');
  if (!domMsg) {
    domMsg = document.createElement('div');
    domMsg.id = 'dom-debug-msg';
    domMsg.style.color = '#43e97b';
    domMsg.style.margin = '8px 0';
    domMsg.style.fontWeight = 'bold';
    const container = document.getElementById('container') || document.body;
    container.insertBefore(domMsg, container.firstChild);
  }
  domMsg.textContent = 'DOM loaded, JS running.';

  // Attach Start Session button event
  debugLog('Looking for start-session button');
  const startBtn = document.getElementById('start-session');
  debugLog('startBtn:', startBtn);
  if (startBtn) {
    debugLog('Found start-session button, attaching event');
    domMsg.textContent = 'Start button found, event attached.';
    startBtn.addEventListener('click', startSession);
  } else {
    debugLog('Start-session button NOT found');
    domMsg.textContent = 'Start button NOT found!';
  }
});

// SSE Event Router (refactored)
function startSSEStream(sessionId) {
  if (sseSource) {
    debugLog('Closing previous SSE source');
    sseSource.close();
    sseSource = null;
  }
  if (!sessionId) {
    debugLog('No sessionId provided to startSSEStream');
    return;
  }
  const url = `${API_BASE}/session/${sessionId}/stream`;
  sseSource = new EventSource(url);
  debugLog('SSE EventSource created:', url);
  // Streaming activity indicator
  const heartbeat = document.getElementById('heartbeat-dot');
  if (heartbeat) heartbeat.style.display = 'inline-block';
  sseSource.onopen = () => {
    debugLog('SSE connection opened');
    if (heartbeat) heartbeat.classList.add('active');
  };
  sseSource.onerror = (e) => {
    debugLog('SSE error:', e);
    if (heartbeat) heartbeat.classList.remove('active');
  };
  // Bind all backend events
  sseSource.addEventListener('avatar', e => {
    updateAvatarUI(JSON.parse(e.data));
  });
  sseSource.addEventListener('questions', e => {
    const data = JSON.parse(e.data);
    updateQuestionsUI(data);
  });
  sseSource.addEventListener('response_chunk', e => {
    const data = JSON.parse(e.data);
    appendResponseChunkUI(data);
  });
  sseSource.addEventListener('presence', e => {
    const data = JSON.parse(e.data);
    updatePresenceUI(data);
  });
  sseSource.addEventListener('skills', e => {
    const data = JSON.parse(e.data);
    updateSkillsUI(data);
  });
  sseSource.addEventListener('timeline_phase', e => {
    const data = JSON.parse(e.data);
    updateTimelinePhaseUI(data);
  });
  sseSource.addEventListener('closing', e => {
    const data = JSON.parse(e.data);
    showClosingUI(data);
    // Disable answer input on closing
    disableAnswerInput();
  });
  sseSource.addEventListener('done', e => {
    const data = JSON.parse(e.data);
    showSessionDoneUI(data);
    if (sseSource) sseSource.close();
    sseSource = null;
    sessionActive = false;
    activeSessionId = null;
    updateSessionDebugFooter();
    if (heartbeat) heartbeat.style.display = 'none';
    debugLog('Session done, SSE closed, state reset');
  });
}
// Fetch and render stream events (single source of truth)
async function fetchAndRenderStream(sessionId = null) {
  const streamPayload = {
    input: {
      user_id: 'demo',
      user_state: { avatar: 'reflecto' },
      history: [],
      flow_context: {},
      raw_response: null
    }
  };
  let url = `${API_BASE}/session/stream`;
  let options = {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(streamPayload)
  };
  if (sessionId) {
    // For replay, use GET /session/{session_id}/replay
    url = `${API_BASE}/session/${sessionId}/replay`;
    options = { method: 'GET' };
  }
  debugLog('Fetching stream/replay:', url, options);
  const streamRes = await fetch(url, options);
  debugLog('Stream/replay response:', streamRes);
  const streamText = await streamRes.text();
  debugLog('Stream/replay text:', streamText);
  // If replay, parse JSON; else, parse SSE blocks
  if (sessionId) {
    try {
      const replayData = JSON.parse(streamText);
      renderReplaySession(replayData);
      return;
    } catch (e) {
      debugLog('Replay parse error:', e);
    }
  }
  const events = streamText.split('\n\n').filter(e => e.trim());
  events.forEach(eventBlock => {
    const eventMatch = eventBlock.match(/^event: (\w+)\ndata: (.*)$/s);
    if (!eventMatch) return;
    const eventType = eventMatch[1];
    let eventData;
    try {
      eventData = JSON.parse(eventMatch[2]);
    } catch (e) {
      eventData = eventMatch[2];
    }
    debugLog('SSE event:', eventType, eventData);
    switch (eventType) {
      case 'avatar':
        updateAvatarUI({ state: "AWAKE" });
        break;
      case 'questions':
        document.getElementById('questions').textContent = (eventData.questions || []).join('\n');
        showAnswerInput(eventData.questions[0]);
        break;
      case 'response_chunk':
        document.getElementById('response').textContent = eventData.text || '';
        break;
      case 'presence':
        document.getElementById('presence').textContent = JSON.stringify(eventData);
        break;
      case 'closing':
        document.getElementById('closing').textContent = JSON.stringify(eventData);
        break;
      case 'done':
        document.getElementById('session-lifecycle').textContent = '⏹️ Ended';
        break;
      default:
        debugLog('Unknown event:', eventType, eventData);
    }
  });
}
// Global app state
const appState = {
  sessionActive: false,
  presence: null,
  skills: null
};
// Set API base URL

// Computes avatar state from presence
function computeAvatarState(presence) {
  let emoji = "🙂";
  let label = "Neutral";
  let cssClass = "avatar-neutral";
  if (presence && presence.state) {
    if (presence.state === "AWAKE") {
      emoji = "🙂";
      label = "Awake";
      cssClass = "avatar-neutral";
    } else if (presence.state === "CALM") {
      emoji = "😌";
      label = "Calm";
      cssClass = "avatar-calm";
    } else if (presence.state === "SLEEPING") {
      emoji = "😴";
      label = "Sleeping";
      cssClass = "avatar-sleeping";
    }
  }
  return { emoji, label, cssClass };


// Environment-aware API base detection
function detectApiBase() {
  // If running on localhost (dev)
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    return 'http://localhost:8000';
  }
  // If running inside Docker (nginx container)
  if (window.location.hostname === 'reflecto-frontend' || window.location.hostname === 'reflecto-backend') {
    return '/api';
  }

}

function setLoading(isLoading) {
  const startBtn = document.getElementById('start-session');
        // Accessibility: focus on response area after new output
        function focusResponse() {
          const response = document.getElementById('response');
          if (response && response.focus) response.focus();
        }
        // Add ARIA live and tabindex for streaming output
        ['questions', 'response', 'presence', 'closing'].forEach(id => {
          const el = document.getElementById(id);
          if (el) {
            el.setAttribute('tabindex', '-1');
            el.setAttribute('aria-live', 'polite');
          }
        });
  startBtn.disabled = isLoading;
  if (isLoading) {
    startBtn.classList.add('loading');
    document.body.classList.add('session-started');
    document.getElementById('session-loading').style.display = 'block';
  } else {
    startBtn.classList.remove('loading');
    document.getElementById('session-loading').style.display = 'none';
  }
}



// Debug log helper (top-level)
function debugLog(...args) {
  console.log('[Reflecto DEBUG]', ...args);
}

function updateAvatarUI(presence) {
  const avatarState = computeAvatarState(presence);
  const avatar = document.getElementById("avatar");
  // ...existing code...
}

// Background reaction by timeOfDay
function setBackgroundByTimeOfDay(timeOfDay) {
  const body = document.body;
  body.classList.remove('bg-morning', 'bg-afternoon', 'bg-evening', 'bg-night');
  if (timeOfDay === 'morning') {
    body.classList.add('bg-morning');
  } else if (timeOfDay === 'afternoon') {
    body.classList.add('bg-afternoon');
  } else if (timeOfDay === 'evening') {
    body.classList.add('bg-evening');
  } else if (timeOfDay === 'night') {
    body.classList.add('bg-night');
  }
}

// Main session start logic
async function startSession() {
  debugLog('Start session button clicked');
  let domMsg = document.getElementById('dom-debug-msg');
  if (domMsg) domMsg.textContent = 'Start session button clicked.';
  setLoading(true);
  // Clear any previous error
  let errorEl = document.getElementById('session-error');
  if (errorEl) errorEl.style.display = 'none';
  try {
    debugLog('Sending fetch to', `${API_BASE}/session/start`);
    if (domMsg) domMsg.textContent = 'Sending fetch to ' + `${API_BASE}/session/start`;
    const res = await fetch(`${API_BASE}/session/start`, { method: 'POST' });
    debugLog('Fetch response:', res);
    if (domMsg) domMsg.textContent = 'Fetch response: ' + res.status;
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    await res.json();
    debugLog('Session started, starting SSE stream');
    if (domMsg) domMsg.textContent = 'Session started, starting SSE stream.';
    setLoading(false);
    startSSEStream();
  } catch (err) {
    debugLog('Error in startSession:', err);
    if (domMsg) domMsg.textContent = 'Error: ' + (err.message || err);
    setLoading(false);
    // Show error in UI
    if (!errorEl) {
      errorEl = document.createElement('div');
      errorEl.id = 'session-error';
      errorEl.style.color = 'red';
      errorEl.style.margin = '12px 0';
      errorEl.style.fontWeight = 'bold';
      const container = document.getElementById('container') || document.body;
      container.insertBefore(errorEl, container.firstChild);
    }
    errorEl.textContent = 'Failed to start session: ' + (err.message || err);
    errorEl.style.display = 'block';
  }
}

// Attach startSession to button (after DOM loaded)
document.addEventListener('DOMContentLoaded', () => {
  debugLog('Looking for start-session button');
  let domMsg = document.getElementById('dom-debug-msg');
  const startBtn = document.getElementById('start-session');
  debugLog('startBtn:', startBtn);
  if (startBtn) {
    debugLog('Found start-session button, attaching event');
    if (domMsg) domMsg.textContent = 'Start button found, event attached.';
    startBtn.addEventListener('click', startSession);
  } else {
    debugLog('Start-session button NOT found');
    if (domMsg) domMsg.textContent = 'Start button NOT found!';
  }
});


function showAnswerInput(question) {
  let answerInput = document.getElementById('answer-input');
  let submitBtn = document.getElementById('submit-answer');
  if (!answerInput) {
    answerInput = document.createElement('input');
    answerInput.type = 'text';
    answerInput.id = 'answer-input';
    answerInput.placeholder = 'Type your answer...';
    answerInput.style.marginTop = '10px';
    answerInput.style.width = '80%';
    document.getElementById('questions').parentNode.insertBefore(answerInput, document.getElementById('questions').nextSibling);
  }
  if (!submitBtn) {
    submitBtn = document.createElement('button');
    submitBtn.textContent = 'Submit Answer';
    submitBtn.id = 'submit-answer';
    submitBtn.style.marginLeft = '10px';
    answerInput.parentNode.insertBefore(submitBtn, answerInput.nextSibling);
  }
  answerInput.disabled = !sessionActive;
  submitBtn.disabled = !sessionActive;
  submitBtn.onclick = async () => {
    const answer = answerInput.value;
    if (!answer || !activeSessionId) return;
    // Send answer as note, let backend assign score
    const action = {
      type: 'log_mood',
      note: answer,
      ts: new Date().toISOString(),
      session_id: activeSessionId
    };
    try {
      debugLog('POST /write/action', action);
      submitBtn.disabled = true;
      answerInput.disabled = true;
      const res = await fetch(`${API_BASE}/write/action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: activeSessionId, answer })
      });
      debugLog('Action response:', res);
      // Wait for SSE response_chunk or questions event to clear input
    } catch (err) {
      debugLog('Action error:', err);
      document.getElementById('response').textContent = 'Submission failed.';
      answerInput.disabled = false;
      submitBtn.disabled = false;
    }
  };
}

function disableAnswerInput() {
  const answerInput = document.getElementById('answer-input');
  const submitBtn = document.getElementById('submit-answer');
  if (answerInput) answerInput.disabled = true;
  if (submitBtn) submitBtn.disabled = true;
}

// --- UI Update Functions ---
function updateAvatarUI(presence) {
  const avatarState = computeAvatarState(presence);
  const avatar = document.getElementById('avatar');
  if (avatar) {
    avatar.textContent = avatarState.emoji;
    avatar.className = 'avatar ' + avatarState.cssClass;
  }
  const avatarStatus = document.getElementById('avatar-status');
  if (avatarStatus) {
    avatarStatus.textContent = avatarState.label;
  }
}

function updateQuestionsUI(data) {
  const qEl = document.getElementById('questions');
  if (qEl) qEl.textContent = (data.questions || []).join('\n');
  showAnswerInput(data.questions ? data.questions[0] : '');
  // Enable input only on new question
  const answerInput = document.getElementById('answer-input');
  const submitBtn = document.getElementById('submit-answer');
  if (answerInput) answerInput.value = '';
  if (answerInput) answerInput.disabled = false;
  if (submitBtn) submitBtn.disabled = false;
}

function appendResponseChunkUI(data) {
  const rEl = document.getElementById('response');
  if (rEl) rEl.textContent += data.text || '';
  // Clear input after response
  const answerInput = document.getElementById('answer-input');
  if (answerInput) answerInput.value = '';
}

function updatePresenceUI(data) {
  const pEl = document.getElementById('presence');
  if (pEl) pEl.textContent = data.state || JSON.stringify(data);
  // Deterministic cognition badge
  const badge = document.getElementById('avatar-status');
  if (badge) badge.textContent = data.state || 'Unknown';
}

function updateSkillsUI(data) {
  // Animate skill bars
  const skills = ['financial', 'health', 'focus', 'relationships'];
  skills.forEach(skill => {
    const val = data[skill] || 0;
    const bar = document.querySelector(`#skill-${skill} .skill-bar-inner`);
    const label = document.querySelector(`#skill-${skill} .skill-value`);
    if (bar) {
      bar.style.width = `${val}%`;
      bar.classList.add('bar-animate');
      setTimeout(() => bar.classList.remove('bar-animate'), 600);
    }
    if (label) label.textContent = val;
  });
}

function updateTimelinePhaseUI(data) {
  // Highlight timeline node
  const steps = document.querySelectorAll('.timeline-step');
  steps.forEach(step => {
    if (step.dataset.phase === data.phase) {
      step.classList.add('active');
    } else {
      step.classList.remove('active');
    }
  });
}

function showClosingUI(data) {
  const cEl = document.getElementById('closing');
  if (cEl) cEl.textContent = data.phrase || JSON.stringify(data);
  // Show closing animation/state
  document.getElementById('session-lifecycle').textContent = '🛑 Closing';
}


function showSessionDoneUI(data) {
  document.getElementById('session-lifecycle').textContent = '⏹️ Ended';
  // Disable input
  disableAnswerInput();
  // Show summary panel
  showCompletionSummaryPanel(data);
}
// --- Debug UI Footer ---
function updateSessionDebugFooter() {
  let footer = document.getElementById('session-debug-footer');
  if (!footer) {
    footer = document.createElement('div');
    footer.id = 'session-debug-footer';
    footer.style.position = 'fixed';
    footer.style.bottom = '0';
    footer.style.left = '0';
    footer.style.width = '100%';
    footer.style.background = '#222';
    footer.style.color = '#43e97b';
    footer.style.fontSize = '14px';
    footer.style.padding = '4px 12px';
    footer.style.zIndex = '9999';
    document.body.appendChild(footer);
  }
  footer.textContent = sessionActive && activeSessionId
    ? `Session Active: ${activeSessionId}`
    : 'No active session.';
}


// --- Debug UI Footer ---
function updateSessionDebugFooter() {
  let footer = document.getElementById('session-debug-footer');
  if (!footer) {
    footer = document.createElement('div');
    footer.id = 'session-debug-footer';
    footer.style.position = 'fixed';
    footer.style.bottom = '0';
    footer.style.left = '0';
    footer.style.width = '100%';
    footer.style.background = '#222';
    footer.style.color = '#43e97b';
    footer.style.fontSize = '14px';
    footer.style.padding = '4px 12px';
    footer.style.zIndex = '9999';
    document.body.appendChild(footer);
  }
  footer.textContent = sessionActive && activeSessionId
    ? `Session Active: ${activeSessionId}`
    : 'No active session.';
}

// Initial debug footer
document.addEventListener('DOMContentLoaded', updateSessionDebugFooter);

function showCompletionSummaryPanel(data) {
  // Simple summary panel implementation
  let summary = document.getElementById('completion-summary');
  if (!summary) {
    summary = document.createElement('div');
    summary.id = 'completion-summary';
    summary.className = 'completion-summary-panel';
    document.body.appendChild(summary);
  }
  summary.innerHTML = `<h3>Session Complete</h3><pre>${JSON.stringify(data, null, 2)}</pre>`;
  summary.style.display = 'block';
}

// --- Replay session logic ---
const replayBtn = document.getElementById('replay-session');
if (replayBtn) {
  replayBtn.addEventListener('click', async () => {
    const sessionId = prompt('Enter session ID to replay:');
    if (!sessionId) return;
    debugLog('Replaying session:', sessionId);
    startSSEStream(sessionId);
  });
}

// Render replayed session data
// (Replay now handled by SSE stream)
}
