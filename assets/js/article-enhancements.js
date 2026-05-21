(function () {
  var progressBar = document.querySelector(".reading-progress-bar");
  var article = document.querySelector(".post-content");
  var toc = document.querySelector(".post-toc");
  var tocList = document.querySelector(".post-toc-list");
  var existingMarkdownToc = article && article.querySelector("#markdown-toc");

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

    var headings = Array.prototype.slice.call(article.querySelectorAll("h1, h2, h3, h4, h5")).filter(function (heading) {
      var text = heading.textContent.trim().toLowerCase();
      return !heading.classList.contains("post-title") && text !== "table of contents";
    });
    if (headings.length < 4) return;

    if (!existingMarkdownToc && document.body.classList.contains("study-guides-index")) return;

    var usedIds = {};
    var stack = [{ level: 0, list: tocList }];

    headings.forEach(function (heading) {
      var level = Number(heading.tagName.slice(1));
      var id = ensureHeadingId(heading, usedIds);
      var item = document.createElement("li");
      var link = document.createElement("a");
      var text = heading.textContent.trim();

      item.className = "post-toc-item post-toc-" + heading.tagName.toLowerCase();
      link.href = "#" + id;
      link.textContent = text === "Table of Contents" ? "TOC" : text;
      item.appendChild(link);

      while (stack.length > 1 && level <= stack[stack.length - 1].level) {
        stack.pop();
      }

      var parent = stack[stack.length - 1];
      if (level > parent.level + 1 && parent.item) {
        level = parent.level + 1;
      }

      parent.list.appendChild(item);

      var childList = document.createElement("ol");
      childList.className = "post-toc-list post-toc-children";
      item.appendChild(childList);
      stack.push({ level: level, list: childList, item: item });
    });

    toc.hidden = false;
  }

  function setupCopyButtons() {
    var buttons = Array.prototype.slice.call(document.querySelectorAll(".copy-code-button"));

    buttons.forEach(function (button) {
      button.addEventListener("click", function () {
        var example = button.closest(".code-example");
        var code = example && example.querySelector("pre code");
        if (!code || !navigator.clipboard) return;

        navigator.clipboard.writeText(code.textContent).then(function () {
          var original = button.textContent;
          button.textContent = "copied";
          setTimeout(function () {
            button.textContent = original;
          }, 1400);
        });
      });
    });
  }

  buildToc();
  setupCopyButtons();
  updateReadingProgress();

  window.addEventListener("scroll", updateReadingProgress, { passive: true });
  window.addEventListener("resize", updateReadingProgress);
})();
