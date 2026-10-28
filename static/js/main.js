const keepScroll = sessionStorage.getItem('keep-scroll');
if (keepScroll !== null) {
  sessionStorage.removeItem('keep-scroll');
  history.scrollRestoration = 'manual';
  window.scrollTo(0, Number(keepScroll));
}

const slider = document.getElementById('slider');
if (slider) {
  const slides = slider.querySelectorAll('.slide');
  const dots = slider.querySelector('.dots');
  let current = 0;
  let timer;

  const show = (index) => {
    current = (index + slides.length) % slides.length;
    slides.forEach((slide, i) => slide.classList.toggle('active', i === current));
    dots.querySelectorAll('button').forEach((dot, i) => dot.classList.toggle('active', i === current));
  };
  const restart = () => {
    clearInterval(timer);
    timer = setInterval(() => show(current + 1), 5000);
  };

  slides.forEach((_, i) => {
    const dot = document.createElement('button');
    dot.onclick = () => { show(i); restart(); };
    dots.appendChild(dot);
  });
  slider.querySelector('.next').onclick = () => { show(current + 1); restart(); };
  slider.querySelector('.prev').onclick = () => { show(current - 1); restart(); };
  show(0);
  restart();
}

const filterForm = document.getElementById('filter-form');
if (filterForm) {
  const gridArea = document.getElementById('grid-area');
  let timer;

  const params = (page) => {
    const query = new URLSearchParams(new FormData(filterForm));
    if (page > 1) query.set('page', page);
    return query;
  };

  const load = async (page) => {
    gridArea.classList.add('loading');
    const response = await fetch(filterForm.dataset.api + '?' + params(page));
    const data = await response.json();
    gridArea.innerHTML = data.html;
    gridArea.classList.remove('loading');
    history.replaceState(null, '', '?' + params(page));
  };

  const delayed = () => { clearTimeout(timer); timer = setTimeout(() => load(1), 300); };
  filterForm.addEventListener('input', delayed);
  filterForm.addEventListener('submit', (event) => { event.preventDefault(); load(1); });
  document.querySelector('[form="filter-form"]').addEventListener('input', delayed);
  document.querySelector('.filter-toggle').onclick = () => document.querySelector('.filters').classList.toggle('open');

  gridArea.addEventListener('click', (event) => {
    const link = event.target.closest('[data-page]');
    if (!link) return;
    event.preventDefault();
    load(Number(link.dataset.page));
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
}

const mainImg = document.getElementById('main-img');
if (mainImg) {
  document.querySelectorAll('.thumbs img').forEach((thumb) => {
    thumb.onclick = () => { mainImg.src = thumb.src; };
  });
}

document.querySelectorAll('.tab-btn').forEach((button) => {
  button.onclick = () => {
    document.querySelectorAll('.tab-btn').forEach((b) => b.classList.remove('active'));
    document.querySelectorAll('.tab-panel').forEach((p) => p.classList.remove('active'));
    button.classList.add('active');
    document.getElementById('tab-' + button.dataset.tab).classList.add('active');
  };
});

setTimeout(() => document.querySelectorAll('.toast').forEach((toast) => toast.remove()), 3500);

const confirmBox = document.getElementById('confirm-box');
if (confirmBox) {
  let confirmForm = null;
  document.querySelectorAll('form[data-confirm]').forEach((form) => {
    form.addEventListener('submit', (event) => {
      event.preventDefault();
      confirmForm = form;
      document.getElementById('confirm-text').textContent = form.dataset.confirm;
      confirmBox.showModal();
    });
  });
  document.getElementById('confirm-yes').onclick = () => {
    const form = confirmForm;
    confirmForm = null;
    confirmBox.close();
    if (form) form.submit();
  };
  document.getElementById('confirm-no').onclick = () => {
    confirmForm = null;
    confirmBox.close();
  };
}

document.querySelectorAll('form').forEach((form) => {
  if (!form.querySelector('input[name="next"]')) return;
  form.addEventListener('submit', () => {
    sessionStorage.setItem('keep-scroll', String(window.scrollY));
  });
});

const themeToggle = document.getElementById('theme-toggle');
if (themeToggle) {
  const label = () => {
    const dark = document.documentElement.classList.contains('dark');
    const text = dark ? 'حالت روز' : 'حالت شب';
    themeToggle.title = text;
    themeToggle.setAttribute('aria-label', text);
  };
  label();
  themeToggle.onclick = () => {
    const dark = document.documentElement.classList.toggle('dark');
    localStorage.setItem('theme', dark ? 'dark' : 'light');
    label();
  };
}

document.querySelectorAll('.resend-btn').forEach((btn) => {
  let left = Number(btn.getAttribute('data-wait') || 0);
  const fa = (n) => String(n).replace(/\d/g, (d) => '۰۱۲۳۴۵۶۷۸۹'[d]);
  const tick = () => {
    if (left <= 0) {
      btn.disabled = false;
      btn.textContent = 'ارسال دوباره کد';
      return;
    }
    btn.disabled = true;
    btn.textContent = 'ارسال دوباره (' + fa(left) + ')';
    left -= 1;
    setTimeout(tick, 1000);
  };
  if (left > 0) tick();
});
