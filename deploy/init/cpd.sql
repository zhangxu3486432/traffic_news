create schema if not exists news collate utf8mb4_unicode_ci;

use news;

create table if not exists cpd_news
(
	news_id varchar(40) not null primary key comment '新闻 id',
	title varchar(255) not null comment '新闻标题',
	category varchar(10) not null comment '新闻分类',
	source varchar(50) not null comment '新闻来源',
	date varchar(30) not null comment '新闻日期',
	page_total int not null comment '新闻总页数',
	duplication varchar(40) not null default '',
	entry_time datetime not null default CURRENT_TIMESTAMP  comment '入库时间',
	constraint data_id_uindex
        unique (news_id)
);

create table if not exists cpd_news_content
(
	news_id varchar(40) not null comment '新闻 id',
	request_id varchar(40) not null primary key comment '请求 id',
	url varchar(255) not null comment '新闻链接',
	content mediumtext not null comment '新闻内容',
	page int not null comment '当前页数',
	entry_time datetime not null default CURRENT_TIMESTAMP  comment '入库时间',
	constraint data_id_uindex
        unique (request_id),
	FOREIGN KEY fk_news(news_id)
    REFERENCES cpd_news(news_id)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
);
