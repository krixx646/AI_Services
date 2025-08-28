console.log("site.js loaded");

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
