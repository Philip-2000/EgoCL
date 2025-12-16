const videoEl = document.getElementById('video');
const tracksContainer = document.getElementById('tracks');
const videoSelect = document.getElementById('videoSelect');
const currentLabelEl = document.getElementById('currentLabel');

let currentVideoId = null;
let annotations = [];
let duration = 0;

async function fetchVideos() {
  const res = await fetch('/api/videos');
  const data = await res.json();
  return data.videos || [];
}

async function fetchAnnotations(videoId) {
  const res = await fetch(`/api/videos/${videoId}/annotations`);
  if (!res.ok) return [];
  const data = await res.json();
  return data.annotations || [];
}

function groupByCategory(items) {
  const map = new Map();
  items.forEach((a) => {
    const key = a.category || '未分组';
    if (!map.has(key)) map.set(key, []);
    map.get(key).push(a);
  });
  return Array.from(map.entries()).map(([category, segments]) => ({ category, segments }));
}

function colorForCategory(category, len) {
  // stable palette hash
  const colors = [
    '#ff0000', '#ff7f00', '#ffff00', '#7fff00', '#00ff00', '#00ff7f',
    '#00ffff', '#007fff', '#0000ff', '#7f00ff', '#ff00ff', '#ff007f',
    '#ff1493', '#ffd700', '#00fa9a', '#8a2be2', '#dc143c', '#ff4500',
    '#2e8b57', '#4682b4', '#ff69b4', '#adff2f', '#20b2aa', '#b8860b'
  ];
  // create numeric seed from category + length
  const seedStr = (category || '') + '|' + (len || 0);
  let hash = 2166136261;
  for (let i = 0; i < seedStr.length; i++) {
    hash ^= seedStr.charCodeAt(i);
    hash = Math.imul(hash, 16777619);
  }
  hash = hash >>> 0;

  // seeded PRNG (mulberry32)
  function mulberry32(a) {
    return function() {
      let t = (a += 0x6D2B79F5);
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  const rand = mulberry32(hash);

  // shuffle a copy of the palette deterministically
  const shuffled = colors.slice();
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(rand() * (i + 1));
    const tmp = shuffled[i];
    shuffled[i] = shuffled[j];
    shuffled[j] = tmp;
  }

  // rotate based on hash and length to add more variation
  const rot = (hash + (len || 0)) % shuffled.length;
  if (rot > 0) {
    const head = shuffled.splice(0, rot);
    shuffled.push(...head);
  }
  //我让COPILOT给我洗个牌，它莫名其妙的给我写了上面这么长好长一坨，我也不知道它在干嘛，不过反正结果是洗好了牌
  return shuffled;
}

function time_display(second) {
  second = second.toFixed(1);
  const h = Math.floor(second / 3600);
  const m = Math.floor((second % 3600) / 60);
  const s = Math.floor(second % 60);
  if(h > 0) {
    return `${h.toString()}h${m.toString()}m${s.toString()}`;
  }
  else if(m > 0) {
    return `${m.toString()}m${s.toString()}s`;
  }
  else {
    return `${s.toString()}s`;
  }
}

function renderTracks() {
  annotations = annotations.map((a) => {// expand any segment shorter than 1s to 1s keeping midpoint and clamping to [0, duration]
    const s = Math.max(0, a.start || 0);
    const e = a.end != null ? Math.min(duration || 0, a.end) : (duration || 0);

    if (isNaN(s) || isNaN(e) || e < s) return { ...a, start: s, end: e };

    const len = e - s;
    // if already >= 1s or video shorter than 1s, just clamp and keep
    if (len >= 1 || (duration || 0) <= 1) {
      return { ...a, start: s, end: e };
    }

    const mid = (s + e) / 2;
    let newStart = mid - 0.5;
    let newEnd = mid + 0.5;

    if (newStart < 0) {
      newStart = 0;
      newEnd = Math.min(duration, newStart + 1);
    }
    if (newEnd > duration) {
      newEnd = duration;
      newStart = Math.max(0, newEnd - 1);
    }

    return { ...a, start: newStart, end: newEnd };
  });
  console.log('totally annotations after expand:', annotations.length);

  tracksContainer.innerHTML = '';
  if (!duration || !annotations.length) return;
  const grouped = groupByCategory(annotations);
  console.log('Rendering tracks:', grouped);
  grouped.forEach(({ category, segments }) => {
    const groupTitle = document.createElement('div');
    groupTitle.className = 'track-group-title';
    groupTitle.textContent = category;

    const row = document.createElement('div');
    row.className = 'track-row';
    row.style.width = videoEl.clientWidth + 'px';

    const colors = colorForCategory(category, segments.length);

    segments.forEach((seg) => {
      const start = Math.max(0, seg.start || 0);
      const end = Math.min(duration, seg.end != null ? seg.end : duration);
      if (end < start-0.01) return;
      const leftPct = (start / duration) * 100;
      const widthPct = ((end - start) / duration) * 100;
      const box = document.createElement('div');
      box.className = 'segment';
      box.style.left = leftPct + '%';
      box.style.width = widthPct + '%';
      box.style.backgroundColor = colors[segments.indexOf(seg) % colors.length];
      box.title = `${category}: ${seg.label || ''} (${time_display(start)} - ${time_display(end)})`;
      row.appendChild(box);
    });

    const label = document.createElement('div');
    label.textContent = category;
    label.style.position = 'absolute';
    label.style.left = '-100px';
    label.style.top = '2px';

    const wrapper = document.createElement('div');
    wrapper.style.position = 'relative';
    // wrapper.style.paddingLeft = '100px';
    wrapper.appendChild(groupTitle);
    wrapper.appendChild(row);

    tracksContainer.appendChild(wrapper);
  });
}

function updateCurrentLabel() {
  const t = videoEl.currentTime || 0;
  const active = annotations.filter((a) => (a.start || 0) <= t && t < (a.end != null ? a.end : Number.MAX_VALUE));
  if (!active.length) {
    currentLabelEl.textContent = '';
    return;
  }
  const grouped = groupByCategory(active);
  const lines = grouped.map(({ category, segments }) => {
    const names = segments.map((s) => s.label || '').filter(Boolean).join('，');
    return `${category}：${names}`;
  });
  
  const senil = lines.slice().reverse();
  currentLabelEl.innerHTML = senil.join('  <br>  ');
}

async function selectVideo(videoId) {
  currentVideoId = videoId;
  // set src using server streaming endpoint
  videoEl.src = `/video/${encodeURIComponent(videoId)}`;
  annotations = await fetchAnnotations(videoId);
  // Render tracks after metadata so we know duration
  if (videoEl.readyState >= 1) {
    duration = videoEl.duration || 0;
    renderTracks();
  }
}

async function init() {
  const videos = await fetchVideos();
  videoSelect.innerHTML = '';
  videos.forEach((v) => {
    const opt = document.createElement('option');
    opt.value = v.id;
    opt.textContent = v.title || v.id;
    opt.style = 'color: black;';
    videoSelect.appendChild(opt);
  });
  if (videos.length) {
    await selectVideo(videos[0].id);
    videoSelect.value = videos[0].id;
  }
}

videoSelect.addEventListener('change', async (e) => {
  await selectVideo(e.target.value);
});

videoEl.addEventListener('loadedmetadata', () => {
  duration = videoEl.duration || 0;
  renderTracks();
});

videoEl.addEventListener('timeupdate', () => {
  updateCurrentLabel();
});

window.addEventListener('resize', () => {
  renderTracks();
});

init();
