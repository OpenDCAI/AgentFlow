# Google Drive 配置说明

当前目录包含运行 `_googledrive_setup` 与 `get_googledrive_file` 所需的三个文件：

1. `settings.yml`  
   - PyDrive 的主配置文件。已将 `client_config_file` 与 `save_credentials_file` 指向本目录。  
   - 如需把凭证存到其他位置，可修改对应路径。

2. `client_secrets.json`  
   - 需要从 Google Cloud Console 创建 OAuth 2.0 桌面应用后下载的客户端密钥。  
   - 获取流程：  
     1. 进入 GCP 控制台 → 选择项目 → 启用 Google Drive API。  
     2. 在“凭据”中新建 OAuth 客户端（类型选 “桌面应用”）。  
     3. 下载得到的 JSON 替换本文件中的 `client_id`、`client_secret` 等字段。

3. `credentials.json`  
   - 首次运行 PyDrive 时会自动生成/更新的访问令牌文件。  
   - 在无法完成 OAuth 的情况下可保持空模板；将来一旦完成授权，PyDrive 会写入真实的 `token`、`refresh_token` 等。

> 注意：以上文件均已加入 `.gitignore`，不会被 Git 追踪。填写真实凭证后即可直接使用；若需要共享模板，可复制 `.template` 版本。下一步可按需配置目录中的其他服务设置文件。
