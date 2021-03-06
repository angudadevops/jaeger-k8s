# Jaeger for K8s

Jaeger Example for Kubernetes cluster with Go Web Application. This document help you to understand how you can setup jaeger and deploy an Application and trace it using Jaeger.

## Prerequisites 
- Kubernetes Cluster
- Helm

`NOTE:` If you don't have kubernetes cluster with Helm, please refer [SingleNode K8s Cluster](https://github.com/angudadevops/singlenode_kubernetes.git)

## Jaeger Installation

Run the below command to install the Jaeger Operator on Kubernetes Cluster
```
$ helm repo add jaegertracing https://jaegertracing.github.io/helm-charts

$ helm install --name my-release jaegertracing/jaeger-operator
```

## Initiate Jaeger Instance

Please run below command to intitiate the jaeger all in one instance using Jaeger custom resource

```
echo "
apiVersion: jaegertracing.io/v1
kind: Jaeger
metadata:
  name: jaeger-service" | kubectl create -f -
```

To access Jaeger UI from host machine expose Jaeger UI service as per below
```
$ kubectl patch svc jaeger-service-query -p '{"spec":{"type":"NodePort"}}'

$ kubectl patch svc jaeger-service-query -p '{"spec":{"ports":[{"name":"http-query", "nodePort": 32000, "port": 16686}]}}'
```

Run the below command to Jaeger WebUI URL

```
export JAEGERPORT=$(kubectl get svc jaeger-service-query -o jsonpath='{.spec.ports[0].nodePort}')
export NODE_IP=$(kubectl get nodes --namespace default -o jsonpath="{.items[0].status.addresses[0].address}")

echo http://$NODE_IP:$JAEGERPORT
```

## Deploy an Application with Jaeger 

First you need include Jaeger tracing in your application to trace the logs on Jaeger. Please refer [Jaeger libraries](https://github.com/jaegertracing/jaeger#instrumentation-libraries)

Run the below command to deploy python application which is already include jaeger tracing
```
$ git clone https://github.com/angudadevops/jaeger-k8s.git

$ kubectl apply -f jaeger-k8s/golang/app-deployment.yaml
```

`NOTE:` If you have a Go Web App, you just need add the below template to the end of the file. Refer [Jaeger Go Libraries](https://github.com/jaegertracing/jaeger-client-go)
```
func main() {
    jaegerHost := os.Getenv("JAEGER_AGENT_HOST")
    fmt.Println(jaegerHost)
    cfg := config.Configuration{
    Sampler: &config.SamplerConfig{
        Type:  "const",
        Param: 1,
    },
    Reporter: &config.ReporterConfig{
        LogSpans:            true,
        BufferFlushInterval: 1 * time.Second,
        LocalAgentHostPort: jaegerHost,
    },
    }
    tracer, closer, err := cfg.New(
        jaegerServiceName,
        config.Logger(jaeger.StdLogger),
    )
    if err != nil {
            fmt.Printf("No Jaeger service")
    }
    opentracing.SetGlobalTracer(tracer)
    defer closer.Close()

    http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
	spanCtx, _ := tracer.Extract(opentracing.HTTPHeaders, opentracing.HTTPHeadersCarrier(r.Header))
        serverSpan := tracer.StartSpan("go-webapp", ext.RPCServerOption(spanCtx))
        defer serverSpan.Finish()
        fmt.Fprintf(w, "Welcome to Golang: %s\n", r.URL.Path)
    })

    log.Fatal(http.ListenAndServe(":80", nil))

```


### Setup Jaeger agent as a Sidecar

To enable jaeger agent on python web application you need annonate the webapp deployment as per below 
```
$ kubectl annotate deployments.apps golang-web sidecar.jaegertracing.io/inject=true
```

When you run annotate Jaeger Operator will trigger a deployment with Jaeger agent as a sidecar

Run below command to get the Python Web Application URL
```
export GOPORT=$(kubectl get svc golang-web -o jsonpath='{.spec.ports[0].nodePort}')
export NODE_IP=$(kubectl get nodes --namespace default -o jsonpath="{.items[0].status.addresses[0].address}")

echo http://$NODE_IP:$PYTHONPORT
```

Trace the access events on Jaeger WebUI 

## Jaeger with Docker Compose

If you want to use docker-compose to run Jaeger Opentracing with docker-compose, run the below command
```
git clone https://github.com/angudadevops/jaeger-k8s.git

docker-compose up -d 
```

- Access Go web application with host port as 8081
- Access Jaeger application with host port as 16686
