---
layout: defaults/page
permalink: index.html
narrow: true
---

[More about me]({{ site.baseurl}}{% link _pages/about.md %})

## Projects

I have a few open source projects on github. My disclaimer - _I don't recommend using them for production systems unless you fully understand the code and are prepared to support them yourself_. That said... if you see something you like, decide to use or would like to collaborate on, please let me know. [Projects here]({{ site.baseurl }}{% link projects/projects.md %})


## Recent Posts

{% for post in site.posts limit:3 %}
{% include components/post-card.html %}
{% endfor %}
