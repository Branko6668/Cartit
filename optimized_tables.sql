
-- 用户信息表
CREATE TABLE user (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '用户ID，主键',
    username VARCHAR(50) NOT NULL COMMENT '用户名（登录用）',
    name VARCHAR(100) DEFAULT NULL COMMENT '真实姓名',
    phone VARCHAR(11) DEFAULT NULL COMMENT '手机号',
    email VARCHAR(100) DEFAULT NULL COMMENT '邮箱',
    password VARCHAR(255) NOT NULL COMMENT '密码（加密存储）',
    avatar_url VARCHAR(500) DEFAULT NULL COMMENT '头像URL',
    gender ENUM('male', 'female', 'other') DEFAULT 'other' COMMENT '性别',
    birthday DATE DEFAULT NULL COMMENT '生日',
    status ENUM('active', 'disabled') DEFAULT 'active' COMMENT '账户状态',
    is_deleted TINYINT(1) DEFAULT 0 COMMENT '是否删除（软删除）',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (id),
    UNIQUE KEY uk_username (username),
    UNIQUE KEY uk_phone (phone),
    UNIQUE KEY uk_email (email),
    KEY idx_status (status),
    KEY idx_create_time (create_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户信息表';

-- 用户地址表
CREATE TABLE user_address (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '地址ID',
    user_id INT UNSIGNED NOT NULL COMMENT '用户ID',
    recipient_name VARCHAR(50) NOT NULL COMMENT '收件人姓名',
    recipient_phone VARCHAR(11) NOT NULL COMMENT '收件人电话',
    province VARCHAR(20) NOT NULL COMMENT '省份',
    city VARCHAR(20) NOT NULL COMMENT '城市',
    district VARCHAR(20) NOT NULL COMMENT '区县',
    detail_address VARCHAR(200) NOT NULL COMMENT '详细地址',
    postal_code VARCHAR(10) DEFAULT NULL COMMENT '邮政编码',
    is_default TINYINT(1) DEFAULT 0 COMMENT '是否默认地址',
    is_deleted TINYINT(1) DEFAULT 0 COMMENT '是否删除',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (id),
    KEY idx_user_id (user_id),
    KEY idx_is_default (user_id, is_default),
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户地址表';

-- 商品分类表（简化为单层分类）
CREATE TABLE category (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '分类ID',
    parent_id INT UNSIGNED DEFAULT 0 COMMENT '父分类ID，0表示顶级分类',
    name VARCHAR(50) NOT NULL COMMENT '分类名称',
    sort_order INT DEFAULT 0 COMMENT '排序顺序',
    icon_url VARCHAR(500) DEFAULT NULL COMMENT '分类图标URL',
    is_active TINYINT(1) DEFAULT 1 COMMENT '是否启用',
    is_deleted TINYINT(1) DEFAULT 0 COMMENT '是否删除',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (id),
    KEY idx_parent_id (parent_id),
    KEY idx_sort_order (sort_order),
    KEY idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='商品分类表';

-- 店铺信息表
CREATE TABLE store (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '店铺ID',
    store_name VARCHAR(100) NOT NULL COMMENT '店铺名称',
    owner_id INT UNSIGNED NOT NULL COMMENT '店主用户ID',
    description TEXT COMMENT '店铺描述',
    logo_url VARCHAR(500) DEFAULT NULL COMMENT '店铺Logo URL',
    contact_phone VARCHAR(11) DEFAULT NULL COMMENT '联系电话',
    business_license VARCHAR(100) DEFAULT NULL COMMENT '营业执照号',
    status ENUM('pending', 'active', 'suspended', 'closed') DEFAULT 'pending' COMMENT '店铺状态',
    is_deleted TINYINT(1) DEFAULT 0 COMMENT '是否删除',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (id),
    UNIQUE KEY uk_store_name (store_name),
    KEY idx_owner_id (owner_id),
    KEY idx_status (status),
    FOREIGN KEY (owner_id) REFERENCES user(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='店铺信息表';

-- 商品信息表
CREATE TABLE product (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '商品ID',
    category_id INT UNSIGNED NOT NULL COMMENT '分类ID',
    store_id INT UNSIGNED NOT NULL COMMENT '店铺ID',
    name VARCHAR(200) NOT NULL COMMENT '商品名称',
    subtitle VARCHAR(500) DEFAULT NULL COMMENT '商品副标题',
    description TEXT COMMENT '商品详情描述',
    price DECIMAL(12,2) NOT NULL COMMENT '售价',
    original_price DECIMAL(12,2) DEFAULT NULL COMMENT '原价',
    cost_price DECIMAL(12,2) DEFAULT NULL COMMENT '成本价',
    stock INT UNSIGNED DEFAULT 0 COMMENT '库存数量',
    min_stock INT UNSIGNED DEFAULT 0 COMMENT '最低库存预警',
    weight DECIMAL(8,3) DEFAULT NULL COMMENT '商品重量（kg）',
    thumbnail VARCHAR(500) DEFAULT NULL COMMENT '缩略图URL',
    gallery TEXT COMMENT '商品图片集（JSON格式）',
    status ENUM('draft', 'on_sale', 'off_sale', 'out_of_stock') DEFAULT 'draft' COMMENT '商品状态',
    sales_count INT UNSIGNED DEFAULT 0 COMMENT '销售数量',
    view_count INT UNSIGNED DEFAULT 0 COMMENT '浏览次数',
    sort_order INT DEFAULT 0 COMMENT '排序',
    seo_title VARCHAR(200) DEFAULT NULL COMMENT 'SEO标题',
    seo_keywords VARCHAR(500) DEFAULT NULL COMMENT 'SEO关键词',
    seo_description VARCHAR(500) DEFAULT NULL COMMENT 'SEO描述',
    is_hot TINYINT(1) DEFAULT 0 COMMENT '是否热门商品',
    is_new TINYINT(1) DEFAULT 0 COMMENT '是否新品',
    is_recommend TINYINT(1) DEFAULT 0 COMMENT '是否推荐商品',
    is_deleted TINYINT(1) DEFAULT 0 COMMENT '是否删除',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (id),
    KEY idx_category_id (category_id),
    KEY idx_store_id (store_id),
    KEY idx_price (price),
    KEY idx_status (status),
    KEY idx_sales_count (sales_count),
    KEY idx_create_time (create_time),
    KEY idx_is_hot (is_hot),
    KEY idx_is_new (is_new),
    KEY idx_is_recommend (is_recommend),
    FULLTEXT KEY ft_search (name, subtitle, description),
    FOREIGN KEY (category_id) REFERENCES category(id),
    FOREIGN KEY (store_id) REFERENCES store(id) ON DELETE CASCADE,
    CONSTRAINT chk_price CHECK (price >= 0),
    CONSTRAINT chk_stock CHECK (stock >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='商品信息表';

-- 购物车表
CREATE TABLE shopping_cart (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '购物车ID',
    user_id INT UNSIGNED NOT NULL COMMENT '用户ID',
    product_id INT UNSIGNED NOT NULL COMMENT '商品ID',
    quantity INT UNSIGNED NOT NULL DEFAULT 1 COMMENT '商品数量',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '加入时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (id),
    UNIQUE KEY uk_user_product (user_id, product_id),
    KEY idx_user_id (user_id),
    KEY idx_product_id (product_id),
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES product(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='购物车表';

-- 订单表
CREATE TABLE `order` (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '订单ID',
    order_no VARCHAR(32) NOT NULL COMMENT '订单编号',
    user_id INT UNSIGNED NOT NULL COMMENT '用户ID',
    store_id INT UNSIGNED NOT NULL COMMENT '店铺ID',
    total_amount DECIMAL(12,2) NOT NULL COMMENT '订单总金额',
    discount_amount DECIMAL(12,2) DEFAULT 0 COMMENT '优惠金额',
    freight_amount DECIMAL(12,2) DEFAULT 0 COMMENT '运费',
    actual_amount DECIMAL(12,2) NOT NULL COMMENT '实付金额',
    status ENUM('pending_payment', 'paid', 'shipped', 'delivered', 'completed', 'cancelled', 'refunded') DEFAULT 'pending_payment' COMMENT '订单状态',
    payment_method ENUM('alipay', 'wechat', 'bank_card', 'cash') DEFAULT NULL COMMENT '支付方式',
    payment_time DATETIME DEFAULT NULL COMMENT '支付时间',
    ship_time DATETIME DEFAULT NULL COMMENT '发货时间',
    deliver_time DATETIME DEFAULT NULL COMMENT '收货时间',
    recipient_name VARCHAR(50) NOT NULL COMMENT '收件人姓名',
    recipient_phone VARCHAR(11) NOT NULL COMMENT '收件人电话',
    recipient_address VARCHAR(500) NOT NULL COMMENT '收件地址',
    remark TEXT COMMENT '订单备注',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (id),
    UNIQUE KEY uk_order_no (order_no),
    KEY idx_user_id (user_id),
    KEY idx_store_id (store_id),
    KEY idx_status (status),
    KEY idx_create_time (create_time),
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (store_id) REFERENCES store(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='订单表';

-- 订单商品明细表
CREATE TABLE order_item (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '明细ID',
    order_id INT UNSIGNED NOT NULL COMMENT '订单ID',
    product_id INT UNSIGNED NOT NULL COMMENT '商品ID',
    product_name VARCHAR(200) NOT NULL COMMENT '商品名称（快照）',
    product_image VARCHAR(500) DEFAULT NULL COMMENT '商品图片（快照）',
    price DECIMAL(12,2) NOT NULL COMMENT '商品单价（快照）',
    quantity INT UNSIGNED NOT NULL COMMENT '购买数量',
    total_amount DECIMAL(12,2) NOT NULL COMMENT '小计金额',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (id),
    KEY idx_order_id (order_id),
    KEY idx_product_id (product_id),
    FOREIGN KEY (order_id) REFERENCES `order`(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES product(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='订单商品明细表';

-- 商品评价表
CREATE TABLE product_review (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '评价ID',
    order_id INT UNSIGNED NOT NULL COMMENT '订单ID',
    order_item_id INT UNSIGNED NOT NULL COMMENT '订单商品明细ID',
    user_id INT UNSIGNED NOT NULL COMMENT '用户ID',
    product_id INT UNSIGNED NOT NULL COMMENT '商品ID',
    store_id INT UNSIGNED NOT NULL COMMENT '店铺ID',
    content TEXT NOT NULL COMMENT '评价内容',
    rating TINYINT UNSIGNED NOT NULL DEFAULT 5 COMMENT '评分（1-5星）',
    images TEXT COMMENT '评价图片（JSON格式）',
    reply_content TEXT DEFAULT NULL COMMENT '商家回复内容',
    reply_time DATETIME DEFAULT NULL COMMENT '回复时间',
    is_anonymous TINYINT(1) DEFAULT 0 COMMENT '是否匿名评价',
    is_deleted TINYINT(1) DEFAULT 0 COMMENT '是否删除',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (id),
    UNIQUE KEY uk_order_item (order_item_id),
    KEY idx_user_id (user_id),
    KEY idx_product_id (product_id),
    KEY idx_store_id (store_id),
    KEY idx_rating (rating),
    KEY idx_create_time (create_time),
    FOREIGN KEY (order_id) REFERENCES `order`(id),
    FOREIGN KEY (order_item_id) REFERENCES order_item(id),
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (product_id) REFERENCES product(id),
    FOREIGN KEY (store_id) REFERENCES store(id),
    CONSTRAINT chk_rating CHECK (rating BETWEEN 1 AND 5)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='商品评价表';

-- 支付记录表
CREATE TABLE payment (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '支付记录ID',
    payment_no VARCHAR(32) NOT NULL COMMENT '支付流水号',
    order_id INT UNSIGNED NOT NULL COMMENT '订单ID',
    user_id INT UNSIGNED NOT NULL COMMENT '用户ID',
    amount DECIMAL(12,2) NOT NULL COMMENT '支付金额',
    payment_method ENUM('alipay', 'wechat', 'bank_card', 'cash') NOT NULL COMMENT '支付方式',
    payment_channel VARCHAR(50) DEFAULT NULL COMMENT '支付渠道',
    transaction_id VARCHAR(100) DEFAULT NULL COMMENT '第三方交易号',
    status ENUM('pending', 'success', 'failed', 'cancelled') DEFAULT 'pending' COMMENT '支付状态',
    paid_time DATETIME DEFAULT NULL COMMENT '支付完成时间',
    notify_time DATETIME DEFAULT NULL COMMENT '回调通知时间',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (id),
    UNIQUE KEY uk_payment_no (payment_no),
    KEY idx_order_id (order_id),
    KEY idx_user_id (user_id),
    KEY idx_status (status),
    KEY idx_create_time (create_time),
    FOREIGN KEY (order_id) REFERENCES `order`(id),
    FOREIGN KEY (user_id) REFERENCES user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='支付记录表';
