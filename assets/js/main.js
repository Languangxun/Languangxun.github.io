(function () {
  document.documentElement.classList.add("js");

  var reduces = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var hero = document.querySelector(".hero");
  var ink = document.querySelector(".ink-svg");

  function finishWriting() {
    if (hero) hero.classList.add("writing-done");
  }

  if (ink) {
    var secs = parseFloat(ink.getAttribute("data-duration") || "0");
    if (reduces || !(secs > 0)) {
      finishWriting();
    } else {
      setTimeout(finishWriting, secs * 1000 + 150);
    }
  } else {
    finishWriting();
  }

  var reveals = document.querySelectorAll(".reveal");

  if (reduces || !("IntersectionObserver" in window)) {
    reveals.forEach(function (el) { el.classList.add("in"); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("in");
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0 });
    reveals.forEach(function (el) { io.observe(el); });
  }

  function fallbackCopy(text, done) {
    var ta = document.createElement("textarea");
    ta.value = text;
    ta.setAttribute("readonly", "");
    ta.style.position = "fixed";
    ta.style.opacity = "0";
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand("copy"); done(); } catch (e) {}
    document.body.removeChild(ta);
  }

  document.querySelectorAll("[data-copy]").forEach(function (el) {
    el.addEventListener("click", function () {
      var text = el.getAttribute("data-copy");
      var hint = el.querySelector(".copy-hint");
      var done = function () {
        el.classList.add("copied");
        if (hint) {
          hint.textContent = "已复制";
          setTimeout(function () {
            hint.textContent = "点击复制";
            el.classList.remove("copied");
          }, 1600);
        }
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done).catch(function () {
          fallbackCopy(text, done);
        });
      } else {
        fallbackCopy(text, done);
      }
    });
  });
})();
