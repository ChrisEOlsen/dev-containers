# Angular / Spring Boot / PostgreSQL development container

Reusable development environment extracted from ReviewDesk. Copy this folder’s contents (including hidden files) into the root of a project, then start it with Docker Compose. Application code is not included.

## Included

- Java 21 (Eclipse Temurin 21.0.11) and Node.js 24.15.0 with npm/npx.
- PostgreSQL 16.13 on the private Compose network.
- code-server 4.141.0 with Java, Angular language support, and Vim extensions.
- Codex CLI 0.162.0, Git, Python 3, curl, unzip, and Vim.
- Persistent volumes for PostgreSQL data, Maven cache, editor state, and Codex state.
- VS Code Dev Containers configuration and editor settings.

The image and download versions are pinned to the source environment. This template targets Linux amd64 because its code-server download is architecture-specific. Docker Engine, Docker Compose with `include` support (Compose 2.20 or newer), and Python 3 for the setup script must be installed on the host. The container runs development tools as the non-root `dev` user; a short root initialization service fixes ownership of its cache volumes. The Docker socket is not mounted.

## Quick start

1. Copy `.devcontainer/`, `.vscode/settings.json`, `compose.dev.yml`, `compose.database.yml`, `.env.example`, and `scripts/init-local.py` into your project root. Merge editor settings if the project already has them. Add the template’s `.gitignore` rules to your project’s existing `.gitignore`.
2. From that project root, create your local configuration:

   ```sh
   python3 scripts/init-local.py
   ```

   The script generates random database and editor passwords, sets `LOCAL_UID` to your host user ID (or 1000 when run as root), and creates `.env` with owner-only permissions (`0600`). It leaves an existing `.env` untouched and never prints passwords. Open `.env` privately when you need the editor password. Run the script from your project root, and keep `.env` ignored by Git. The container group is GID 1000.
3. Build and start:

   ```sh
   docker compose -f compose.dev.yml up -d --build
   ```

4. Open <http://localhost:5678> and sign in using `CODE_SERVER_PASSWORD`. The project is mounted at `/workspace/app`. For a terminal:

   ```sh
   docker compose -f compose.dev.yml exec dev bash
   ```

The first build downloads the toolchain and extensions; later starts reuse the image and volumes. Alternatively, open the project with VS Code’s Dev Containers extension and choose **Reopen in Container** after preparing `.env`.

## Running your application

Start your project’s frontend and backend from inside the container using its existing commands. Angular should listen on `0.0.0.0:4200`; the backend should listen on port 8080. The host exposes:

| Service | Host address |
| --- | --- |
| Browser editor | http://localhost:5678 |
| Angular frontend | http://localhost:4200 |
| Spring Boot backend | http://localhost:8081 |

All published ports bind to host loopback. PostgreSQL is accessible within Compose at `postgres:5432`; it has no published host port. The development service receives `DATABASE_URL` (a JDBC URL), `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `APP_BASE_URL`. Configure your Spring Boot project to consume these variables; they are not automatically mapped to Spring datasource properties.

This is a toolchain template: Angular, Spring Boot, and Quartz dependencies belong to your application, and Maven should be invoked through the project’s Maven wrapper. AWS resources and tooling are not provisioned. `FILES_ENABLED=false` remains the local default; this template does not verify an S3 integration.

## Accessing a remote machine over Tailscale

The published ports bind to `127.0.0.1` on the machine running Docker. If Docker runs on a remote machine, your laptop’s `localhost` does not reach those ports directly. Run this command **on your laptop** to forward them through SSH over Tailscale:

```sh
ssh -N -o ExitOnForwardFailure=yes \
  -L 127.0.0.1:5678:127.0.0.1:5678 \
  -L 127.0.0.1:4200:127.0.0.1:4200 \
  -L 127.0.0.1:8081:127.0.0.1:8081 \
  your-user@remote-tailscale-name-or-ip
```

Replace `your-user` with your account on the remote machine and `remote-tailscale-name-or-ip` with its Tailscale hostname or IP. Both machines must have Tailscale connectivity, and the remote machine must accept SSH for your account (through its SSH server or configured Tailscale SSH).

Keep the command running, then open <http://localhost:5678> for the editor, <http://localhost:4200> for the frontend, or <http://localhost:8081> for the backend **on your laptop**. Stop the tunnel with Ctrl+C. If a local port is occupied, change the first port in its `-L` mapping and use that port in your browser; for example, `-L 127.0.0.1:15678:127.0.0.1:5678` exposes the editor at <http://localhost:15678>.

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

Keep `.env` and credentials out of version control. Persistent editor and Codex volumes may contain authentication state. This environment is intended for local development; production should use separate runtime images without development tools.
