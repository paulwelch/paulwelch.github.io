---
title:  2018 - The Year of DevOps for Machine Learning
tags:
  - Machine Learning
  - DevOps
---

Happy New Year! I don't normally make predictions for the new year. But, this year I've had a lightbulb moment. It took me a while to make a connection between these two seemingly independent trends. I've been following and working with them for a long time. The foundations of both [DevOps](https://en.wikipedia.org/wiki/DevOps#Definitions_and_History){:target="_blank"} and [Machine Learning (ML)](https://en.wikipedia.org/wiki/Machine_learning#History_and_relationships_to_other_fields){:target="_blank"} go back decades. The hype around them lately is deafening. Yet, I haven't heard much about how well they go together. That's about to change...

<!--more-->

ML solutions are proliferating across more and more problem domains every day. They've become much more accessible, with maturing open source, commercial and cloud options. It's [on the radar for most enterprise CIO's](https://www.cio.com/article/3233310/cio-role/ai-and-machine-learning-are-forcing-cios-to-rethink-it-strategies.html){:target="_blank"}, even in traditionally late-adopting industries. And, [being there early gets you the largest competitive advantage](https://www.technologyreview.com/s/603872/machine-learning-the-new-proving-ground-for-competitive-advantage/){:target="_blank"}.

Here's the kicker -- ML is hard. I'm not referring to the deep math knowledge required to make a good model. Although finding talent with those skills can be tricky, instead I was thinking about what it takes to manage ML solutions at scale. Ok, maybe "hard" is a bit vague. More specifically compared to traditional apps, ML deployment and runtime requirements tend to be more complex and come with unique operational challenges, such as:

- Model development requires experimentation, with iterative training cycles that can take days or weeks to show how the model is performing. Modern development practices and tools are designed for fast compile-package-test iterations, not long running workflows.
- ML frameworks, models and training datasets do not always integrate well with version control, testing or automation tools.
- Changes at integration points and dependent data feeds will cause problems if you're missing a versioning strategy with backwards compatibility.
- As with my post on [running a TensorFlow model](/2017/12/04/running-tensorflow-p1){:target="_blank"}, deploying the trained model starts to resemble a traditional app deployment. There are some unique twists, however. For example, how do you tell if the ML is working, i.e. producing good classifications or predictions?
- ML frameworks tend to have heavy dependencies on configuration, external libraries and runtime environment, which can make deployments complex and lengthy. Done manually, this introduces additional risk and longer recovery times. This also makes the hand-off from ML developers to the operations team harder.
- All of the frameworks I've dug into so far are fairly monolithic, which comes with it's own [architecture and deployment trade-offs](https://martinfowler.com/articles/microservice-trade-offs.html){:target="_blank"}.
- Monitoring, alerting and troubleshooting must be more comprehensive and context-aware than with traditional systems management. For example, a root cause to "poor" model predictions could end up being data quality rather than environmental performance or code defects.
- As of when I'm writing this, there's practically no guidance or best practices available to follow.

Many of these will get easier over time, as processes and tools mature. Thinking about the challenges is when my lightbulb turned on. DevOps was created to address challenges like these for developing traditional apps. Couldn't DevOps could bring similar benefits to the ML workflow?

A few examples bringing the two together might include adopting automation tools at every layer in the stack, incorporating agile processes [with a DevOps friendly team structure](http://web.devopstopologies.com/#team-topologies){:target="_blank"} and incorporating [12-Factor App principals](https://12factor.net/){:target="_blank"}. I'd expect the benefits to be similar to what they have been for adopting DevOps with traditional apps. For example:

- Automation for model development (experimentation) iterations would make the workflow more repeatable and reduce failed iterations caused by human error.
- Automating production releases would increase release cycles and improve quality, in addition to making it much easier to recover from a failed release.
- Finding ways to creatively incorporate version control for model definitions and training data should lead to easier traceability and troubleshooting.
- Reducing the unit of deployment, or the size and scope of a release package, would make releases less complex and faster. This can also make it easier for new team members to get up to speed with the product codebase.
- Unit and integration tests are challenging due to the inherent fuzziness of ML. As mentioned above, how would you know if the model is giving "good" predictions? For that matter, what does "good" mean? But, solving this dilemma and automating it is essential to ensuring high quality releases.
- Operations considerations such as team structure, support processes, monitoring & alerting tools, logging strategy and general [site reliability principals](https://landing.google.com/sre/book.html){:target="_blank"} are still critical. Just because this is an AI problem doesn't mean it will operate itself.

Hopefully by now, you've bought in to my prediction. It seems obvious to me now. The market demand for ML solutions, combined with their complexity and lack of maturity will demand DevOps. In 2018 we should see a flurry of DevOps tooling integration, process methodology and cultural impact targeting the world of Machine Learning.

Sounds great, right? But, where do you start?

As with DevOps in general, I like to suggest starting simple and making incremental improvements. Find one thing that can be done quickly, then build on it. Some of DevOps can be applied to ML in exactly the same way as other apps. Watch for new approaches and features and adopt as makes sense. Also, follow my blog. I plan to spend some time this year exploring DevOps for Machine Learning.
