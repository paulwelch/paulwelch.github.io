---
title: "Bringing kubestate Back to Life"
tags:
  - Kubernetes
  - Go
  - Open Source
  - DevOps
---

A few years ago I built [kubestate](https://github.com/paulwelch/kubestate), a small CLI tool that surfaces Kubernetes cluster state metrics at the command line. The idea was simple: most people use kube-state-metrics as a Prometheus data source, but sometimes you just want to ask a quick question about your cluster without standing up a full monitoring stack. It worked well enough — until it didn't.

<!--more-->

### The problem with "good enough"

Software has a shelf life, and kubestate had been sitting untouched since 2019. The Go ecosystem moves quickly. The Kubernetes client library moves even faster. After a few years, the project was effectively frozen in time:

- It used **Glide** for dependency management, which has long since been superseded by Go modules
- The `urfave/cli` dependency was on v1, while v2 had shipped with a meaningfully different API
- Calls into `client-go` were using deprecated function signatures that no longer compiled cleanly against modern versions
- The `watch` command existed in the help output but was never actually implemented
- TLS verification was hardcoded in a way that made it unusable in environments with self-signed certificates

The project wasn't broken in a catastrophic way — it just accumulated enough drift from the ecosystem that it would have taken someone a real effort to build it from scratch. That's the kind of technical debt that quietly kills open source projects.

### Modernizing the foundation

The first step was migrating away from Glide. This meant deleting `glide.yaml`, `glide.lock`, and the entire vendored dependency tree, and replacing it with a proper `go.mod` and `go.sum`. With Go modules, dependency versions are explicit, reproducible, and auditable — which matters both for security and for the long-term health of the project.

With the module system in place, bumping `client-go` and `urfave/cli` to current versions became straightforward. The CLI migration from v1 to v2 required updating how commands and flags are wired — flag access moved from positional arguments to typed methods on the context object — but the logic underneath stayed intact.

### Fixing what was broken

Modern `client-go` requires a `context.Context` to be passed through most API calls, reflecting the broader Go ecosystem shift toward explicit cancellation and timeout propagation. Updating those call sites was mechanical but important — it's the kind of change that makes the code behave correctly under load and gives operators a proper way to interrupt long-running requests.

The raw-metric filtering logic got a cleanup pass too. A handful of edge cases in the aggregation code could produce panics when a node returned incomplete data — not common, but the kind of thing that turns a useful debugging tool into an unreliable one. Adding explicit nil checks and extracting the filtering into reusable helpers makes the behavior predictable.

### Implementing what was promised

The `watch` command was wired up in the help text but never actually built. That's now fixed. It polls on a configurable interval (`--interval`), supports the same output formats as the other commands, and handles `Ctrl+C` cleanly via signal interception. Small thing, but it makes the tool feel complete.

Two operational improvements that turned out to matter more than expected:

**`--insecure-skip-tls-verify`** — Many real-world Kubernetes environments (dev clusters, airgapped installs, homelab setups) use self-signed certificates. Without a way to skip TLS verification, kubestate simply wouldn't connect. This flag brings it in line with what `kubectl` has supported for years.

**`--metrics-namespace` and service auto-discovery** — The original code assumed kube-state-metrics was always installed in `kube-system`. That's the default, but it's not universal. The tool now accepts a namespace parameter and will attempt to discover the service automatically if no explicit endpoint is provided.

### Quality gates

The project now has a CI workflow that runs `go test ./...`, `go vet ./...`, and `go build ./...` on every push. There are unit tests covering the filtering and output validation logic. Neither of those things existed before.

It's worth being honest about why: the original version was built quickly to scratch a personal itch, and tests felt like overhead for something so small. That calculus shifts once other people might depend on it, or once you come back to it after a long gap and need to refactor with confidence. Tests are documentation that executes.

### One remaining issue

After all the fixes, there's still one runtime problem worth mentioning: in some cluster configurations, kubestate returns `no endpoints available for service "kube-state-metrics"` even when the service exists. This turns out to be a service/endpoints wiring issue rather than anything in kubestate itself — the original namespace hardcoding bug masked it. The fix is straightforward on the cluster side, but it's worth knowing about if you hit it.

### What's next

kubestate is a small tool, and it doesn't need to be much more than what it is. A few things I may add over time:

- Support for kubeconfig contexts, so you can query multiple clusters without changing your active context
- Better output formatting for wide terminals
- A watch mode that highlights values that changed since the last poll

The updated release is on [GitHub](https://github.com/paulwelch/kubestate). If you're using kube-state-metrics and want a quick way to explore its data without a Prometheus setup, give it a try.
