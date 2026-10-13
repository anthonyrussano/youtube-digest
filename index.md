---
layout: default
title: Reports
---
A daily roundup of the latest AI and DevOps news, reported from new videos on the channels I follow. Each article cites and deep-links the videos it draws on.

{% assign reports = site.pages | where_exp: "p", "p.path contains 'reports/'" | sort: "date" | reverse %}
<ul class="report-list">
{% for r in reports %}
  <li><span class="d">{{ r.date | date: "%B %-d, %Y" }}</span><br>
  <a href="{{ r.url | relative_url }}"><strong>{{ r.title }}</strong></a><br>
  {{ r.dek }}</li>
{% endfor %}
</ul>
