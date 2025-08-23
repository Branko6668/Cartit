# Cartit 接口 & 前后端对接文档

> 状态：本地开发版本（验证码走控制台打印，无真实短信网关）。
> 统一响应包装：CustomResponse；除特别说明外均使用 JSON。

---
## 1. 通用响应结构
```json
{
  "code": 0,
  "msg": "success",
  "data": {},
  "action": "(可选)",
  "errors": {"field": "error"},
  "sub_code": 10001
}
```
字段说明：
- code：业务码（集中管理：utils/error_codes.py）
- msg：简短描述
- data：主数据载荷（对象 / 数组 / 分页 / null）
- errors：字段级错误详情（仅调试/表单展示，不返回敏感信息）
- action：前端可选后续指令（如 refresh_login）
- sub_code：细分业务码（预留）

分页 data 示意（PageNumberPagination）：
```json
{
  "count": 120,
  "next": "http://.../page=3",
  "previous": "http://.../page=1",
  "results": [ ... ]
}
```

---
## 2. 模块路径前缀

| 模块 | 前缀 |
|------|------|
| 商品 Product | /product/ |
| 购物车 Shopping Cart | /shopping_cart/ |
| 用户 User | /user/ |
| 订单 Order | /order/ |
| 评论 Review | /review/ |
| Admin | /admin/ |
| OpenAPI Schema | /api/schema/ |
| Swagger UI | /api/docs/ |
| Redoc | /api/redoc/ |

---
## 3. 商品模块 Product
### 3.1 分类
| 方法 | 路径 | 说明 | 成功码 |
|------|------|------|--------|
| GET | /product/main_menu/ | 一级分类(parent_id=0) | 1000 |
| GET | /product/sub_menu/?main_menu_id=1 | 二级分类 | 1001 |
| GET | /product/sub_sub_menu/?sub_menu_id=2 | 三级分类 | 1002 |
缺参/格式错误：1400

### 3.2 标签商品列表
GET /product/tag/<product_tag_id>/<page>/  (分页大小固定 20) 成功码：2000

### 3.3 商品详情
GET /product/query/<id>/ 成功码：2001
- 不存在 / 参数错误：2400

### 3.4 商品搜索
GET /product/search/?q=关键词&page=1&page_size=20&sort=0

| 参数 | 必填 | 说明 | 默认 | 取值 |
|------|------|------|------|------|
| q | 是 | 搜索关键词(模糊匹配 name/subtitle/description) | - | 非空字符串 |
| page | 否 | 页码 >=1 | 1 | 正整数 |
| page_size | 否 | 每页条数(1~100) | 20 | 正整数 |
| sort | 否 | 排序方式 | 0 | 0/1/2/3/4 |

sort 映射：
| 值 | 含义 | 排序表达式 |
|----|------|-------------|
| 0 | 默认 | id DESC |
| 1 | 价格升序 | price ASC, id DESC |
| 2 | 价格降序 | price DESC, id DESC |
| 3 | 评论数升序 | review_count ASC, id DESC |
| 4 | 评论数降序 | review_count DESC, id DESC |

返回 data：
q, sort, page, page_size, total, total_pages, has_next, has_prev, current_count, results[]

results[i] 字段：id, name, price(字符串), thumbnail(绝对URL), review_count, store_id, store_name

成功码：2002；错误（缺 q / 参数非法）：1400

---
## 4. 购物车模块 Shopping Cart
路径：/shopping_cart/
| 方法 | 说明 | 参数 | 成功码 |
|------|------|------|--------|
| GET | 获取购物车 | query: user_id | 3000 |
| POST | 添加/更新/移除 | user_id, product_id, quantity | 3001 / 3002 |
规则：已有条目时数量累加；累加=0 -> 删除 (3002)；累加后<0 -> 3400。

---
## 5. 用户模块 User
### 5.1 发送验证码
POST /user/send_code/
请求：{ phone, scene=register|login|reset }
成功：4500；60s 节流：4501；无效手机号：4400
验证码有效期：5 分钟（控制台打印 [DEBUG VCODE]）

### 5.2 注册
POST /user/register/
请求必填：phone, password, code
可选：username, email, avatar_url, birthday
规则：
- 手机号格式 ^1\d{10}$
- 密码 >=6 且含字母 + 数字
- 验证码正确且未过期
成功：4000；错误：4400 / 4502(验证码错误) / 4503(验证码失效)

