# 环境配置说明

## 问题诊断

如果遇到 **404 错误**，说明 API 地址配置不正确或后端服务未运行。

## 解决方案

### 方案 1: 使用本地开发服务器（推荐）

#### 1. 启动后端服务器

```bash
cd c:\coding\kongbai
python run.py
```

确保看到类似输出：
```
* Running on http://127.0.0.1:5000
```

#### 2. 配置移动端 API 地址

编辑 `config.js`，设置环境为 `local`：

```javascript
const ENV = 'local'; // 使用本地开发环境
```

#### 3. 根据运行平台选择地址

**Android 模拟器**:
```javascript
android: 'http://10.0.2.2:5000',  // 10.0.2.2 是模拟器访问主机的特殊地址
```

**iOS 模拟器**:
```javascript
ios: 'http://localhost:5000',
```

**真机测试**（需要在同一 WiFi 网络）:
```javascript
// 查看本机 IP 地址
// Windows: ipconfig
// Mac/Linux: ifconfig

android: 'http://192.168.1.100:5000',  // 替换为你的本机 IP
ios: 'http://192.168.1.100:5000',
```

### 方案 2: 部署到生产服务器

#### 1. 部署后端代码到服务器

```bash
# 在服务器上
cd /path/to/kongbai
git pull
pip install -r requirements.txt
# 重启服务
systemctl restart your-app-service
```

#### 2. 配置移动端使用生产环境

编辑 `config.js`：

```javascript
const ENV = 'production'; // 使用生产环境
```

生产环境地址已配置为：
```javascript
production: {
  android: 'https://bigmang.xyz',
  ios: 'https://bigmang.xyz',
  web: 'https://bigmang.xyz',
}
```

## 快速测试

### 测试后端 API 是否可访问

#### 本地环境测试

```bash
# PowerShell
Invoke-WebRequest -Uri "http://localhost:5000/api/auth/login" -Method POST -ContentType "application/json" -Body '{"username":"admin","password":"admin123"}'
```

#### 生产环境测试

```bash
# Postman
POST https://bigmang.xyz/api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

**期望响应**:
```json
{
  "status": "success",
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "user_id": "admin",
      "username": "admin"
    }
  }
}
```

## 常见问题

### 1. Android 模拟器无法连接 localhost

**问题**: Android 模拟器的 localhost 指向模拟器本身，不是主机。

**解决**: 使用 `10.0.2.2` 代替 `localhost`
```javascript
android: 'http://10.0.2.2:5000',
```

### 2. 真机无法连接本地服务器

**问题**: 真机和电脑不在同一网络。

**解决**: 
1. 确保手机和电脑连接同一 WiFi
2. 查看电脑 IP 地址：
   ```bash
   # Windows
   ipconfig
   
   # 找到 IPv4 地址，例如: 192.168.1.100
   ```
3. 使用电脑 IP 地址：
   ```javascript
   android: 'http://192.168.1.100:5000',
   ```

### 3. 生产环境 404 错误

**问题**: 后端代码未部署或服务未重启。

**解决**:
1. 确认后端代码已更新
2. 重启后端服务
3. 检查路由是否正确注册

### 4. CORS 跨域错误

**问题**: 后端未配置 CORS。

**解决**: 在后端 `app/__init__.py` 中添加：
```python
from flask_cors import CORS
CORS(app)
```

## 调试技巧

### 1. 查看当前 API 地址

移动端启动时会在控制台打印：
```
API Base URL: http://10.0.2.2:5000
```

### 2. 查看网络请求

在 React Native Debugger 中查看 Network 标签。

### 3. 添加详细日志

在 `services/api.js` 中添加：
```javascript
apiClient.interceptors.request.use(
  async (config) => {
    console.log('Request:', config.method.toUpperCase(), config.url);
    console.log('Headers:', config.headers);
    console.log('Data:', config.data);
    // ...
  }
);

apiClient.interceptors.response.use(
  (response) => {
    console.log('Response:', response.status, response.data);
    return response;
  },
  (error) => {
    console.log('Error:', error.response?.status, error.response?.data);
    return Promise.reject(error);
  }
);
```

## 推荐配置

### 开发阶段

```javascript
// config.js
const ENV = 'local';

const API_URLS = {
  local: {
    android: 'http://10.0.2.2:5000',
    ios: 'http://localhost:5000',
    web: 'http://localhost:5000',
  },
};
```

### 生产发布

```javascript
// config.js
const ENV = 'production';

const API_URLS = {
  production: {
    android: 'https://bigmang.xyz',
    ios: 'https://bigmang.xyz',
    web: 'https://bigmang.xyz',
  },
};
```

## 检查清单

- [ ] 后端服务器正在运行
- [ ] 后端 API 路由已正确注册
- [ ] `config.js` 中的 ENV 设置正确
- [ ] API 地址配置正确（本地用 10.0.2.2，生产用域名）
- [ ] 网络连接正常
- [ ] 防火墙未阻止连接
- [ ] 后端已安装所有依赖（`pip install -r requirements.txt`）
- [ ] 移动端已安装所有依赖（`npm install`）

## 快速修复步骤

1. **确认后端运行**
   ```bash
   cd c:\coding\kongbai
   python run.py
   ```

2. **配置本地开发**
   ```javascript
   // config.js
   const ENV = 'local';
   ```

3. **重启移动端**
   ```bash
   cd c:\coding\kongbai\BattleStats
   npm start
   ```

4. **测试登录**
   - 用户名: admin
   - 密码: admin123

如果仍有问题，查看控制台的详细错误信息。
