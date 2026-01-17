# ÉP CHẠY AMD64 ĐỂ TRÁNH LỖI PLUGIN TRÊN ARM (M2)
FROM jenkins/jenkins:lts

USER root

# Cài Docker CLI + các tool cần cho CI
RUN apt-get update && \
    apt-get install -y \
    docker.io \
    curl \
    git \
    ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Cho user jenkins dùng docker
RUN usermod -aG docker jenkins

# Fix quyền cho Jenkins home
RUN chown -R jenkins:jenkins /var/jenkins_home

USER jenkins
