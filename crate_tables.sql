-- user 用户身份信息表
create table user (
    id int unsigned not null auto_increment comment '用户ID，主键，自增',
    name varchar(255) collate utf8mb4_general_ci default null comment '用户姓名',
    birthday datetime default null comment '用户生日',
    phone varchar(20) collate utf8mb4_general_ci default null comment '用户手机号',
    gender enum('male', 'female', 'other') default 'other' comment '用户性别',
    email varchar(255) collate utf8mb4_general_ci default null comment '用户邮箱',
    password varchar(255) collate utf8mb4_general_ci default null comment '用户密码',
    avatar_url varchar(255) collate utf8mb4_general_ci default null comment '用户头像 url',
    create_time datetime default current_timestamp comment '账号创建时间',
    primary key (id),
    unique index idx_phone (phone)
) engine = innodb default charset = utf8mb4 collate utf8mb4_general_ci comment = '用户信息表，存储用户的基本身份数据';

-- user_address 用户地址管理表
create table user_address (
    id int unsigned not null auto_increment comment '主键id',
    user_id INT UNSIGNED NOT NULL COMMENT '用户ID，唯一标识，并且关联 user 表',
    recipient_name varchar(255) collate utf8mb4_general_ci default null comment '收件人名称',
    recipient_phone varchar(20) collate utf8mb4_general_ci default null comment '收件人电话号码',
    province varchar(255) collate utf8mb4_general_ci default null comment '省',
    city varchar(255) collate utf8mb4_general_ci default null comment '市',
    district varchar(255) collate utf8mb4_general_ci default null comment '县/地区',
    street_address varchar(255) collate utf8mb4_general_ci default null comment '街道',
    detailed_address varchar(255) collate utf8mb4_general_ci default null comment '详细地址',
    is_default boolean default false comment 'true为该用户默认地址',
    create_time datetime default current_timestamp comment '地址创建时间',
    primary key (id)
) engine = innodb default charset=utf8mb4 collate utf8mb4_general_ci comment = '用户地址管理表，存储用户的地址';

-- main_menu 主导航菜单表
create table main_menu (
    id int unsigned not null auto_increment comment '主菜单id，主键',
    main_menu_name varchar(50) not null comment '主菜单名称',
    main_menu_class int unsigned not null comment '主菜单分类',
    primary key (id),
    index idx_main_menu_class (main_menu_class)
) engine = innodb default charset=utf8mb4 collate utf8mb4_general_ci comment = '主导航菜单表，存储不同分类的主菜单';

-- sub_menu 二级菜单表
create table sub_menu (
    id int unsigned not null auto_increment comment '二级菜单id，主键',
    main_menu_id int unsigned not null comment '主菜单id，关联 main_menu 表',
    sub_menu_name varchar(50) not null comment '二级菜单名称',
    sub_menu_class varchar(50) not null comment '二级菜单分类',
    primary key (id),
    index idx_main_menu (main_menu_id),
    foreign key (main_menu_id) references main_menu(id) on delete cascade
) engine = innodb default charset=utf8mb4 collate utf8mb4_general_ci comment = '二级菜单表，关联主菜单';

-- comment 商品评价表
create table comment (
    id int unsigned not null auto_increment comment '评论id，主键',
    user_id int unsigned not null comment '用户id，关联 user 表',
    product_id int unsigned not null comment '商品id，关联 product 表',
    content text not null comment '评论内容',
    rating tinyint unsigned not null default 5 check (rating between 1 and 5) comment '评分(1-5星)',
    reply_to int unsigned default null comment '回复的父评论id',
    reply_count int unsigned default 0 comment '该评论的回复数量',
    create_time datetime default current_timestamp comment '创建时间',
    primary key (id),
    index idx_product (product_id),
    index idx_user_product (user_id, product_id),
    foreign key (user_id) references user(id) on delete cascade,
    foreign key (product_id) references product(id) on delete cascade
) engine = innodb default charset=utf8mb4 collate utf8mb4_general_ci comment = '商品评价表，存储用户对商品的评论信息';

-- 店铺信息表
create table store (
    id int unsigned not null auto_increment comment '店铺id，主键',
    store_name varchar(255) not null comment '店铺名称',
    owner_id int unsigned not null comment '店铺所有者用户id，关联 user 表',
    description text comment '店铺介绍',
    create_time datetime default current_timestamp comment '创建时间',
    primary key (id),
    index idx_owner (owner_id),
    foreign key (owner_id) references user(id) on delete cascade
) engine = innodb default charset=utf8mb4 collate utf8mb4_general_ci comment = '店铺信息表，存储店铺数据';

-- 商品信息表
create table product (
  id int unsigned not null auto_increment comment '商品id，主键',
  category_id int unsigned not null comment '分类id，关联 sub_menu 表',
  store_id int unsigned not null comment '店铺id，关联 store 表',
  name varchar(255) collate utf8mb4_general_ci not null comment '商品名称',
  description text collate utf8mb4_general_ci comment '商品详情描述',
  price decimal(10,2) not null comment '商品价格(精度到分)',
  stock int unsigned not null default 0 comment '库存数量',
  thumbnail varchar(255) collate utf8mb4_general_ci default null comment '商品缩略图 url',
  status enum('on_sale','off_sale','out_of_stock') collate utf8mb4_general_ci default 'on_sale' comment '商品状态',
  sales_volume int unsigned default 0 comment '累计销量',
  view_count int unsigned default 0 comment '浏览次数',
  create_time datetime default current_timestamp comment '创建时间',
  update_time datetime default current_timestamp on update current_timestamp comment '更新时间',
  primary key (id),
  key idx_category (category_id),
  key idx_store (store_id),
  key idx_price (price),
  fulltext key idx_search (name,description),
  constraint product_ibfk_1 foreign key (store_id) references store (id) on delete cascade,
  constraint product_chk_1 check (price >= 0)
) engine=innodb default charset=utf8mb4 collate=utf8mb4_general_ci comment='商品核心信息表，存储商品的基本属性及销售数据';
