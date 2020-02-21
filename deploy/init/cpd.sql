create database if not exists news default character set utf8mb4 collate utf8mb4_unicode_ci;

use news;

create table if not exists cpd_news
(
        news_id varchar(40) not null unique primary key comment '',
        title varchar(255) not null comment '',
        category varchar(10) not null comment '',
        source varchar(50) not null comment '',
        publish_date varchar(30) not null comment '',
        page_total int not null comment '',
        duplication varchar(40) not null default '',
        entry_time datetime not null default CURRENT_TIMESTAMP  comment ''
);

create table if not exists cpd_news_content
(
        news_id varchar(40) not null comment '',
        request_id varchar(40) not null unique primary key comment '',
        url varchar(255) not null comment '',
        content mediumtext not null comment '',
        page int not null comment '',
        entry_time datetime not null default CURRENT_TIMESTAMP  comment '',
        FOREIGN KEY fk_news(news_id)
        REFERENCES cpd_news(news_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);