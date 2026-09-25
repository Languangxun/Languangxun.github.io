(function () {
  document.documentElement.classList.add("js");

  var reduces = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var hero = document.querySelector(".hero");
  var ink = document.querySelector(".ink-svg");

  function finishWriting() {
    if (hero) hero.classList.add("writing-done");
  }

  if (ink) {
    var inks = Array.prototype.slice.call(ink.querySelectorAll(".hk-ink"));
    var outlines = Array.prototype.slice.call(ink.querySelectorAll(".hk-outline"));
    var animatable = inks.length > 0 && typeof inks[0].animate === "function";

    if (!reduces && animatable) {
      var t = 350;
      inks.forEach(function (path) {
        var idx = path.getAttribute("data-i");
        var isLine = path.classList.contains("hk-line");
        var len = 100;
        try { len = path.getTotalLength(); } catch (e) {}
        var dur = isLine ? 900 : Math.max(170, Math.min(340, len * 0.85));

        path.style.strokeDasharray = len;
        path.style.strokeDashoffset = len;
        path.animate(
          [{ strokeDashoffset: len }, { strokeDashoffset: 0 }],
          { duration: dur, delay: t, easing: "cubic-bezier(0.33, 0, 0.2, 1)", fill: "forwards" }
        );

        if (!isLine && idx !== null) {
          var outline = outlines[parseInt(idx, 10)];
          if (outline) {
            outline.animate(
              [{ opacity: 0 }, { opacity: 1 }],
              { duration: 240, delay: t + dur * 0.6, fill: "forwards" }
            );
          }
          path.animate(
            [{ opacity: 1 }, { opacity: 0 }],
            { duration: 260, delay: t + dur * 0.74, fill: "forwards" }
          );
        }
        t += dur * 0.78;
      });
      setTimeout(finishWriting, t + 250);
    } else {
      outlines.forEach(function (path) { path.style.opacity = "1"; });
      inks.forEach(function (path) { path.style.display = "none"; });
      finishWriting();
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
    }, { threshold: 0.12 });
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
