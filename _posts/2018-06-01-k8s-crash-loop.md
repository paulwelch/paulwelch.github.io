---
title: "Kubernetes 101: Pod Won't Start? (Part 2)"
tags:
  - Kubernetes
  - Kubernetes101
  - Docker
  - Troubleshooting
---

### Is your pod crashing?

There are a number of reasons why pods fail to reach a running state. Missing required resources was covered in [Part 1](/2018/03/01/k8s-insufficient-resources){:target="_blank"}. Another scenario happens after the pod is successfully scheduled on a node. When the pod trys to start on its node and either crashes or exits unexpectedly, the `restartPolicy` field of the pods `PodSpec` determines what happens next. It may just fail and stop, if set to `Never`. Or if set to `Always`, which is the default, the pod could go into a never ending loop of exiting, trying again and exiting again... In this case its status will show as `CrashLoopBackOff`.

<!--more-->

I ran into an example of this when installing Rancher Labs very interesting distributed storage project called [Longhorn](https://github.com/rancher/longhorn){:target="_blank"} - that's a good topic for a future post on it's own. After installing Longhorn, I noticed the pods stuck in `CrasLoopBackOff` status.

``` shell
[centos@wrk1 ~]$ kubectl get pods -n longhorn-system
NAME                                        READY   STATUS             RESTARTS   AGE
longhorn-driver-deployer-69f889d6c7-5zcsf   0/1     Init:0/1           0          12h
longhorn-manager-5mc6p                      0/1     CrashLoopBackOff   149        12h
longhorn-manager-cp7xp                      0/1     CrashLoopBackOff   148        12h
longhorn-manager-jrw8x                      0/1     CrashLoopBackOff   149        12h
longhorn-manager-kwdjk                      0/1     CrashLoopBackOff   149        12h
longhorn-manager-r8qzz                      0/1     CrashLoopBackOff   148        12h
longhorn-manager-wq7z8                      0/1     CrashLoopBackOff   149        12h
longhorn-ui-789db56875-qqk7w                1/1     Running            0          12h
```


Investigating deeper, I found the cause in the pod logs. Longhorn requires the `open-iscsi` package to handle mounting volumes after they are provisioned. Makes sense.


``` shell
[centos@wrk1 ~]$ kubectl -n longhorn-system logs longhorn-manager-5mc6p
time="2019-01-03T13:19:29Z" level=error msg="Failed environment check, please make sure you have iscsiadm/open-iscsi installed on the host"
time="2019-01-03T13:19:29Z" level=fatal msg="Error starting manager: Environment check failed: Failed to execute: nsenter [--mount=/host/proc/1004/ns/mnt --net=/host/proc/1004/ns/net iscsiadm --version], output nsenter: failed to execute iscsiadm: No such file or directory\n, error exit status 1"
```

I installed the missing package `sudo yum -y install iscsi-initiator-utils` then deleted the pods. These Pods were started by a `DaemonSet` which means they will get recreated automatically. The new instances started, made it to `Running` status and the storage system was working.


``` shell
[centos@mgr1 ~]$ kubectl get pods -n longhorn-system
NAME                                        READY     STATUS    RESTARTS   AGE
engine-image-ei-3bda103d-4wm5v              1/1       Running   0          15m
engine-image-ei-3bda103d-72jh6              1/1       Running   0          15m
engine-image-ei-3bda103d-8c5qx              1/1       Running   0          15m
engine-image-ei-3bda103d-8l5ql              1/1       Running   0          15m
engine-image-ei-3bda103d-b48jx              1/1       Running   0          15m
engine-image-ei-3bda103d-fmkkr              1/1       Running   0          15m
longhorn-driver-deployer-69f889d6c7-gm28b   1/1       Running   0          15m
longhorn-flexvolume-driver-64ldd            1/1       Running   0          8m14s
longhorn-flexvolume-driver-8s2zf            1/1       Running   0          8m14s
longhorn-flexvolume-driver-9sz25            1/1       Running   0          8m14s
longhorn-flexvolume-driver-dqdnx            1/1       Running   0          8m14s
longhorn-flexvolume-driver-p7xv9            1/1       Running   0          8m14s
longhorn-flexvolume-driver-vjbz4            1/1       Running   0          8m14s
longhorn-manager-97fbv                      1/1       Running   0          6m27s
longhorn-manager-9ljbq                      1/1       Running   0          6m39s
longhorn-manager-bvdgc                      1/1       Running   0          6m53s
longhorn-manager-jrw8x                      1/1       Running   151        12h
longhorn-manager-mmwml                      1/1       Running   0          6m52s
longhorn-manager-zprn7                      1/1       Running   0          6m48s
longhorn-ui-789db56875-qqk7w                1/1       Running   0          12h
```


#### Conclusion
Many things can cause crash loops. It happens any time the containers process systemically exits and kubernetes is configured to restart it, causing a loop of start-stop crashes. Other examples include 

* A bug in the containers application
* Trying to use a port that's already being used
* Bad configuration
* Missing RBAC permissions for a cluster resource 
* Corrupted container image on the hosts disk
* Forgetting to configure the pod to run something after starting. 

Most of the time it's easy to fix once you track down the cause of the crash. Look at the pod logs, the error usually shows up there, then fix the cause and restart the pods.
