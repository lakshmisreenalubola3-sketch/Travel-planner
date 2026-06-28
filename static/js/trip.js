// WanderAI trip.js — renders the JSON itinerary into HTML

document.addEventListener('DOMContentLoaded', function () {
  const container = document.getElementById('itineraryContent');
  const budgetEl = document.getElementById('budgetSidebar');
  const tipsEl = document.getElementById('tipsSidebar');

  if (!container || typeof RAW_ITINERARY === 'undefined') return;

  let data;
  try {
    data = typeof RAW_ITINERARY === 'string' ? JSON.parse(RAW_ITINERARY) : RAW_ITINERARY;
  } catch (e) {
    container.innerHTML = `<div class="alert alert-warning">Could not parse itinerary data.</div>`;
    return;
  }

  // ── Overview ──
  let html = '';
  if (data.overview) {
    html += `<div class="sidebar-card mb-4">
      <p class="mb-0" style="font-size:0.95rem; line-height:1.7; color:var(--text-primary)">
        <i class="bi bi-info-circle-fill me-2 text-accent"></i>${data.overview}
      </p>
    </div>`;
  }

  // ── Days ──
  if (data.days && Array.isArray(data.days)) {
    data.days.forEach(function (day) {
      html += `<div class="day-card">
        <div class="day-card-header" onclick="toggleDay(this)">
          <div class="day-number-badge">${day.day}</div>
          <div class="flex-grow-1">
            <p class="day-title">${escHtml(day.title || 'Day ' + day.day)}</p>
            ${day.daily_cost ? `<span class="day-cost"><i class="bi bi-currency-rupee"></i>~₹${Number(day.daily_cost).toFixed(0)} today</span>` : ''}
          </div>
          <i class="bi bi-chevron-down toggle-icon" style="color:var(--text-muted); transition: transform 0.25s;"></i>
        </div>
        <div class="day-body">`;

      // Time blocks
      if (day.morning) html += timeBlock('Morning', 'bi-sunrise', day.morning);
      if (day.afternoon) html += timeBlock('Afternoon', 'bi-sun', day.afternoon);
      if (day.evening) html += timeBlock('Evening', 'bi-moon-stars', day.evening);

      // Meals
      if (day.meals) {
        html += `<div class="meals-section">
          <p style="font-size:0.78rem; font-weight:700; text-transform:uppercase; letter-spacing:1px; color:var(--text-muted); margin-bottom:0.5rem;">
            <i class="bi bi-egg-fried me-1 text-accent"></i>Meals
          </p>`;
        const meals = day.meals;
        if (meals.breakfast) html += mealItem('🌅 Breakfast', meals.breakfast);
        if (meals.lunch) html += mealItem('☀️ Lunch', meals.lunch);
        if (meals.dinner) html += mealItem('🌙 Dinner', meals.dinner);
        html += `</div>`;
      }

      // Highlights
      if (day.highlights && day.highlights.length) {
        html += `<div class="highlight-tags">`;
        day.highlights.forEach(h => { html += `<span class="highlight-tag"><i class="bi bi-pin-map me-1"></i>${escHtml(h)}</span>`; });
        html += `</div>`;
      }

      html += `</div></div>`;
    });
  }

  container.innerHTML = html;

  // ── Budget Sidebar ──
  if (budgetEl && data.budget_breakdown) {
    const b = data.budget_breakdown;
    const total = b.total || Object.values(b).reduce((s, v) => s + (isNaN(v) ? 0 : v), 0);
    const items = [
      { label: 'Accommodation', key: 'accommodation', icon: 'bi-building' },
      { label: 'Food & Dining', key: 'food', icon: 'bi-egg-fried' },
      { label: 'Transportation', key: 'transportation', icon: 'bi-bus-front' },
      { label: 'Activities', key: 'activities', icon: 'bi-ticket-perforated' },
      { label: 'Miscellaneous', key: 'miscellaneous', icon: 'bi-three-dots' }
    ];
    let bHtml = `<div class="sidebar-card mb-4"><h6 class="sidebar-card-title"><i class="bi bi-wallet2 me-2 text-accent"></i>Budget Breakdown</h6>`;
    items.forEach(item => {
      const val = b[item.key] || 0;
      const pct = total > 0 ? Math.round((val / total) * 100) : 0;
      bHtml += `<div class="budget-item">
        <div class="budget-label">
          <span><i class="bi ${item.icon} me-1"></i>${item.label}</span>
          <span>₹${Number(val).toFixed(0)} <small class="text-muted">(${pct}%)</small></span>
        </div>
        <div class="budget-bar"><div class="budget-bar-fill" style="width:${pct}%"></div></div>
      </div>`;
    });
    bHtml += `<div class="budget-total"><span>Total Estimated</span><span style="color:var(--accent)">₹${Number(total).toFixed(0)}</span></div></div>`;
    budgetEl.innerHTML = bHtml;
  }

  // ── Tips Sidebar ──
  if (tipsEl && data.travel_tips && data.travel_tips.length) {
    let tHtml = `<div class="sidebar-card"><h6 class="sidebar-card-title"><i class="bi bi-lightbulb me-2 text-accent"></i>Travel Tips</h6>`;
    data.travel_tips.forEach((tip, i) => {
      tHtml += `<div class="tip-item"><span class="tip-num">${i + 1}</span><span>${escHtml(tip)}</span></div>`;
    });
    tHtml += `</div>`;
    tipsEl.innerHTML = tHtml;
  }

  // Animate budget bars
  setTimeout(() => {
    document.querySelectorAll('.budget-bar-fill').forEach(el => {
      const w = el.style.width;
      el.style.width = '0';
      setTimeout(() => { el.style.width = w; }, 100);
    });
  }, 200);
});

function timeBlock(label, icon, text) {
  let content = '';
  if (Array.isArray(text)) {
    content = '<ul class="place-list">';
    text.forEach(t => { content += `<li>${escHtml(t)}</li>`; });
    content += '</ul>';
  } else {
    content = `<p>${escHtml(text)}</p>`;
  }
  return `<div class="time-block">
    <div class="time-block-label"><i class="bi ${icon} me-1"></i>${label}</div>
    ${content}
  </div>`;
}

function mealItem(label, text) {
  return `<div class="meal-item"><span class="meal-label">${label}</span><span>${escHtml(text)}</span></div>`;
}

function escHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function toggleDay(header) {
  const body = header.nextElementSibling;
  const icon = header.querySelector('.toggle-icon');
  const isOpen = body.style.display !== 'none';
  body.style.display = isOpen ? 'none' : 'block';
  if (icon) icon.style.transform = isOpen ? 'rotate(-90deg)' : 'rotate(0deg)';
}
