package main

import (
    opentracing "github.com/opentracing/opentracing-go"
    jaeger "github.com/uber/jaeger-client-go"
    config "github.com/uber/jaeger-client-go/config"
    "github.com/opentracing/opentracing-go/ext"
    "fmt"
    "time"
    "net/http"
    "log"
    "io"
    "os"
)


const jaegerServiceName = "goweb"
//const jaegerHostPort = "jaeger:5775"

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

}
