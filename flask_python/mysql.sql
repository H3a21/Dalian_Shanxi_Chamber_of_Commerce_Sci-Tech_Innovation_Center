-- 创建项目的 mysql 数据库 smart_mine_db
create database smart_mine_db;

-- 使用数据库
USE smart_mine_db;

-- 在数据库中创建 users 表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '用户ID，主键',
    username VARCHAR(50) NULL UNIQUE COMMENT '用户名，唯一标识',
    real_name VARCHAR(30)  NULL COMMENT '真实姓名',
    id_card VARCHAR(18)  NULL UNIQUE COMMENT '身份证号（唯一）',
    phone VARCHAR(20) NOT NULL UNIQUE COMMENT '手机号，唯一标识',
    password_hash VARCHAR(255) NOT NULL COMMENT '加密后的密码',
    role VARCHAR(20) NOT NULL DEFAULT 'common' COMMENT '用户角色：common-普通用户，admin-管理员，service-客服',
    status TINYINT(1) NOT NULL DEFAULT 1 COMMENT '用户状态：0-禁用，1-正常'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- 创建消息表 messages
CREATE TABLE `messages` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '消息唯一ID',
  `send_user_id` INT NOT NULL DEFAULT 0 COMMENT '发送者ID（0=系统消息）',
  `receive_user_id` INT NOT NULL COMMENT '接收消息用户ID',
  `msg_type` VARCHAR(20) NOT NULL COMMENT '消息类型：audit=待审核提醒、result=审核结果通知、admin=管理员通知',
  `biz_type` VARCHAR(20) NOT NULL COMMENT '业务类型：achievement=成果、demand=需求',
  `biz_id` VARCHAR(50) NOT NULL COMMENT '对应成果ID/需求ID',
  `content` VARCHAR(255) NOT NULL COMMENT '消息内容（如：待审核、审核不通过）',
  `is_read` TINYINT NOT NULL DEFAULT 0 COMMENT '是否已读：0=未读、1=已读',
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '消息发送时间',
  -- 主键约束
  PRIMARY KEY (`id`),
  -- 业务查询索引（优化接收用户+已读状态查询速度）
  INDEX `idx_receive_isread` (`receive_user_id`, `is_read`),
  -- 业务关联索引（优化业务类型+业务ID查询）
  INDEX `idx_biz_type_id` (`biz_type`, `biz_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统消息通知表';

-- 创建审核记录表 audit_logs
CREATE TABLE `audit_logs` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '审核记录ID',
  `biz_type` VARCHAR(20) NOT NULL COMMENT '业务类型：achievement=成果、demand=需求',
  `biz_id` INT NOT NULL COMMENT '被审核的成果ID/需求ID',
  `admin_id` INT NOT NULL COMMENT '执行审核的管理员ID',
  `result` TINYINT NOT NULL COMMENT '审核结果：rejected',
  `reason` VARCHAR(255) NULL DEFAULT NULL COMMENT '不通过原因（通过可为空）',
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '审核时间',
  -- 主键约束
  PRIMARY KEY (`id`),
  -- 业务索引：根据业务类型+业务ID快速查询审核记录
  INDEX `idx_biz_type_id` (`biz_type`, `biz_id`),
  -- 管理员查询索引：根据管理员ID查询审核记录
  INDEX `idx_admin_id` (`admin_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='审核记录表';

CREATE TABLE `editor_user` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `account` varchar(50) NOT NULL COMMENT '登录账号',
  `password` varchar(255) NOT NULL COMMENT '登录密码(生产环境建议存哈希值)',
  `role` varchar(20) DEFAULT 'editor' COMMENT '角色标识',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_account` (`account`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='编辑器专属用户表';

CREATE TABLE `dynamic_pages` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `page_path` varchar(100) NOT NULL COMMENT '页面访问路径 (例如: about-us, custom-demand)',
  `page_name` varchar(100) NOT NULL COMMENT '页面名称 (例如: 关于我们)',
  `html_content` longtext COMMENT 'GrapesJS生成的HTML代码',
  `css_content` longtext COMMENT 'GrapesJS生成的CSS代码',
  `gjs_data` longtext COMMENT 'GrapesJS的原始JSON配置(用于二次打开继续编辑)',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_page_path` (`page_path`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='动态可编辑页面表';

CREATE TABLE `site_configs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `config_key` varchar(50) NOT NULL COMMENT '配置键 (如 site_name)',
  `config_value` text COMMENT '配置内容',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_key` (`config_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='全局站点配置表';

 ALTER TABLE dynamic_pages MODIFY COLUMN html_content LONGTEXT COMMENT 'GrapesJS生成的HTML代码';
  ALTER TABLE dynamic_pages MODIFY COLUMN css_content LONGTEXT COMMENT 'GrapesJS生成的CSS代码';
  ALTER TABLE dynamic_pages MODIFY COLUMN gjs_data LONGTEXT COMMENT 'GrapesJS的原始JSON配置(用于二次打开继续编辑)';