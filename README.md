
## 🛒 仿京东商城项目（Django + Vue）

一个基于 Django 后端与 Vue 前端构建的在线购物平台练习项目，目标是实现一个功能完整、可扩展的电商系统。

---

### 📦 技术栈

- **后端**：Django + Django REST Framework + MySQL  
- **前端**：Vue 3 + Pinia + Axios + Element Plus  
- **开发工具**：PyCharm, VS Code, Git, GitHub  
- **环境管理**：Python venv / pipenv, Node.js + npm/yarn

---

### 🚀 快速启动

#### 后端

```bash
# 创建虚拟环境并激活
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 数据库迁移
python manage.py migrate

# 启动开发服务器
python manage.py runserver
```

#### 前端

```bash
# 安装依赖
cd frontend
yarn install

# 启动前端开发服务器
yarn dev
```

---

### 📁 项目结构（可扩展）

```
├── backend/               # Django 项目目录
│   ├── api/               # Django 应用：商品、订单、用户等
│   ├── settings/          # 分环境配置（dev/prod）
│   └── urls.py            # 路由配置
├── frontend/              # Vue 项目目录
│   ├── src/
│   │   ├── views/         # 页面组件
│   │   ├── components/    # 可复用组件
│   │   ├── store/         # 状态管理（Pinia）
│   │   └── router/        # 路由配置
├── .gitignore
├── README.md
└── requirements.txt
```

---

### 🧩 功能模块规划（持续扩展）

- ✅ 商品浏览与搜索
- ✅ 用户注册与登录（JWT）
- ✅ 购物车与结算
- ✅ 订单管理与支付接口（模拟）
- ⏳ 后台管理系统（待开发）
- ⏳ 商品评价与推荐系统（待开发）

---

### 📌 TODO

- [ ] 接入第三方支付（如支付宝沙箱）
- [ ] 商品分类与筛选
- [ ] 后台商品管理界面
- [ ] 单元测试与接口测试

---

### 📜 License

MIT License
