# Multi-stage Docker build for FFXI LandSandBoat Server
# Production-optimized with C++20 support and security hardening

# Build stage - Use Ubuntu 24.04 with modern toolchain
FROM ubuntu:24.04 AS build-stage

LABEL maintainer="FFXI LandSandBoat Development Team"
LABEL description="Production-ready FFXI Server with C++20 optimizations"
LABEL version="1.0.0"

# Set environment variables for build
ENV DEBIAN_FRONTEND=noninteractive
ENV CC=gcc-13
ENV CXX=g++-13
ENV CMAKE_BUILD_TYPE=Release
ENV CMAKE_CXX_STANDARD=20

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc-13 \
    g++-13 \
    cmake \
    ninja-build \
    git \
    python3 \
    python3-dev \
    python3-pip \
    libmariadb-dev \
    libmariadb3 \
    mariadb-client \
    libluajit-5.1-dev \
    libzmq3-dev \
    libssl-dev \
    zlib1g-dev \
    pkg-config \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create build directory and copy source
WORKDIR /build
COPY . .

# Configure and build with optimizations
RUN cmake -B build -S . \
    -GNinja \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_CXX_STANDARD=20 \
    -DCMAKE_C_COMPILER=gcc-13 \
    -DCMAKE_CXX_COMPILER=g++-13 \
    -DCMAKE_INSTALL_PREFIX=/opt/ffxi \
    -DBUILD_SHARED_LIBS=OFF \
    -DENABLE_STATIC_LINKING=ON \
    && cmake --build build --config Release --parallel $(nproc) \
    && cmake --install build

# Runtime stage - Minimal production image
FROM ubuntu:24.04 AS runtime-stage

LABEL maintainer="FFXI LandSandBoat Development Team"
LABEL description="FFXI Server Runtime Container"

# Set runtime environment
ENV DEBIAN_FRONTEND=noninteractive
ENV FFXI_USER=ffxi
ENV FFXI_HOME=/opt/ffxi
ENV PATH="$FFXI_HOME/bin:$PATH"

# Create non-root user for security
RUN groupadd -r $FFXI_USER && useradd -r -g $FFXI_USER -d $FFXI_HOME -s /bin/bash $FFXI_USER

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    libmariadb3 \
    mariadb-client \
    libluajit-5.1-2 \
    libzmq5 \
    libssl3 \
    zlib1g \
    python3 \
    python3-pip \
    curl \
    ca-certificates \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY tools/requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt

# Create application directory structure
RUN mkdir -p $FFXI_HOME/{bin,settings,logs,sql,scripts,tools,res} \
    && chown -R $FFXI_USER:$FFXI_USER $FFXI_HOME

# Copy built binaries and dependencies from build stage
COPY --from=build-stage --chown=$FFXI_USER:$FFXI_USER /opt/ffxi $FFXI_HOME/

# Copy additional runtime files
COPY --chown=$FFXI_USER:$FFXI_USER settings/ $FFXI_HOME/settings/
COPY --chown=$FFXI_USER:$FFXI_USER scripts/ $FFXI_HOME/scripts/
COPY --chown=$FFXI_USER:$FFXI_USER sql/ $FFXI_HOME/sql/
COPY --chown=$FFXI_USER:$FFXI_USER tools/ $FFXI_HOME/tools/
COPY --chown=$FFXI_USER:$FFXI_USER res/ $FFXI_HOME/res/
COPY --chown=$FFXI_USER:$FFXI_USER docker/entrypoint.sh $FFXI_HOME/entrypoint.sh
COPY --chown=$FFXI_USER:$FFXI_USER docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Set proper permissions
RUN chmod +x $FFXI_HOME/entrypoint.sh \
    && chmod +x $FFXI_HOME/bin/* \
    && mkdir -p $FFXI_HOME/logs \
    && chown -R $FFXI_USER:$FFXI_USER $FFXI_HOME

# Expose standard FFXI ports
EXPOSE 54001/tcp 54002/tcp 54230/tcp 54230/udp 54231/tcp 51220/tcp 54003/tcp 8088/tcp

# Set up health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD $FFXI_HOME/entrypoint.sh health || exit 1

# Switch to non-root user
USER $FFXI_USER
WORKDIR $FFXI_HOME

# Set entrypoint
ENTRYPOINT ["./entrypoint.sh"]
CMD ["all"]