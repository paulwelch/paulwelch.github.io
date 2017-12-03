---
title: Projects
narrow: true
permalink: projects
show_profile: true
---

{% for project in site.projects %}
- [{{ project.title }}]({{ project.repo }})
{% endfor %}
