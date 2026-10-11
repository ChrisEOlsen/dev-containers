# Angular / Spring Boot / PostgreSQL development container

Copy this folder’s contents (including hidden files) into the root of a project, then start it with Docker Compose. Application code is not included.

## Included

- Java 25 (Eclipse Temurin 25.0.4.1) and Node.js 24.15.0 with npm/npx.
- PostgreSQL 16.13 on the private Compose network.
- Codex CLI 0.162.0, Git, Python 3, curl, unzip, and Neovim (`nvim`).
- Persistent volumes for PostgreSQL data, Maven cache and Codex state.
- Zed and VS Code Dev Containers configuration; VS Code Java, Angular, and Vim extensions.

The image and download versions are pinned to the source environment. The base images support Linux ARM64 and AMD64. Docker Engine, Docker Compose with `include` support (Compose 2.20 or newer), and Python 3 for the setup script must be installed on the host. The container runs development tools as the non-root `dev` user; a short root initialization service fixes ownership of its cache volumes. The Docker socket is not mounted.

## Quick start

1. Copy `.devcontainer/`, `.vscode/settings.json`, `compose.dev.yml`, `compose.database.yml`, `.env.example`, and `scripts/init-local.py` into your project root. Merge editor settings if the project already has them. Add the template’s `.gitignore` rules to your project’s existing `.gitignore`.
2. From that project root, create your local configuration:

   ```sh
   python3 scripts/init-local.py
   ```

   The script generates a random database password, sets `LOCAL_UID` to your host user ID (or 1000 when run as root), and creates `.env` with owner-only permissions (`0600`). It leaves an existing `.env` untouched and never prints passwords. Run the script from your project root, and keep `.env` ignored by Git. The container group is GID 1000.
3. Build and start:

   ```sh
   docker compose -f compose.dev.yml up -d --build
   ```

4. Open the project root in your desktop editor:

   - **VS Code:** install the Dev Containers extension, then choose **Dev Containers: Reopen in Container** from the command palette.
   - **Zed:** choose **Project: Open Remote → Connect Dev Container**, then select this project's configuration. Install current Zed and ensure Docker is available in its PATH.

   Terminals and language servers run inside the container as `dev`. VS Code installs the configured Java, Angular, and Vim extensions; Zed installs its Java extension and uses its own language support. Editor extensions are managed by the desktop editor, not baked into the image.

For a shell or Neovim without a desktop editor:

```sh
docker compose -f compose.dev.yml exec dev bash
docker compose -f compose.dev.yml exec dev nvim
```

The container stays running with `sleep infinity`; there is no browser editor, editor password, or published editor port. The `dev` user's home, cache, configuration, and data directories are writable so editor remote servers can start. `LOCAL_UID` controls the image's user ID; the editor does not rewrite it. After changing it, rebuild the image.

When migrating an existing setup, rebuild with `docker compose -f compose.dev.yml up -d --build`. Reconnect Zed to the new container; in VS Code use **Dev Containers: Rebuild and Reopen in Container**. PostgreSQL, Maven, and Codex volumes are preserved. The old unused editor volume is not mounted or deleted.

Editor remote binaries and extensions may be downloaded again when the container is recreated. Neovim is installed from the base distribution's package repository and has no bundled plugin configuration.

References: [Zed dev containers](https://zed.dev/docs/dev-containers), [VS Code dev containers](https://code.visualstudio.com/docs/devcontainers/containers).

## Running your application

Start your project’s frontend and backend from inside the container using its existing commands. Angular should listen on `0.0.0.0:4200`; the backend should listen on port 8080. The host exposes:

| Service | Host address |
| --- | --- |
| Angular frontend | http://localhost:4200 |
| Spring Boot backend | http://localhost:8081 |

If port 8081 is already in use, set `BACKEND_PORT=8082` (or another free port) in `.env`, then rerun `docker compose -f compose.dev.yml up -d`. Use the configured port in the backend URL, such as <http://localhost:8082>.

All published ports bind to host loopback. PostgreSQL is accessible within Compose at `postgres:5432`; it has no published host port. The development service receives `DATABASE_URL` (a JDBC URL), `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `APP_BASE_URL`. Configure your Spring Boot project to consume these variables; they are not automatically mapped to Spring datasource properties.

This is a toolchain template: Angular, Spring Boot, and Quartz dependencies belong to your application, and Maven should be invoked through the project’s Maven wrapper. AWS resources and tooling are not provisioned. `FILES_ENABLED=false` remains the local default; this template does not verify an S3 integration.

## Accessing a remote machine over Tailscale

The published ports bind to `127.0.0.1` on the machine running Docker. If Docker runs on a remote machine, your laptop’s `localhost` does not reach those ports directly. Run this command **on your laptop** to forward them through SSH over Tailscale:

```sh
ssh -N -o ExitOnForwardFailure=yes \
  -L 127.0.0.1:4200:127.0.0.1:4200 \
  -L 127.0.0.1:8081:127.0.0.1:8081 \
  your-user@remote-tailscale-name-or-ip
```

Replace `your-user` with your account on the remote machine and `remote-tailscale-name-or-ip` with its Tailscale hostname or IP. Both machines must have Tailscale connectivity, and the remote machine must accept SSH for your account (through its SSH server or configured Tailscale SSH).

If you changed `BACKEND_PORT` on the remote machine, update the destination port in the backend tunnel mapping too; for example, use `-L 127.0.0.1:8081:127.0.0.1:8082` for `BACKEND_PORT=8082`.

Keep the command running, then open <http://localhost:4200> for the frontend or <http://localhost:8081> for the backend on your laptop. Stop the tunnel with Ctrl+C. If a local port is occupied, change the first port in its `-L` mapping and use that port in your browser.

For editing on a remote Docker host, VS Code supports connecting to that host with Remote SSH and then reopening the project in its dev container. Zed's local dev container instructions above assume Docker runs locally; its SSH workflow is separate. Do not expose the Docker API or add an SSH server to this container just for local editor access.

This is SSH **local forwarding** (`-L`): it brings services on the remote machine to your laptop. Reverse forwarding (`-R`) exposes a service from your laptop on the remote machine, so it is not needed for this setup. The Compose port bindings can stay as they are.

## Everyday use

```sh
# Stop while preserving database and development state.
docker compose -f compose.dev.yml stop

# Restart existing containers.
docker compose -f compose.dev.yml start

# Inspect service status.
docker compose -f compose.dev.yml ps
```

Each project directory gets its own Compose volumes by default. Use a unique `-p` project name if two directories have the same basename, and change host port mappings if running multiple environments simultaneously. Reusing the same Compose project name reuses its database and caches. Changing `POSTGRES_PASSWORD`, `POSTGRES_USER`, or `POSTGRES_DB` in `.env` does not reinitialize an existing PostgreSQL data volume.

Keep `.env` and credentials out of version control. The persistent Codex volume may contain authentication state. This environment is intended for local development; production should use separate runtime images without development tools.
