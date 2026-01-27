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
}
// Unified app state
const appState = {
  sessionActive: false,
  presence: null,
  skills: {},
};
let avatarRendered = false;

document.getElementById('start-session').addEventListener('click', startSession);

async function startSession() {
  avatarRendered = false;
  setLoading(true);
  try {
    // 1️⃣ Backend returns JSON
    const res = await fetch('http://127.0.0.1:8000/session/start', { method: 'POST' });
    const data = await res.json();
    console.log('Session started:', data);

    setLoading(false);
    // Safety: force initial UI update in case SSE is delayed
    updateAvatarUI({ state: "AWAKE" });
    // 2️⃣ Open SSE connection for this session (after success)
    const es = new EventSource('http://127.0.0.1:8000/stream/demo');

    let lastPresenceState = null;
    let lastTimeOfDay = null;
    let lastHeartbeatReceived = Date.now();
    // Show avatar container immediately
    document.getElementById('avatar-container').style.display = 'flex';

    // Heartbeat indicator setup
    let heartbeatDot = document.getElementById('heartbeat-dot');
    if (!heartbeatDot) {
      heartbeatDot = document.createElement('span');
      heartbeatDot.id = 'heartbeat-dot';
      heartbeatDot.style.display = 'inline-block';
      heartbeatDot.style.width = '10px';
      heartbeatDot.style.height = '10px';
      heartbeatDot.style.borderRadius = '50%';
      heartbeatDot.style.background = '#4caf50';
      heartbeatDot.style.marginLeft = '8px';
      heartbeatDot.style.verticalAlign = 'middle';
      heartbeatDot.style.transition = 'transform 0.2s cubic-bezier(.4,0,.2,1), background 0.2s';
      heartbeatDot.style.transform = 'scale(1)';
      heartbeatDot.title = 'Live heartbeat';
      // Insert immediately next to avatar-status
      const status = document.getElementById('avatar-status');
      if (status && !document.getElementById('heartbeat-dot')) {
        status.parentNode.insertBefore(heartbeatDot, status.nextSibling);
      }
    }

    // Heartbeat pulse function
    function pulseHeartbeat() {
      heartbeatDot.style.background = '#4caf50';
      heartbeatDot.style.transform = 'scale(1.4)';
      setTimeout(() => {
        heartbeatDot.style.transform = 'scale(1)';
        heartbeatDot.style.background = '#4caf50';
      }, 200);
    }

    es.addEventListener('stream_open', e => {
      appState.sessionActive = true;
      document.getElementById('start-session').style.display = 'none';
      const status = document.getElementById('avatar-status');
      if (status) status.textContent = 'Session active';
      document.body.classList.add('session-live');
    });

    es.addEventListener('presence', e => {
      const data = JSON.parse(e.data);
      appState.presence = data;
      console.log('[UI] presence received', data);
      if (data.state && data.state !== lastPresenceState) {
        console.log('[Avatar] State changed:', lastPresenceState, '→', data.state);
        lastPresenceState = data.state;
      }
      // Accept both timeOfDay and time_of_day keys
      const tod = data.timeOfDay || data.time_of_day;
      if (tod && tod !== lastTimeOfDay) {
        setBackgroundByTimeOfDay(tod);
        console.log('[UI] time_of_day received', tod);
        lastTimeOfDay = tod;
      }
      updateAvatarUI(data);
      console.log('[Avatar] UI updated');
    });

    // Dedicated heartbeat event listener
    es.addEventListener('heartbeat', e => {
      lastHeartbeatReceived = Date.now();
      pulseHeartbeat();
      console.log('[UI] heartbeat received');
    });

    es.addEventListener('time_of_day', e => {
      // Handle explicit time_of_day event
      const data = JSON.parse(e.data);
      if (data.time_of_day) {
        setBackgroundByTimeOfDay(data.time_of_day);
        console.log('[UI] time_of_day received', data.time_of_day);
      }
    });

    es.addEventListener('skills', e => {
      const skillsDict = JSON.parse(e.data);
      appState.skills = skillsDict;
      // Log event
      console.log('[UI] skills received', skillsDict);
      // Show and animate skill bars
      const skillsSection = document.getElementById('skills-section');
      if (skillsSection) {
        skillsSection.style.display = 'block';
        skillsSection.classList.add('skills-visible');
      }
      // Always animate bars on skills event
      renderSkills(skillsDict);
      document.body.classList.add('session-live');
    });

    es.addEventListener('stream', e => {
      if (typeof onStreamEvent === 'function') {
        onStreamEvent(JSON.parse(e.data));
      }
      console.log('[SSE] stream event:', e.data);
    });

    es.addEventListener('closing', e => {
      if (typeof onSessionClose === 'function') {
        onSessionClose(JSON.parse(e.data));
      }
      console.log('[SSE] closing event:', e.data);
    });

    // Log every SSE event
    es.onmessage = function(e) {
      // Generic fallback
      console.log('[SSE] generic event:', e);
    };

    // Heartbeat timeout: turn red if no heartbeat in 5s
    setInterval(() => {
      if (appState.sessionActive && Date.now() - lastHeartbeatReceived > 5000) {
        heartbeatDot.style.background = '#e53935';
        console.warn('[SSE] No heartbeat event received in >5s!');
      }
    }, 2000);
  } catch (err) {
    console.error(err);
    setLoading(false);
  }
}

function setLoading(isLoading) {
  const startBtn = document.getElementById('start-session');
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



// Step 1: Declare as normal function
function updateAvatarUI(presence) {
  const avatarState = computeAvatarState(presence);
  const avatar = document.getElementById("avatar");
  if (avatar) {
    avatar.textContent = avatarState.emoji;
    avatar.className = avatarState.cssClass;
  }
  const avatarLabel = document.getElementById("avatar-label");
  if (avatarLabel) {
    avatarLabel.textContent = avatarState.label;
  }
  // Sync status text with presence.state
  const status = document.getElementById('avatar-status');
  if (status && presence.state) {
    if (presence.state === "AWAKE") {
      status.textContent = "Awake";
    } else if (presence.state === "CALM") {
      status.textContent = "Calm";
    } else if (presence.state === "SLEEPING") {
      status.textContent = "Sleeping";
    }
  }
}

// Skills UI update (skills)
function renderSkills(skillsDict) {
  // ...existing code...
  // Map skill names to bar IDs
  const skillMap = {
    financial: 'skill-financial',
    health: 'skill-health',
    focus: 'skill-focus',
    relationships: 'skill-relationships'
  };
  Object.entries(skillMap).forEach(([name, id]) => {
    const bar = document.getElementById(id);
    if (!bar) return;
    const barInner = bar.querySelector('.skill-bar-inner');
    const valueDiv = bar.querySelector('.skill-value');
    const val = Math.max(0, Math.min(100, Number(skillsDict[name] || 0)));
    // Animate width
    barInner.style.width = val + '%';
    valueDiv.textContent = val;
    // Animate bar
    barInner.classList.remove('bar-animate');
    void barInner.offsetWidth;
    barInner.classList.add('bar-animate');
  });
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
