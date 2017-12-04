---
title:  Running TensorFlow Models (Part 1)
tags:
  - Machine Learning
  - TensorFlow
  - Docker
---

So you've trained your TensorFlow ML model, now what?  *(Part 1)*

To show how to run it, I'll use an open source pre-trained model, specifically [Inception V3](https://github.com/tensorflow/models/tree/master/research/inception){:target="_blank"}. Inception was developed at Google and won the ILSVRC 2014 image classification competition. Plus, it's a fun model to play around with.

<!--more-->

First, you'll need a way to call the model. That's what TensorFlow [Serving](https://www.tensorflow.org/serving/){:target="_blank"} is all about. Serving provides a way to deploy your model so other applications can use it.  It takes a saved version of the model, a training checkpoint, and represents it as a "Servable" that can be exposed as a [gRPC](https://grpc.io/){:target="_blank"} endpoint. An example of starting the Serving endpoint on port `9000` using the Inception checkpoint at `/serving/inception-export`:

~~~ terminal
» tensorflow_model_server --port=9000 --model_name=inception --model_base_path=/serving/inception-export
~~~

Next, you'll need somewhere to run it. Package the compiled Serving binaries and the Inception model in a Docker image. The image should be configured to run the Serving process on startup, so it's immediately able to accept requests. You can follow the very good TensorFlow [tutorial](https://www.tensorflow.org/serving/serving_inception){:target="_blank"} to build the image from scratch.  Or, just use my [image](https://hub.docker.com/r/paulwelch/tensorflow-serving-inception/){:target="_blank"}, created following the same steps.

The Docker image can be run on any Docker server, even locally on your laptop. For example, start the Serving model server and find the CONTAINER ID value:

~~~ terminal
» docker run -d --rm index.docker.io/paulwelch/tensorflow-serving-inception /bin/sh -c 'tensorflow_model_server --port=9000 --model_name=inception --model_base_path=/serving/inception-export'
d7e0d1378f3527c1d97164d8f7c5bd8a900393978d3895645c8d37cb52997f7f

» docker ps
CONTAINER ID        IMAGE                                    COMMAND                  CREATED             STATUS              PORTS               NAMES
d7e0d1378f35        paulwelch/tensorflow-serving-inception   "/bin/sh -c 'tensorf…"   4 seconds ago       Up 8 seconds                            fervent_pasteur
~~~

Using the CONTAINER ID, copy an example image to the container instance. Connect to the instance with a new shell and run the [inception_client](https://github.com/tensorflow/serving/tree/master/tensorflow_serving/example/inception_client.py){:target="_blank"}. Pass the local server:port and image file parameters as appropriate and the classification results should be output to the console.

~~~ terminal
» docker cp ~/local/path/to/cat.png d7e0d1378f35:/serving/cat.png
» docker exec -it d7e0d1378f35 /bin/sh
# /serving/bazel-bin/tensorflow_serving/example/inception_client --server=localhost:9000 --image=/serving/cat.png
~~~

As you can see in my output, the Top-5 guesses were pretty good. "plastic bag" is a little suspect. But the top 3 were spot on.

~~~ jsonnet
outputs {
  key: "classes"
  value {
    dtype: DT_STRING
    tensor_shape {
      dim {
        size: 1
      }
      dim {
        size: 5
      }
    }
    string_val: "tabby, tabby cat"
    string_val: "tiger cat"
    string_val: "Egyptian cat"
    string_val: "plastic bag"
    string_val: "lynx, catamount"
  }
}
outputs {
  key: "scores"
  value {
    dtype: DT_FLOAT
    tensor_shape {
      dim {
        size: 1
      }
      dim {
        size: 5
      }
    }
    float_val: 9.66426753998
    float_val: 9.57033252716
    float_val: 6.46347570419
    float_val: 4.13882112503
    float_val: 3.52212190628
  }
}
~~~

Next time, I'll show how to run our classification service in Kubernetes for better scalability and manageability.
