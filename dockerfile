FROM python:3.10.12-slim-bookworm

WORKDIR /app
COPY requirements.txt .

# Install common dependencies
RUN pip install $(grep -v "fuse\|git+" requirements.txt)

# Install build dependencies
RUN apt-get update && \
    apt-get install -y git pkg-config libfuse-dev gcc make

# Architecture-specific installations
ARG TARGETPLATFORM
RUN target_platform="${TARGETPLATFORM:-linux/$(dpkg --print-architecture)}" && \
    echo "Building for $target_platform" && \
    case "$target_platform" in \
        "linux/amd64"|"linux/arm64") \
            pip install fuse-python \
            ;; \
        "linux/armhf"|"linux/arm/v7"|"linux/arm/v8") \
            pip install git+https://github.com/libfuse/python-fuse \
            ;; \
        *) \
            echo "Unsupported platform: $target_platform" && exit 1 \
            ;; \
    esac

COPY . .

ENV TORBOX_API_KEY=
ENV MOUNT_METHOD=strm
ENV MOUNT_PATH=/torbox

CMD ["python", "main.py"]
