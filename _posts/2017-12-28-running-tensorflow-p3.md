---
title:  Running TensorFlow Models (Part 3 - Using the model in other apps)
tags:
  - Machine Learning
  - TensorFlow
  - Kubernetes
  - Docker
  - Node.js
  - Single Page App (SPA)
  - Microservices
---

So you've trained your TensorFlow ML model, now what?  *(Part 3 - Using the model in other apps)*

The first two posts in the series showed how to [run a TensorFlow model](/2017/12/04/running-tensorflow-p1.html){:target="_blank"}, then how to [deploy it to Kubernetes](/2017/12/07/running-tensorflow-p2.html){:target="_blank"}. Now that our image classification service is managed by a scheduler and scaled dynamically, the next step is to start using it. In this post, we'll walk through an example Node.js single page app (SPA) that calls the service and displays the classification results.

<!--more-->
The demo web page shown below is very simple with practically no formatting. It's purpose is only to show how to call our image classification service. But, the layout and styles could easily be styled by a web designer for a nicer look and feel. It has one input field that takes an image URL. Where the Python script we used in Part 1 would be very useful for processing a folder full of image files, this Node.js page is a better example for an image portfolio or e-commerce website that processes user uploaded images.

![Inception Demo UI Input](/blog/images/running-tensorflow-images/Inception_UI_Input.png "Inception Demo UI Input"){:style="border: 1px solid black"}


When the Classify button is clicked, the magic happens in [server.js](https://github.com/paulwelch/tensorflow-kubernetes/blob/master/nodejs-inception-demo/server.js){:target="_blank"}. The `classify()` function downloads the image at the given URL, encodes it into a Base64 string and passes it in the request to the service endpoint. An example of the YAML structure for the request is below. The `model_spec` values tell Serving which model to use and `inputs` must map to the signature for that model when it was exported.

Example of YAML Request
``` yaml
model_spec: { name: 'inception', signature_name: 'predict_images' },
inputs: {
  images: {
    dtype: 'DT_STRING',
    tensor_shape: {
      dim: {
        size: # <<Length of Image Data>>
      }
    },
    string_val: # <<Image Data as Base64 Encoded String>>
  }
}
}
```

Once a service client is instantiated, making a prediction is simple. It's done by calling the `predict()` function passing in the request YAML described above and processing the results found in the response. I hard-coded the service endpoint to `inception-service:9000` for purposes of this demo. I'm targeting Kubernetes, which provides service discovery to resolve the address dynamically. Otherwise, I'd make it configurable.

``` javascript
var tensorflow_serving = grpc.load('proto/prediction_service.proto').tensorflow.serving;
var client = new tensorflow_serving.PredictionService(
  "inception-service:9000", grpc.credentials.createInsecure()
);
...
client.predict(msg, (err, response) => {
  ...
});
```
The prediction service sends back response `outputs` named `classes` and `scores`. Like the inputs, the outputs are also defined by the model when exported. Classes are the names of the top 5 category predictions. Their corresponding scores represent prediction confidence.

Example of YAML Response
``` yaml
Response: { outputs:
   { classes:
      { dtype: 'DT_STRING',
        tensor_shape:
         { dim: [ { size: '1', name: '' }, { size: '5', name: '' } ],
           unknown_rank: false },
        version_number: 0,
        tensor_content: <Buffer >,
        half_val: [],
        float_val: [],
        double_val: [],
        int_val: [],
        string_val:
         [ <Buffer 74 61 62 62 79 2c 20 74 61 62 62 79 20 63 61 74>,
           <Buffer 74 69 67 65 72 20 63 61 74>,
           <Buffer 45 67 79 70 74 69 61 6e 20 63 61 74>,
           <Buffer 77 61 72 64 72 6f 62 65 2c 20 63 6c 6f 73 65 74 2c 20 70 72 65 73 73>,
           <Buffer 64 6f 6f 72 6d 61 74 2c 20 77 65 6c 63 6f 6d 65 20 6d 61 74> ],
        scomplex_val: [],
        int64_val: [],
        bool_val: [],
        dcomplex_val: [],
        resource_handle_val: [] },
     scores:
      { dtype: 'DT_FLOAT',
        tensor_shape:
         { dim: [ { size: '1', name: '' }, { size: '5', name: '' } ],
           unknown_rank: false },
        version_number: 0,
        tensor_content: <Buffer >,
        half_val: [],
        float_val:
         [ 9.300559997558594,
           7.751873970031738,
           4.995975494384766,
           4.341161251068115,
           2.9982337951660156 ],
        double_val: [],
        int_val: [],
        string_val: [],
        scomplex_val: [],
        int64_val: [],
        bool_val: [],
        dcomplex_val: [],
        resource_handle_val: [] } } }
```

The prediction outputs are parsed and formatted for UI display. Scores are translated to percentages using the `softmax()` function.

``` javascript
var percents = softmax(scores);
```

Classes and percentages are returned to the demo page where they are displayed using hidden placeholder tags in the page. As a side note, this is what makes the demo UI a SPA. The page never navigates away to a new page. Instead, using the Node.js libraries Express and Socket.io, Javascript code calls from the page to the server, gets the results and dynamically updates the same page in place. That's probably a good topic for a future post on it's own.

![Inception Demo UI Results](/blog/images/running-tensorflow-images/Inception_UI_Results.png "Inception Demo UI Results"){:style="border: 1px solid black"}

One final piece. If you want to run the demo page in Kubernetes, you need to package it as a container. Or, you can just use my [image](https://hub.docker.com/r/paulwelch/image-classifier-ui/){:target="_blank"}, created following the same steps as this post.

To make your own image, use the [`docker build`](https://docs.docker.com/engine/reference/commandline/build){:target="_blank"} command with a `Dockerfile` such as the following example.

``` docker
FROM node:8.6-alpine

RUN apk --update add libc6-compat

WORKDIR /usr/src/classifier-ui

COPY package.json .
RUN npm install
COPY . .

EXPOSE 8080
CMD [ "npm", "start" ]
```

Then, push it to your favorite repo and deploy to Kubernetes in the same way we did with the service in [Part 2](/2017/12/07/running-tensorflow-p2){:target="_blank"}. An example Kubernetes deployment YAML for the demo UI can be found in the project [here](https://github.com/paulwelch/tensorflow-kubernetes/blob/master/nodejs-inception-demo/inception_ui_k8s.yaml){:target="_blank"}.

#### Conclusion
You now have your own private image classification service similar to [AWS Rekognition](https://aws.amazon.com/rekognition){:target="_blank"} or [Google Vision](https://cloud.google.com/vision){:target="_blank"}. But, it's one you can run on your own servers. I showed calling the service from a Python script in Part 1 and from a Node.js webpage in Part 3.  It can just as easily be used in apps written in any other [language that supports gRPC](https://grpc.io/docs/){:target="_blank"}. Some suggestions for where to take it next might include:

- Securing the TensorFlow Serving endpoint
- Deploying new versions and concurrent models
- Optimizations - let's face it, the 3GB Docker image you get with this procedure should go on a diet
- Training an additional category for the Inception model
- Training your own model from scratch

Those are all interesting topics that I might get back to at some point. But personally, I think there's a much more interesting and bigger problem domain looming on the horizon. That is, ways to improve the process from training through using the deployed model. Stay tuned.

Full source code for this series can be found on [GitHub here](https://github.com/paulwelch/tensorflow-kubernetes){:target="_blank"} with the demo UI in a subfolder named `nodejs-inception-demo`.
