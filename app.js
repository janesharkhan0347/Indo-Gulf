// IndoGulf — Main JS

// Mobile menu toggle
document.addEventListener('DOMContentLoaded', () => {
  const btn  = document.getElementById('mobile-menu-btn');
  const menu = document.getElementById('mobile-menu');
  if (btn && menu) {
    btn.addEventListener('click', () => {
      menu.classList.toggle('hidden');
    });
  }

  // Auto-dismiss flash messages after 4 seconds
  document.querySelectorAll('.flash-msg').forEach(el => {
    setTimeout(() => {
      el.style.transition = 'opacity 0.5s';
      el.style.opacity = '0';
      setTimeout(() => el.remove(), 500);
    }, 4000);
  });

  // Image preview on file input (for product/logo forms)
  const imageInputs = document.querySelectorAll('input[type="file"]');
  imageInputs.forEach(input => {
    input.addEventListener('change', e => {
      const file = e.target.files[0];
      if (!file) return;
      const preview = document.getElementById('image-preview');
      if (preview) {
        const reader = new FileReader();
        reader.onload = ev => { preview.src = ev.target.result; preview.classList.remove('hidden'); };
        reader.readAsDataURL(file);
      }
    });
  });

  // Confirm before delete forms
  document.querySelectorAll('form[data-confirm]').forEach(form => {
    form.addEventListener('submit', e => {
      if (!confirm(form.dataset.confirm)) e.preventDefault();
    });
  });
});