### 5.3 登录
POST /user/login/
请求：{ phone, password }
成功：4000 → data.token + user
错误码：4401(手机号空) 4402(密码空) 4403(未注册) 4405(禁用) 4406(凭证错误)

### 5.4 重置密码
POST /user/reset_password/
请求：{ phone, code, new_password }
成功：4504；错误：4503/4502/4505/4400

### 5.5 登出
POST /user/logout/ → 4000 （占位，无状态清除）

### 5.6 查询当前用户
GET /user/me/?username=tom （username / email / phone 三选一）
成功：4000；未找到：4404；缺参：4400

### 5.7 更新用户资料
PUT /user/update/
请求需包含 id，允许修改 username/name/phone/email/avatar_url/gender/birthday 与 password（自动加密），成功：4000

### 5.8 注销
DELETE /user/delete/?id=9 软删除 is_deleted=True / status=disabled，成功：4000

### 5.9 地址管理
| 方法 | 路径 | 说明 | 成功码 |
|------|------|------|--------|
| POST | /user/address/ | 创建 | 4000 |
| GET | /user/address/<id>/ | 详情 | 4000 |
| PUT | /user/address/<id>/ | 更新 | 4000 |
| DELETE | /user/address/<id>/ | 删除(软) | 4000 |
| GET | /user/address/list/?user=9 | 列表(支持 user 或 user_id) | 4000 |

---
## 6. 订单模块 Order
| 方法 | 路径 | 说明 | 成功码 |
|------|------|------|--------|
| POST | /order/create/ | 基于购物车批量创建 | 3000 |
| POST | /order/direct/ | 直接购买 | 3000 |
错误：3400 参数缺失/非法；3401 业务失败

---
## 7. 评论模块 Review
基础路由 /review/ (ViewSet)
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /review/ | 列表（分页） |
| POST | /review/ | 创建 |
| GET | /review/{id}/ | 详情 |
| PATCH | /review/{id}/ | 部分更新 |
| PUT | /review/{id}/ | 全量更新 |
| DELETE | /review/{id}/ | 软删除 |
| GET | /review/user/{user_id}/ | 按用户 |
| GET | /review/product/{product_id}/ | 按商品 |
| GET | /review/store/{store_id}/ | 按店铺 |

创建字段：order_item, content, rating, images(字符串列表，可空) —— 其余依据订单明细自动推导。

返回扩展：user_id, user_username, user_avatar_url(前缀补全)，images 统一为列表。

成功码：
- 列表/详情：5000
- 创建：5001
- 更新：5002
- 删除：5003

---
## 8. 图片 URL 规则
- settings.IMAGE_URL 作为基础前缀（默认 http://localhost:8000/）
- ProductSerializer 自动补全 thumbnail 与 gallery（如可解析）
- 评论中的 user_avatar_url 自动补前缀；用户注册传入相对路径也会在读取时补全
- 商品搜索接口 results[].thumbnail 已补全

---
## 9. JWT 认证说明
- 生成：登录成功返回 data.token
- 算法：HS256，载荷：{ user_id, username, exp }
- 有效期：默认 7 天
- 传递方式（任一）：
  1. Header: Token: <jwt>
  2. Query: ?token=<jwt>
- 当前 request.user 为 AnonymousUser（可后续扩展实际用户解析）
- 过期 / 无效：抛出 AuthenticationFailed → 前端清除本地 token 并跳转 /login
- 未实现刷新 token；需要可新增 refresh_token 与单独刷新接口

---
## 10. 表单 & 校验规范
| 字段 | 规则 | 错误示例 |
|------|------|----------|
| phone | ^1\d{10}$ | 手机号格式不正确 |
| password | >=6 且含字母+数字 | 密码至少6位 / 密码需包含字母和数字 |
| code | 6 位数字（随机） | 验证码错误 / 验证码已失效 |
| images (评论) | 字符串数组 | images 仅支持列表 |
| page/page_size | 正整数 | 参数格式错误 / page 不能小于1 |

提示风格：中文短句，不含技术栈实现细节。

