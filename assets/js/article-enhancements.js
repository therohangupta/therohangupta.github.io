(function () {
  var progressBar = document.querySelector(".reading-progress-bar");
  var article = document.querySelector(".post-content");
  var toc = document.querySelector(".post-toc");
  var tocList = document.querySelector(".post-toc-list");

  function updateReadingProgress() {
    if (!progressBar || !article) return;

    var articleTop = article.offsetTop;
    var articleHeight = article.scrollHeight - window.innerHeight;
    var scrolled = window.scrollY - articleTop;
    var progress = articleHeight > 0 ? scrolled / articleHeight : 0;
    var clamped = Math.max(0, Math.min(1, progress));

    progressBar.style.transform = "scaleX(" + clamped + ")";
  }

  function slugify(text) {
    return text
      .toLowerCase()
      .trim()
      .replace(/[^\w\s-]/g, "")
      .replace(/\s+/g, "-")
      .replace(/-+/g, "-");
  }

  function ensureHeadingId(heading, usedIds) {
    if (heading.id) {
      usedIds[heading.id] = true;
      return heading.id;
    }

    var base = slugify(heading.textContent) || "section";
    var id = base;
    var index = 2;

    while (usedIds[id] || document.getElementById(id)) {
      id = base + "-" + index;
      index += 1;
    }

    heading.id = id;
    usedIds[id] = true;
    return id;
  }

  function buildToc() {
    if (!article || !toc || !tocList) return;

    var headings = Array.prototype.slice.call(article.querySelectorAll("h2, h3, h4, h5"));
    if (headings.length < 4) return;

    var usedIds = {};
    headings.forEach(function (heading) {
      var id = ensureHeadingId(heading, usedIds);
      var item = document.createElement("li");
      var link = document.createElement("a");

      item.className = "post-toc-item post-toc-" + heading.tagName.toLowerCase();
      link.href = "#" + id;
      link.textContent = heading.textContent;
      item.appendChild(link);
      tocList.appendChild(item);
    });

    toc.hidden = false;
  }

  buildToc();
  updateReadingProgress();

  window.addEventListener("scroll", updateReadingProgress, { passive: true });
  window.addEventListener("resize", updateReadingProgress);
})();
