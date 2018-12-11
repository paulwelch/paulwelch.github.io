---
title: "Kubernetes 101: Pod Won't Start? (Part 1)"
tags:
  - Kubernetes
  - Kubernetes101
  - Docker
  - Troubleshooting
---

### What do you do when your pod won't start?

There are a number of reasons why pods stall and never reach a running state. One common cause happens when the cluster lacks the resources required to run the pod.

<!--more-->
When a pod stalls, you'll see its status is `Pending` as with `gpu-pod2` in the following example. In the example, the cluster has 4 GPU's. The pod is requesting 2 for itself, but 3 are already allocated to another running pod.

``` shell
> kubectl get pods
NAME                                                   READY   STATUS      RESTARTS   AGE
gpu-pod2                                               0/1     Pending     0          48s
gpu-pod3                                               1/1     Running     0          51s
nginx-ingress-kubernetes-worker-cpu-controller-54q9t   1/1     Running     1          13d
nginx-ingress-kubernetes-worker-cpu-controller-82cx4   1/1     Running     0          12d
nginx-ingress-kubernetes-worker-cpu-controller-g7ch4   1/1     Running     0          13d
nginx-ingress-kubernetes-worker-gpu-controller-zgp8j   1/1     Running     2          12d
wordpress-796698694f-ks46t                             1/1     Running     0          12d
wordpress-mysql-6bb7b7f95d-vtfl9                       1/1     Running     0          12d
```

Pods always start in `Pending` status. So if you look immediately after creation, it may just still be initializing. But if it's still in `Pending` after a reasonable amount of time, you may want to dig deeper.

The first thing I usually look at is the details of the pod. You can see these with the `kubectl describe` command. Towards the end, look in the `Events` section for clues.

In this example, you'll see a `FailedScheduling` warning with the answer. The warning message says the pod is requesting a `nvidia.com/gpu` resource that's not available in the cluster.

``` shell
> kubectl describe pod gpu-pod2
```

``` yaml
Name:         gpu-pod2
Namespace:    default
Node:         <none>
Labels:       <none>
Annotations:  kubectl.kubernetes.io/last-applied-configuration:
                {"apiVersion":"v1","kind":"Pod","metadata":{"annotations":{},"name":"gpu-pod2","namespace":"default"},"spec":{"containers":[{"image":"nvcr....
Status:       Pending
IP:
Containers:
  digits-container:
    Image:      nvcr.io/nvidia/digits:18.11-tensorflow
    Port:       5000/TCP
    Host Port:  0/TCP
    Limits:
      nvidia.com/gpu:  2
    Requests:
      nvidia.com/gpu:  2
    Environment:       <none>
    Mounts:
      /var/run/secrets/kubernetes.io/serviceaccount from default-token-846r6 (ro)
Conditions:
  Type           Status
  PodScheduled   False
Volumes:
  default-token-846r6:
    Type:        Secret (a volume populated by a Secret)
    SecretName:  default-token-846r6
    Optional:    false
QoS Class:       BestEffort
Node-Selectors:  <none>
Tolerations:     node.kubernetes.io/not-ready:NoExecute for 300s
                 node.kubernetes.io/unreachable:NoExecute for 300s
Events:
  Type     Reason            Age                From               Message
  ----     ------            ----               ----               -------
  Warning  FailedScheduling  6s (x25 over 64s)  default-scheduler  0/4 nodes are available: 4 Insufficient nvidia.com/gpu.
```

Another resource that's frequently not available is storage. Many pods need a volume for persistent storage. But, unless a cluster is configured with a default StorageClass, a persistent volume claim (pvc) must be pre-allocated for the pod. That could be the topic of a future post. But for now, here's the warning message in an example pod where the pvc named `missing-pvc` doesn't exist.

``` shell
> kubectl describe pod missing-pvc-example
```

``` yaml
.
.
.
Events:
  Type     Reason            Age                From               Message
  ----     ------            ----               ----               -------
  Warning  FailedScheduling  0s (x20 over 45s)  default-scheduler  persistentvolumeclaim "missing-pvc" not found
```

Other resource types can also be the culprit. For example if the cluster is heavily used or your pod requests a large amount, the available `CPU` or `Memory` resources may be insufficient. The `Event` warning message should make it clear which resource is needed.

#### Conclusion

When your pod fails to start, don't panic. There are many reasons that could be causing it to stall and most are fairly easy to troubleshoot. Don't forget to check the Event messages first to see if it's simply a lack of resources.
