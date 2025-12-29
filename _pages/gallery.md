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
Data source: _data/gallery.yml
Each item:
- year: 2025
  section: "Field test – Tifton"
  path: assets/img/gallery/2025/field_test_01.jpg
  caption: "UGA/Tifton field test – Husky + UR5e setup"
  alt: "Robot setup in field" (optional)
{% endcomment %}

<div class="projects">
  <!-- <p class="text-muted">
    Browse images grouped by <b>year</b> and <b>section</b>. Click an image to open full size.
  </p> -->

  {% assign years = site.data.gallery | map: "year" | uniq | sort | reverse %}

  {%- if years.size == 0 -%}
    <div class="alert alert-warning">
      <b>No gallery data found.</b><br>
      Create <code>_data/gallery.yml</code> and add entries.
    </div>
  {%- endif -%}

  <!-- Jump links -->
  {%- if years.size > 0 -%}
    <div class="gallery-jump">
      <span class="gallery-jump-label">Jump to:</span>
      {%- for y in years -%}
        <a href="#y{{ y }}" class="gallery-jump-link">{{ y }}</a>{% unless forloop.last %}&nbsp;&nbsp;•&nbsp;&nbsp;{% endunless %}
      {%- endfor -%}
    </div>
  {%- endif -%}


  <!-- Year loop -->
  {%- for y in years -%}
    <a id="y{{ y }}" href=".#y{{ y }}">
      <h2 class="category">{{ y }}</h2>
    </a>

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
</div>
