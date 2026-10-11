FROM node:24.15.0-bookworm-slim@sha256:4e6b70dd6cbfc88c8157ba19aa3d9f9cce6ba4703576d55459e45efcbc9c5f5d AS node
FROM eclipse-temurin:25.0.4.1_1-jdk-jammy@sha256:318f90a80337fb6f26b025dbec0a95fa6f48abf60ce129babf555618356bdbf8
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates unzip git python3 libatomic1 neovim && rm -rf /var/lib/apt/lists/*
COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY --from=node /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -s /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm && ln -s /usr/local/lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx \
 && npm install -g @openai/codex@0.162.0
ARG DEV_UID=1000
RUN groupadd --gid 1000 dev && useradd --create-home --uid ${DEV_UID} --gid dev --shell /bin/bash dev \
 && mkdir -p /home/dev/.local/share /home/dev/.config /home/dev/.cache /home/dev/.m2 /home/dev/.codex \
 && chown -R dev:dev /home/dev
ENV HOME=/home/dev SHELL=/bin/bash
USER dev
WORKDIR /workspace/app
CMD ["sleep", "infinity"]
