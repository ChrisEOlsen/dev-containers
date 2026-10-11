FROM node:24.15.0-bookworm-slim@sha256:4e6b70dd6cbfc88c8157ba19aa3d9f9cce6ba4703576d55459e45efcbc9c5f5d AS node
FROM eclipse-temurin:21.0.11_10-jdk-jammy@sha256:dbfd085220ae632a0830166e443747d1ee89e9038d92e3b48c3e5e9d8292b9a7
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates unzip git python3 libatomic1 vim && rm -rf /var/lib/apt/lists/*
COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY --from=node /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -s /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm && ln -s /usr/local/lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx \
 && npm install -g @openai/codex@0.162.0
ARG TARGETARCH
RUN case "$TARGETARCH" in \
      amd64) EDITOR_SHA=65bcd20b524d03eb1b5adb7f360244599ef0e5b74089a46a982d32c074b97a29 ;; \
      arm64) EDITOR_SHA=e5cc78da1d631c6cf6162f9b18eeaa8ee9d3239e1a88bb99d0602cdc5fa1852d ;; \
      *) echo "Unsupported architecture: $TARGETARCH" >&2; exit 1 ;; \
    esac \
 && curl -fsSL "https://github.com/coder/code-server/releases/download/v4.141.0/code-server-4.141.0-linux-${TARGETARCH}.tar.gz" -o /tmp/editor.tgz \
 && echo "$EDITOR_SHA  /tmp/editor.tgz" | sha256sum -c - \
 && tar -xzf /tmp/editor.tgz -C /opt && rm /tmp/editor.tgz \
 && ln -s /opt/code-server-4.141.0-linux-${TARGETARCH}/bin/code-server /usr/local/bin/code-server
ARG DEV_UID=1000
RUN groupadd --gid 1000 dev && useradd --create-home --uid ${DEV_UID} --gid dev --shell /bin/bash dev && mkdir -p /opt/extensions
RUN curl -fsSL https://open-vsx.org/api/redhat/java/1.49.0/file/redhat.java-1.49.0.vsix -o /opt/extensions/java.vsix \
 && echo 'e2e067d8d1dddf666ca284c9d1cf4f589d7860722aed18176fe29d687e2fb82a  /opt/extensions/java.vsix' | sha256sum -c - \
 && curl -fsSL https://open-vsx.org/api/vscodevim/vim/1.32.4/file/vscodevim.vim-1.32.4.vsix -o /opt/extensions/vim.vsix \
 && echo '0faab122afd25bc94f5ef9cf9678e64cbd554d6dc88fe87ffe11bba623814168  /opt/extensions/vim.vsix' | sha256sum -c - \
 && curl -fsSL https://open-vsx.org/api/Angular/ng-template/22.2.0/file/Angular.ng-template-22.2.0.vsix -o /opt/extensions/angular.vsix \
 && echo '13f97986133a7f5e0aec7ffc83ed3b8ff642f6cf09611324343b7172ed9eca36  /opt/extensions/angular.vsix' | sha256sum -c -
COPY .devcontainer/start.sh /usr/local/bin/start-editor
RUN chmod 755 /usr/local/bin/start-editor
USER dev
WORKDIR /workspace/app
ENTRYPOINT ["start-editor"]
