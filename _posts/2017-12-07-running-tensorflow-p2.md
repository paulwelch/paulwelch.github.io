---
title:  Running TensorFlow Models (Part 2 - Deploying to Kubernetes)
tags:
  - Machine Learning
  - TensorFlow
  - Kubernetes
  - Docker
---

So you've trained your TensorFlow ML model, now what?  *(Part 2 - Deploying to Kubernetes)*

[Part 1](/2017/12/04/running-tensorflow-p1){:target="_blank"} showed how to run the open source pre-trained model [Inception V3](https://github.com/tensorflow/models/tree/master/research/inception){:target="_blank"} as an image classification service. That's all you need to do for a single classification instance, whether you run it on a server, your laptop or even a smart IoT device. But, what if you need to scale to handle a high volume of concurrent requests or you want multiple instances for resilency? For that, you'll want to [scale horizaontally](https://en.wikipedia.org/wiki/Scalability#Horizontal_and_vertical_scaling){:target="_blank"} with many instances. Then, a cluster managed by a resource scheduler like Kubernetes is a great way to go. Not only does it help with scalability, but it also enables deployment automation, improves manageability and will most likely result in better infrastructure utilization.

<!--more-->

Running the classification service in Kubernetes is pretty straightforward once you have the Docker image. It only requires one more step, creating a Kubernetes Deployment. You define the Deployment in a YAML file, such as the one below.

~~~ yaml
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: inception-deployment
spec:
  replicas: 1
  template:
    metadata:
      labels:
        app: inception-server
    spec:
      containers:
      - name: inception-container
        image: index.docker.io/paulwelch/tensorflow-serving-inception
        command:
        - /bin/sh
        - -c
        args:
        - tensorflow_model_server
          --port=9000 --model_name=inception --model_base_path=/serving/inception-export
        ports:
        - containerPort: 9000
~~~

My Deployment starts an instance listening on port `9000`. Note the nested keys of `containers` that define the `image`, as well as the `command` and `args` to run when the instance starts. These correspond to the command line parameters we used with `docker run` in Part 1.

Copy the YAML to a file `inception_serving_k8s.yaml`. Assuming you have the Kubernetes cli tool `kubectl` configured to talk to your cluster, it can be applied as follows:

~~~ terminal
» kubectl apply -f inception_serving_k8s.yaml
~~~

You can see the Deployment status with the following command:

~~~ terminal
» kubectl get deployments
NAME                      DESIRED   CURRENT   UP-TO-DATE   AVAILABLE   AGE
inception-deployment      1         1         1            1           42s
~~~

The group of containers started by the Deployment is called a Pod, which you can see with this command:

~~~ terminal
» kubectl get pods
NAME                                      READY     STATUS    RESTARTS   AGE
inception-deployment-57553967-36l4k       1/1       Running   0          42s
~~~

Now an instance of the service is running. You could run the inception_client in the instance, just as in Part 1. But, we want to run more instances to handle the high request volume. And, we'll need a way to distribute the volume across all of the instances. Kubernetes makes this pretty trivial as well.  In the YAML file, simply change the `replicas` key from `1` to the count you want and re-run the `kubectl apply` as above.  

You may also want to provide connectivity to the service endpoint. A simple way is to add a [`Service`](https://kubernetes.io/docs/concepts/services-networking/service/){:target="_blank"} definition to the Deployment. The Service defines an endpoint for the Pod.

Note the `type` key. As of the current release, if you're running in a supported Cloud Provider you can specify a Service type of `LoadBalancer` and it will auto-allocate a load balanced IP that is accessible outside the cluster with all instance endpoints in its pool. The load balancer implementation is specific to the Cloud Provider, such as ELB on AWS.

The LoadBalancer type won't be available if you're running on a platform that doesn't have a Cloud Provider, like my bare metal dev environment. In this case, you'll need to use another type such as `NodePort`. The NodePort type allocates a port for each instance and makes it discoverable inside the cluster. But you'll need to bring your own load balancer to distribute the requests and expose the IP outside the cluster. The good news is that there are several Kubernetes integrated open source load balancers available, such as the excellent [Traefik Project](https://traefik.io/){:target="_blank"}.

The full YAML updates are shown in the example below to scale out to 3 instances and add a Service.

~~~ yaml
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: inception-deployment
spec:
  replicas: 3
  template:
    metadata:
      labels:
        app: inception-server
    spec:
      containers:
      - name: inception-container
        image: index.docker.io/paulwelch/tensorflow-serving-inception
        command:
        - /bin/sh
        - -c
        args:
        - tensorflow_model_server
          --port=9000 --model_name=inception --model_base_path=/serving/inception-export
        ports:
        - containerPort: 9000
---
apiVersion: v1
kind: Service
metadata:
  labels:
    run: inception-service
  name: inception-service
spec:
  ports:
  - port: 9000
    targetPort: 9000
  selector:
    app: inception-server
  type: NodePort
~~~

Apply the changes with `kubectl apply`, as follows.

~~~ terminal
» kubectl apply -f inception_serving_k8s.yaml
~~~

Then you can see the changes with the `kubectl get pods` and `kubectl get services` commands. If you applied a `replicas` value to 3, you should see 3 instances listed. One great thing about running in Kubernetes is the value could just as easily be 30 or 300, as long as there are sufficient resources to run them.

~~~ terminal
» kubectl get pods
NAME                                      READY     STATUS    RESTARTS   AGE
inception-deployment-57553967-36l4k       1/1       Running   0          28m
inception-deployment-57553967-8228b       1/1       Running   0          42s
inception-deployment-57553967-nr087       1/1       Running   0          3s
~~~

~~~ terminal
» kubectl get services
NAME                      TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)                         AGE
inception-service         NodePort    10.3.50.102    <none>        9000:32027/TCP                  28s
traefik-ingress-service   NodePort    10.3.106.173   <none>        8888:32720/TCP,8080:30569/TCP   65d
~~~

At this point, you have 3 instances running. I've also added a Traefik load balancer to provide the load balanced endpoint accessible outside the cluster. Rolling your own load balancer may be a good topic for a future post.

To sum it up, a few of the benefits of using Kubernetes to run our classification service:

* **Scalability** - It enables a load balanced pool of instances to handle a high volume of concurrent requests.
* **Self-Healing** - Kubernetes keeps the instance count fixed at your configured value. For example if an instance unexpectedly dies, Kubernetes will automatically start a new one to replace it.
* **Auto-Scaling** - You can dynamically scale the instances in or out to handle the required load by applying a new `replicas` config value. Changing the scale is easily initiated by an external system, such as a monitoring system that could make changes based on CPU utilization, the depth of some queue or another metric.
* **Optimized Utilization** - Infrastructure resources in the cluster are used efficiently, both because they are shared across all pods and also by dynamically scaling deployments to use only the resources they need at the time. Also, compared to virtual machines, resources are not hard allocated per container instance which may be a another good topic for a future post.

The service is shaping up pretty well so far. In the [next part](/2017/12/28/running-tensorflow-p3.html){:target="_blank"}, I'll take a look at using the service from another application separately deployed in the cluster.
