// WanderAI main.js — global helpers

// Auto-dismiss alerts after 5s
document.addEventListener('DOMContentLoaded', function () {
  setTimeout(function () {
    document.querySelectorAll('.alert').forEach(function (el) {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(el);
      bsAlert.close();
    });
  }, 5000);
});
