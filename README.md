先把需求对齐，然后给出后端接口完善建议，便于你直接开工。

## 我需要的关键信息
- 是否有 SKU/规格？若有：需要 `sku_id/sku_text/库存/价格`。
- 商品字段是否能返回：`product_image`、`unit_price`（现价）、`original_price`、`stock`、`max_per_order`、是否下架。
- 价格精度与币种：分/元，四舍五入规则。
- 结算流程：是否支持“只结算所选项”，以及“本项直接结算”如何落地（传 cart_item_ids 还是 product_id+quantity）。
- Token 使用：后端是否从 Token 解析 user，是否仍要求前端传 `user_id`（建议忽略前端的 user_id，以 Token 为准）。
- CORS：后端是否允许自定义请求头 `Token`（购物车必须携带 Token）。

## 接口设计与完善建议
现有接口：
- GET /shopping_cart/?user_id=1（建议后端改为“从 Token 获取用户”，忽略 user_id）
- POST /shopping_cart/ 添加商品

建议补充/调整：
1) 列表与汇总
- GET /shopping_cart/
  - 头：Token
  - 返回：{ code, msg, data: { items: [...], summary: {...} } }

2) 新增/增量添加/设定数量（合并为一个接口，控制行为）
- POST /shopping_cart/
  - 头：Token, Content-Type: application/json
  - 入参：{ product_id, sku_id?, quantity, mode?: 'add' | 'set' }（不传默认 add）
  - 语义：add 为在已有基础上增加；set 为直接设定为该数量
  - 返回：更新后的条目或整个列表（任选其一）

3) 修改条目（数量/选中）
- PATCH /shopping_cart/{id}/
  - 入参：{ quantity? , selected? }（支持只改其中一项）
  - 数量设为 0 可选择直接删除，或返回错误提示

4) 批量选择/取消选择
- POST /shopping_cart/select_all
  - 入参：{ selected: true|false }

5) 批量更新（可选，优化并发）
- POST /shopping_cart/batch_update
  - 入参：{ items: [{ id, quantity?, selected? }, ...] }

6) 删除与清空
- DELETE /shopping_cart/{id}/
- POST /shopping_cart/clear
  - 入参：{ only_selected: true|false }（true 表示仅清空已选）

7) 汇总（可选；也可直接随列表返回）
- GET /shopping_cart/summary

8) 本项直接结算（配合订单预览）
- POST /order/preview_from_cart
  - 入参：{ cart_item_ids: [id] }（单项结算传一个 id；去结算传“当前已选”）
  - 返回：订单预览（实付、配送费、优惠等），用于确认页

## 前端行为对齐（与你的页面 UI 一致）
- 顶部表头五列：全选 | 商品信息（图+名+SKU）| 单价 | 数量（步进器）| 小计 | 操作（删除/本项结算）
- 中间列表：checkbox 控制 selected，数量步进器联动 PATCH
- 底部汇总栏：
  - 删除所选：收集选中的 id → 批量 DELETE（或循环）
  - 清空购物车：POST /clear
  - 信息展示：selected_count / selected_amount（来自 summary 或本地计算）
  - 去结算：调 /order/preview_from_cart（传选中项 id 列表）→ 跳转确认页
- 搜索页“加入购物车”：POST /shopping_cart/ { product_id, quantity:1, mode:'add' }
- 商品详情“加入购物车”：POST /shopping_cart/ { product_id, sku_id?, quantity, mode:'add' }
- “本项直接结算”：POST /order/preview_from_cart { cart_item_ids:[当前项 id] }

## 校验与交互细节
- 数量边界：1 ≤ quantity ≤ min(stock, max_per_order)
- 库存/下架：禁用步进器并提示；可显示“已下架/库存不足”标记
- 乐观更新：数量调整可先本地更新 UI，再按返回结果修正；或保守做法：接口成功后再更新
- 统一错误提示：沿用你现在的 `normalizedMessage`，对 401 自动跳登录（带 next 回跳）
- Token/CORS：购物车与订单接口必须带 `Token`；确保后端 CORS 允许 `Token` 头

## 我需要你补充/确认
- 是否有 SKU；若有，请提供 `sku_id/sku_text` 字段定义与接口参数要求
- 价格字段与单位（是否返回 `unit_price`、`original_price`，单位分/元）
- 是否返回 `stock/max_per_order/is_off_shelf`
- 是否接受批量接口（`batch_update`、`clear only_selected`、`select_all`）
- 订单预览接口是否存在；若没有，按上面建议新建
- 错误码与成功码的最终约定（我可按你的码表在前端映射提示）

给定你当前的 communicate.md，最小改动即可上线的版本：
- 保持 GET /shopping_cart/（后台从 Token 取 user）
- 保持 POST /shopping_cart/，新增 `mode` 字段（add/set）
- 新增：
  - PATCH /shopping_cart/{id}/
  - DELETE /shopping_cart/{id}/
  - POST /shopping_cart/clear（only_selected）
  - POST /shopping_cart/select_all
- GET 列表返回时附带 `summary`，避免前端再遍历计算
- 后端 CORS 放行 `Token` 请求头
