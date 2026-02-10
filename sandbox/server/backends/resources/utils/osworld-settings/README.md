# osworld-settings 说明

该目录用于集中存放桌面环境相关的配置文件，供服务端在启动与运行时读取。
当前包含以下子目录与文件：

## 目录结构与用途

- `google/`
  - `settings.json`：当前 Google 相关配置。
  - `settings.json.template`：配置模板与参考格式。
- `googledrive/`
  - `client_secrets.json`：Google Drive OAuth 客户端配置。
  - `settings.yml`：当前 Google Drive 相关配置。
  - `settings.yml.template`：配置模板与参考格式。
  - `README.md`：该子目录的详细说明（如鉴权流程）。
- `proxy/`
  - `dataimpulse.json`：当前代理池配置（当前仅 1 条代理）。
  - `dataimpulse.json.template`：代理池配置模板。
- `thunderbird/`
  - `settings.json`：当前 Thunderbird 相关配置。
  - `settings.json.template`：配置模板与参考格式。

## 通用约定

- `*.template` 文件用于说明字段结构与默认示例，可作为新环境的初始化参考。
- `proxy/` 的配置默认由 `PROXY_CONFIG_FILE` 环境变量覆盖；若未设置，则使用
  `proxy/dataimpulse.json`。

