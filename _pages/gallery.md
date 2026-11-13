---
layout: page
title: Gallery
permalink: /gallery/
description: Year-wise and section-wise gallery of conferences, awards, research, field tests, and projects.
nav: false
nav_order: 3
social: true
---

{% comment %}
Data source: \_data/gallery.yml

Each item:

- year: 2025
  month: 8 # 1–12; sections are ordered latest month first
  section: "Field test – Tifton"
  path: assets/img/gallery/2025/field_test_01.jpg
  caption: "UGA/Tifton field test – Husky + UR5e setup"
  alt: "Robot setup in field"
  {% endcomment %}

{% assign years = site.data.gallery | map: "year" | uniq | sort | reverse %}

{% if years.size == 0 %}

<div class="alert alert-warning">
  <b>No gallery data found.</b><br>
  Create <code>_data/gallery.yml</code> and add entries.
</div>
{% endif %}

<div class="gallery-layout">
  <!-- LEFT: Sticky sidebar (Years + Sections) -->
  <aside class="gallery-sidebar">
    <div class="gallery-sidebar-inner">
      <div class="gallery-sidebar-title">Browse</div>

      <nav class="gallery-years">
        {%- for y in years -%}
          <div class="gallery-year-block">
            <a href="#y{{ y }}" class="gallery-year-link">{{ y }}</a>

            {%- assign year_items_for_nav = site.data.gallery | where: "year", y | sort: "month", "first" | reverse -%}
            {%- assign sections_for_nav = year_items_for_nav | map: "section" | compact | uniq -%}
            {%- if sections_for_nav.size == 0 -%}
              {%- assign sections_for_nav = "Other" | split: "," -%}
            {%- endif -%}

            <div class="gallery-sections">
              {%- for s in sections_for_nav -%}
                {%- assign sid = s | slugify -%}
                <a class="gallery-section-link" href="#y{{ y }}-{{ sid }}">{{ s }}</a>
              {%- endfor -%}
            </div>
          </div>
        {%- endfor -%}
      </nav>
    </div>

  </aside>

  <!-- RIGHT: Gallery content -->
  <main class="gallery-main projects">
    {%- for y in years -%}
      <a class="anchor" id="y{{ y }}"></a>
      <h2 class="category">{{ y }}</h2>

      {% assign year_items = site.data.gallery | where: "year", y %}
      {%- comment -%} Sections ordered by month (latest first); entries without a month go last {%- endcomment -%}
      {% assign year_items_by_month = year_items | sort: "month", "first" | reverse %}
      {% assign sections_raw = year_items_by_month | map: "section" | compact %}
      {% assign sections = sections_raw | uniq %}
      {%- if sections.size == 0 -%}
        {% assign sections = "Other" | split: "," %}
      {%- endif -%}

      <!-- Section loop -->
      {%- for s in sections -%}
        {% assign section_items = year_items | where: "section", s %}

        {%- if section_items.size == 0 and s == "Other" -%}
          {% assign section_items = year_items | where_exp: "it", "it.section == nil or it.section == ''" %}
        {%- endif -%}

        {%- if section_items.size > 0 -%}
          {%- assign sid = s | slugify -%}
          <a class="anchor" id="y{{ y }}-{{ sid }}"></a>
          <h3 class="mt-3 mb-2">{{ s }}</h3>

          <div class="gallery-justified" data-gallery-justified>
            {%- for item in section_items -%}
              {%- assign img_path = item.path -%}
              {%- assign caption = item.caption | default: "" -%}
              {%- assign alt = item.alt | default: caption | default: "Gallery image" -%}
              {%- assign w = item.width | default: 4 -%}
              {%- assign h = item.height | default: 3 -%}
              {%- assign ar = w | times: 1.0 | divided_by: h | round: 4 -%}

              <figure class="gallery-tile gj-item" style="--ar: {{ ar }}">
                <a class="gallery-link" href="{{ img_path | relative_url }}" target="_blank" rel="noopener">
                  <img
                    class="gallery-img"
                    src="{{ img_path | relative_url }}"
                    alt="{{ alt }}"
                    {% if item.width %}width="{{ item.width }}" height="{{ item.height }}"{% endif %}
                    loading="lazy"
                  />
                </a>

                {%- if caption != "" -%}
                  <figcaption class="gallery-caption">{{ caption }}</figcaption>
                {%- endif -%}
              </figure>
            {%- endfor -%}
          </div>
        {%- endif -%}
      {%- endfor -%}
    {%- endfor -%}

  </main>