---
## 11. 前端交互建议
| 场景 | 建议处理 |
|------|----------|
| 未登录访问受限页 | 跳转 /login?next=<原路径> |
| 登录成功 | 若有 next 优先回跳；否则首页或个人中心 |
| 注册成功 | 引导到 /login（当前未自动登录） |
| 重置密码成功 | 跳转 /login + Toast "密码已更新" |
| Token 过期 | 清除本地 token → /login |
| 频繁获取验证码 | 倒计时灰显按钮 60s |

受限页面示例：订单创建/列表、地址管理、评论创建、结算页。

---
## 12. HTTP 调试示例片段
(完整示例见 http/pycharm.http)
```
### 发送验证码
POST {{base_url}}/user/send_code/
Content-Type: application/json

{"phone":"13800000000","scene":"register"}

### 注册
POST {{base_url}}/user/register/
Content-Type: application/json

{"phone":"13800000000","password":"Abc123","code":"123456","username":"tom"}

### 登录
POST {{base_url}}/user/login/
Content-Type: application/json
{"phone":"13800000000","password":"Abc123"}

### 搜索
GET {{base_url}}/product/search/?q=蓝&sort=4&page=1&page_size=10
```

---
## 13. 错误码（节选）
| code | 常量 | 场景 |
|------|------|------|
| 0 | SUCCESS | 通用成功（规划后期统一） |
| 1000/1001/1002 | CATEGORY_* | 分类成功 |
| 1400 | CATEGORY_PARAM_ERROR | 分类/商品参数错误/缺参 |
| 2000 | PRODUCT_TAG_LIST_OK | 标签商品列表 |
| 2001 | PRODUCT_DETAIL_OK | 商品详情 |
| 2002 | PRODUCT_SEARCH_OK | 商品搜索成功 |
| 2400 | PRODUCT_NOT_FOUND_OR_PARAM_ERROR | 商品不存在 / 页面越界 |
| 3000 | CART_LIST_OK / ORDER_CREATE_OK_ALIAS | 购物车列表 / 订单创建 |
| 3001 | CART_ADD_OR_UPDATE_OK | 加/更新购物车 |
| 3002 | CART_ITEM_REMOVED | 条目被移除 |
| 3400 | CART_OR_ORDER_PARAM_ERROR | 购物车/订单参数错误 |
| 3401 | ORDER_CREATE_FAILED | 下单失败 |
| 4000 | USER_ACTION_OK | 用户成功通用 |
| 4400 | USER_PARAM_INVALID | 用户参数非法 |
| 4401~4406 | LOGIN_* | 登录相关错误 |
| 4404 | USER_NOT_FOUND | 用户不存在 |
| 4407 | USER_UPDATE_FAILED | 用户更新失败 |
| 4500 | VERIFICATION_CODE_SENT | 验证码发送成功 |
| 4501 | VERIFICATION_CODE_THROTTLED | 验证码发送过快 |
| 4502 | VERIFICATION_CODE_INVALID | 验证码错误 |
| 4503 | VERIFICATION_CODE_EXPIRED | 验证码失效 |
| 4504 | PASSWORD_RESET_OK | 密码重置成功 |
| 4505 | PASSWORD_RESET_PHONE_NOT_FOUND | 手机未注册 |
| 5000~5003 | REVIEW_* | 评论列表/创建/更新/删除 |
| 5400 | REVIEW_PARAM_ERROR | 评论参数错误 |
| 5404 | REVIEW_NOT_FOUND | 评论不存在 |
| 9000 | INTERNAL_ERROR | 内部错误预留 |

---
## 14. Roadmap & 后续建议
1. 引入 refresh token（短 access + 长 refresh）
2. 注册成功自动登录（统一体验）
3. 统一权限：IsOwner / IsAuthenticated 应用到购物车、订单、评论创建
4. 短信网关接入（替换控制台验证码）
5. 错误码最终统一成功=0，其余>0
6. 全局异常捕获映射 9000 及日志链路 ID
7. 商品搜索增加多字段过滤（价格区间/店铺/标签）与高亮

---
## 15. 版本记录
| 版本 | 日期 | 说明 |
|------|------|------|
| 0.1.0 | 2025-08-22 | 初始接口文档 |
| 0.1.1 | 2025-08-22 | 响应码集中、评论用户信息、商品搜索 |
| 0.1.2 | 2025-08-23 | 验证码/重置密码/注册验证码校验、文档整合 |

---
> 请在修改接口后及时同步本文档；错误码新增遵循既定区间策略。
