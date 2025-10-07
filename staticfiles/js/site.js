console.log("site.js loaded");

// Enhanced navbar visibility on scroll
(function() {
  var navbar = document.querySelector('.navbar');
  var lastScrollTop = 0;
  
  window.addEventListener('scroll', function() {
    var scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    
    // Add 'scrolled' class when user scrolls down
    if (scrollTop > 50) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
    
    lastScrollTop = scrollTop;
  });
})();

(function loadBotpressDemo() {
  try {
    fetch('/api/demo/info/')
      .then(function (res) { return res.ok ? res.json() : null; })
      .then(function (data) {
        if (!data || !data.bot_url) return;
        var inject = document.createElement('script');
        inject.src = 'https://cdn.botpress.cloud/webchat/v1/inject.js';
        inject.async = true;
        document.head.appendChild(inject);

        var config = document.createElement('script');
        config.src = data.bot_url; // expected Botpress config.js URL
        config.defer = true;
        document.head.appendChild(config);
      })
      .catch(function () {});
  } catch (e) {}
})();
