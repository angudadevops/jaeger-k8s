FROM golang

COPY . ./

RUN go get -u github.com/go-sql-driver/mysql && \
    go get -u github.com/opentracing/opentracing-go && \
    go get -u github.com/uber/jaeger-lib/metrics && \ 
    go get -u github.com/uber/jaeger-client-go && \
    go get -u github.com/uber/jaeger-client-go/config && \
    go get -u github.com/uber/jaeger-client-go/log && \
    go get -u github.com/opentracing/opentracing-go/ext

RUN go build ./main.go

EXPOSE 80 

CMD ["./main"]
