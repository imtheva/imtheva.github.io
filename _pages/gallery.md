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

            {%- assign year_items_for_nav = site.data.gallery | where: "year", y -%}
            {%- assign sections_for_nav = year_items_for_nav | map: "section" | compact | uniq | sort -%}
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
      {% assign sections_raw = year_items | map: "section" | compact %}
      {% assign sections = sections_raw | uniq | sort %}
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

          <div class="row row-cols-1 row-cols-sm-2 row-cols-md-3 g-3 mb-4">
            {%- for item in section_items -%}
              {%- assign img_path = item.path -%}
              {%- assign caption = item.caption | default: "" -%}
              {%- assign alt = item.alt | default: caption | default: "Gallery image" -%}

              <div class="col">
                <div class="gallery-tile">
                  <a class="gallery-link" href="{{ img_path | relative_url }}" target="_blank" rel="noopener">
                    <img
                      class="gallery-img"
                      src="{{ img_path | relative_url }}"
                      alt="{{ alt }}"
                      loading="lazy"
                    />
                  </a>

                  {%- if caption != "" -%}
                    <div class="gallery-caption">{{ caption }}</div>
                  {%- endif -%}
                </div>
              </div>
            {%- endfor -%}
          </div>
        {%- endif -%}
      {%- endfor -%}
    {%- endfor -%}

  </main>
</div>
