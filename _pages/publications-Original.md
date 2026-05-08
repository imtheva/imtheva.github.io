---
layout: page
permalink: /publications/
title: Publications
social: true # includes social icons at the bottom of the page
description: Publications including journal articles, conference papers, and book chapters, organized by category in reverse chronological order.

nav: true
nav_order: 2
---
{% include scholar_citations.html %}
{% include scholar_stats.html %}
<!-- _pages/publications.md -->

<!-- Bibsearch Feature -->

{% include bib_search.liquid %}

<div class="publications">

{% bibliography %}

</div>
