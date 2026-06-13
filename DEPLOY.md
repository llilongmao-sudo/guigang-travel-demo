# 贵港旅游智能助手 - 部署指南

## 环境要求
- Python 3.8+
- Windows Server / Linux

## 本地生产环境启动

### Windows（使用 Waitress）
```powershell
# 安装依赖
pip install -r requirements.txt

# 启动生产服务器（端口 5001）
waitress-serve --host=0.0.0.0 --port=5001 app:app
```

### Linux（使用 Gunicorn）
```bash
# 安装依赖
pip install -r requirements.txt

# 启动（4 workers）
gunicorn -w 4 -b 0.0.0.0:5001 app:app
```

## 云服务器部署

### 方案 A：阿里云/腾讯云轻量应用服务器

1. **购买服务器**
   - 配置：1核2G 足够（约 60-100元/月）
   - 系统：Ubuntu 22.04 或 CentOS 8

2. **安装环境**
   ```bash
   # SSH 登录服务器
   ssh root@你的服务器IP
   
   # 安装 Python
   apt update && apt install -y python3 python3-pip python3-venv nginx
   
   # 上传代码（本地执行）
   scp -r guigang-travel-demo root@服务器IP:/opt/
   
   # 服务器上创建虚拟环境
   cd /opt/guigang-travel-demo
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt gunicorn
   ```

3. **配置 Systemd 服务**
   ```bash
   # /etc/systemd/system/guigang-travel.service
   [Unit]
   Description=Guigang Travel Assistant
   After=network.target
   
   [Service]
   User=www-data
   WorkingDirectory=/opt/guigang-travel-demo
   ExecStart=/opt/guigang-travel-demo/venv/bin/gunicorn -w 4 -b 127.0.0.1:5001 app:app
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```
   
   ```bash
   systemctl enable guigang-travel
   systemctl start guigang-travel
   ```

4. **配置 Nginx 反向代理**
   ```nginx
   # /etc/nginx/sites-available/guigang-travel
   server {
       listen 80;
       server_name 你的域名.com;
   
       location / {
           proxy_pass http://127.0.0.1:5001;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   
       location /static {
           alias /opt/guigang-travel-demo/static;
       }
   }
   ```
   
   ```bash
   ln -s /etc/nginx/sites-available/guigang-travel /etc/nginx/sites-enabled/
   nginx -t && systemctl restart nginx
   ```

5. **HTTPS（可选但推荐）**
   ```bash
   apt install -y certbot python3-certbot-nginx
   certbot --nginx -d 你的域名.com
   ```

### 方案 B：内网穿透（适合开发测试）

使用 frp 或 ngrok 暴露本地服务：

```bash
# ngrok（需要注册）
ngrok http 5001

# 或 frp（自建服务器）
frpc -c frpc.ini
```

## 环境变量配置

```bash
# LLM API（可选，不配置则使用本地知识库）
export LLM_API_BASE="http://你的Ollama服务器:11434/v1"
export LLM_API_KEY="你的API密钥"  # 如果用云服务

# 端口（默认 5001）
export PORT=5001
```

## 数据维护

景点数据在 `data/` 目录：
- `attractions.json` - 景点信息
- `food.json` - 美食数据
- `routes.json` - 路线数据

修改后重启服务即可生效。

## 监控日志

```bash
# 查看服务状态
systemctl status guigang-travel

# 查看日志
journalctl -u guigang-travel -f
```

## 常见问题

**Q: 启动后外部无法访问？**
- 检查防火墙：`ufw allow 5001` 或云服务器安全组放行端口
- 检查 Nginx 配置：`nginx -t`

**Q: LLM 连接失败？**
- 应用会自动降级到本地知识库模式
- 如需 LLM，确保 Ollama 运行或配置正确的 API 地址

**Q: 静态文件 404？**
- 检查 `static/` 目录权限
- Nginx 配置中的 alias 路径需完整
