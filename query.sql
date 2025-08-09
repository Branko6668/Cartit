show tables;
use shopping;
SHOW CREATE TABLE user;
drop table product;
DROP TABLE IF EXISTS user, user_address, main_menu, sub_menu, product, comment, store;
insert into sub_menu (main_menu_id, sub_menu_name, sub_menu_class) values (1, '牛逼','cc'), (1, '蔬菜','df');