FROM golang:1.21-alpine AS build
WORKDIR /src
COPY go.mod ./
RUN go mod download 2>/dev/null || true
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o /out/cyberguard main.go

FROM alpine:3.19
RUN adduser -D -u 1001 cyberguard
WORKDIR /srv
COPY --from=build /out/cyberguard /usr/local/bin/cyberguard
COPY static /srv/static
USER cyberguard
EXPOSE 8080
CMD ["/usr/local/bin/cyberguard"]