</div>

<script>
  // Justified gallery: every row fills the width, all photos in a row share one height,
  // and each photo keeps its own aspect ratio (no cropping of portraits or landscapes).
  (function () {
    var GAP = 12;

    // Split aspect ratios into k rows with sums as even as possible (linear partition).
    function partition(ar, k) {
      var n = ar.length;
      if (k >= n) return ar.map(function () { return 1; });
      var pre = [0];
      for (var i = 0; i < n; i++) pre.push(pre[i] + ar[i]);
      var target = pre[n] / k, INF = 1e18, dp = [], cut = [];
      for (var r = 0; r <= k; r++) { dp.push(new Array(n + 1).fill(INF)); cut.push(new Array(n + 1).fill(0)); }
      dp[0][0] = 0;
      for (r = 1; r <= k; r++)
        for (var j = r; j <= n; j++)
          for (i = r - 1; i < j; i++) {
            var d = pre[j] - pre[i] - target, c = dp[r - 1][i] + d * d;
            if (c < dp[r][j]) { dp[r][j] = c; cut[r][j] = i; }
          }
      var rows = [], end = n;
      for (r = k; r > 0; r--) { rows.unshift(end - cut[r][end]); end = cut[r][end]; }
      return rows;
    }

    function layout(sec) {
      var items = Array.prototype.slice.call(sec.querySelectorAll(".gj-item"));
      var W = Math.floor(sec.getBoundingClientRect().width);
      if (!items.length || !W) return;
      var small = W < 576;
      var targetH = small ? 150 : 230, minH = small ? 120 : 140, maxH = small ? 280 : 360;
      var ar = items.map(function (el) { return parseFloat(el.style.getPropertyValue("--ar")) || 1.3333; });
      var total = ar.reduce(function (a, b) { return a + b; }, 0);
      var k = Math.min(items.length, Math.max(1, Math.round((total * targetH) / W)));
      // Add rows if photos would get too short (e.g. several photos on a phone).
      while (k < items.length && (W - GAP * (items.length / k - 1)) / (total / k) < minH) k++;
      var idx = 0;
      partition(ar, k).forEach(function (len) {
        var rowAr = ar.slice(idx, idx + len);
        var sum = rowAr.reduce(function (a, b) { return a + b; }, 0);
        var avail = W - GAP * (len - 1);
        var h = Math.min(avail / sum, maxH);
        var used = 0;
        rowAr.forEach(function (a, t) {
          var el = items[idx + t];
          var w = t === len - 1 && h < maxH ? avail - used : Math.floor(a * h);
          used += w;
          el.style.width = w + "px";
          el.style.marginRight = "";
          el.querySelector(".gallery-img").style.height = Math.round(h) + "px";
          // A capped (short) row: pad the end so the next photo starts a new row.
          if (t === len - 1 && h >= maxH) el.style.marginRight = Math.max(0, avail - used) + "px";
        });
        idx += len;
      });
      sec.classList.add("gj-ready");
    }

    function init() {
      var secs = document.querySelectorAll("[data-gallery-justified]");
      Array.prototype.forEach.call(secs, function (sec) {
        layout(sec);
        if (window.ResizeObserver) {
          var lastW = 0;
          new ResizeObserver(function () {
            var w = Math.floor(sec.getBoundingClientRect().width);
            if (w !== lastW) { lastW = w; layout(sec); }
          }).observe(sec);
        }
      });
    }

    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
    else init();
  })();
</script>
