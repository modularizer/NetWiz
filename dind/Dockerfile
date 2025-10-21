# Dockerfile for NetWiz Docker-in-Docker container
# This Dockerfile must be built from the project root directory
# Usage: docker build -f dind/Dockerfile -t netwiz:tag .

FROM docker:24-dind
RUN apk add --no-cache docker-cli-compose tini
# Install docker-compose and curl
RUN apk add --no-cache docker-compose curl

# Create working directory
WORKDIR /app

# Copy only the necessary files for DinD operation
COPY dind/docker-compose.yml /app/
COPY dind/dind-internal-start.sh /app/

# Copy locally built images as tar files
COPY netwiz-backend.tar /app/
COPY netwiz-frontend.tar /app/
COPY netwiz-nginx.tar /app/
COPY mongo.tar /app/


RUN apk add --no-cache iptables iptables-legacy ebtables || true \
 && if [ -x /sbin/iptables-legacy ]; then \
      ln -sf /sbin/iptables-legacy /sbin/iptables; \
    fi \
 && if [ -x /sbin/ip6tables-legacy ]; then \
      ln -sf /sbin/ip6tables-legacy /sbin/ip6tables; \
    fi \
 && if [ -x /sbin/ebtables-legacy ]; then \
      ln -sf /sbin/ebtables-legacy /sbin/ebtables || true; \
    fi



# Set DinD environment variables for better compatibility and security
ENV DOCKER_TLS_CERTDIR=""
EXPOSE 80

# Our script will start dockerd then compose
ENTRYPOINT ["/sbin/tini","-s","--"]
CMD ["/app/dind-internal-start.sh"]
