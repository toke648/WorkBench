/*
 Navicat Premium Data Transfer

 Source Server         : localhost_3306
 Source Server Type    : MySQL
 Source Server Version : 50737
 Source Host           : localhost:3306
 Source Schema         : db_library

 Target Server Type    : MySQL
 Target Server Version : 50737
 File Encoding         : 65001

 Date: 11/04/2022 09:57:20
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for t_book
-- ----------------------------
DROP TABLE IF EXISTS `t_book`;
CREATE TABLE `t_book`  (
  `isbn` char(17) CHARACTER SET gb2312 COLLATE gb2312_chinese_ci NOT NULL,
  `book_name` varchar(50) CHARACTER SET gb2312 COLLATE gb2312_chinese_ci NULL DEFAULT NULL,
  `book_author` varchar(20) CHARACTER SET gb2312 COLLATE gb2312_chinese_ci NULL DEFAULT NULL,
  `book_price` decimal(6, 1) NULL DEFAULT NULL,
  `press_id` char(3) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL,
  `book_copy` int(11) NULL DEFAULT NULL,
  `book_inventory` int(11) NULL DEFAULT NULL,
  PRIMARY KEY (`isbn`) USING BTREE,
  INDEX `press_id`(`press_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = gb2312 COLLATE = gb2312_chinese_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of t_book
-- ----------------------------
INSERT INTO `t_book` VALUES ('9-234-3345-223-34', 'mysql数据库技术', NULL, NULL, NULL, NULL, NULL);
INSERT INTO `t_book` VALUES ('9-234-567-567-345', 'C语言', NULL, NULL, NULL, NULL, NULL);
INSERT INTO `t_book` VALUES ('978-7-04-034745-6', '3DSMAX2012+VRAY室内效果图案例教程', '刘刚', 76.0, '103', 2, 1);
INSERT INTO `t_book` VALUES ('978-7-04-035413-3', 'Premiere Pro CS5.5案例教程', '李涛', 71.0, '103', 5, 2);
INSERT INTO `t_book` VALUES ('978-7-04-051483-4', '数据结构', '曾海', 38.0, '103', 3, 1);
INSERT INTO `t_book` VALUES ('978-7-04-052083-5', 'MySQL数据库技术', '周德伟 覃国蓉', 45.0, '103', 4, 1);
INSERT INTO `t_book` VALUES ('978-7-04-057974-1', '工业互联网网络运维', '胡春芬', 46.8, '103', 4, 2);
INSERT INTO `t_book` VALUES ('978-7-30-132878-1', '巧学巧用Excel', '安迪', 109.0, '102', 4, 2);
INSERT INTO `t_book` VALUES ('978-7-30-258643-2', 'Windows Server 2019 Active Directory配置指南', '戴有炜', 109.0, '101', 5, 1);
INSERT INTO `t_book` VALUES ('978-7-30-258643-3', '从零开始读懂量子力学', '戴瑾', 88.0, '102', 6, 3);
INSERT INTO `t_book` VALUES ('978-7-30-259190-0', '51单片机C语言学习之道', '孙鹏', 88.0, '101', 5, 2);
INSERT INTO `t_book` VALUES ('978-7-5106-8159-2', '思维导图作文法', '赵妮尔', 39.8, '104', 4, 4);
INSERT INTO `t_book` VALUES ('978-7-5677-3957-5', 'Python程序设计', NULL, NULL, NULL, NULL, NULL);
INSERT INTO `t_book` VALUES ('9787113267407', '中国神话故事', '于红', 24.5, '105', 3, 1);
INSERT INTO `t_book` VALUES ('9787121306662', '完美应用Ubuntu', '何晓龙', 85.0, '106', 4, 2);

-- ----------------------------
-- Table structure for t_borrow_record
-- ----------------------------
DROP TABLE IF EXISTS `t_borrow_record`;
CREATE TABLE `t_borrow_record`  (
  `borrow_id` char(6) CHARACTER SET gb2312 COLLATE gb2312_chinese_ci NOT NULL,
  `reader_id` char(6) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL,
  `isbn` char(17) CHARACTER SET gb2312 COLLATE gb2312_chinese_ci NULL DEFAULT NULL,
  `borrow_date` date NULL DEFAULT NULL,
  PRIMARY KEY (`borrow_id`) USING BTREE,
  INDEX `reader_id`(`reader_id`) USING BTREE,
  INDEX `isbn`(`isbn`) USING BTREE,
  CONSTRAINT `t_borrow_record_ibfk_1` FOREIGN KEY (`reader_id`) REFERENCES `t_reader` (`reader_id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `t_borrow_record_ibfk_2` FOREIGN KEY (`isbn`) REFERENCES `t_book` (`isbn`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = latin1 COLLATE = latin1_swedish_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of t_borrow_record
-- ----------------------------
INSERT INTO `t_borrow_record` VALUES ('220401', '101101', '9-234-567-567-345', '2022-04-04');

-- ----------------------------
-- Table structure for t_press
-- ----------------------------
DROP TABLE IF EXISTS `t_press`;
CREATE TABLE `t_press`  (
  `press_id` char(3) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL,
  `press_name` varchar(50) CHARACTER SET gb2312 COLLATE gb2312_chinese_ci NULL DEFAULT NULL,
  `website` varchar(100) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL,
  `postcode` char(6) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL,
  `press_telephone` varchar(20) CHARACTER SET gb2312 COLLATE gb2312_chinese_ci NULL DEFAULT NULL,
  `press_email` varchar(50) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL,
  `press_address` varchar(100) CHARACTER SET gb2312 COLLATE gb2312_chinese_ci NULL DEFAULT NULL,
  PRIMARY KEY (`press_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = latin1 COLLATE = latin1_swedish_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of t_press
-- ----------------------------
INSERT INTO `t_press` VALUES ('101', '清华大学出版社', 'http://www.tup.tsinghua.edu.cn/', '100084', '010-62772015', 'zhiliang@tup.tsinghua.edu.cn', '北京市海淀区清华园街道双清路30号学研大厦A座');
INSERT INTO `t_press` VALUES ('102', '北京大学出版社', 'www.pup.cn', '100871', '021-62752032', 'zpup@pup.cn', '中国北京市海淀区成府路205号');
INSERT INTO `t_press` VALUES ('103', '高等教育出版社', 'https://www.hep.com.cn/aboutus', '100120', '010-58581118', 'gjdzfwb@pub.hep.cn', '北京市西城区德外大街4号');
INSERT INTO `t_press` VALUES ('104', '现代教育出版社', 'http://www.xdjycbs.com/', '100120', '010-64251256', 'admin@xdjycbs.com', '北京市东城区鼓楼外大街26号荣宝大厦三层');
INSERT INTO `t_press` VALUES ('105', '中国铁道出版社', 'http://www.tdpress.com/', '100054', '010-63549459', 'fx@tdpress.com', '北京市西城区右安门西街8号');
INSERT INTO `t_press` VALUES ('106', '电子工业出版社', 'https://www.phei.com.cn/', '100036', '020-88258888', 'support@phei.com.cn', '北京市万寿路南口金家村288号');

-- ----------------------------
-- Table structure for t_reader
-- ----------------------------
DROP TABLE IF EXISTS `t_reader`;
CREATE TABLE `t_reader`  (
  `reader_id` char(6) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL,
  `reader_name` varchar(50) CHARACTER SET gb2312 COLLATE gb2312_chinese_ci NULL DEFAULT NULL,
  `reader_sex` char(2) CHARACTER SET gb2312 COLLATE gb2312_chinese_ci NULL DEFAULT NULL,
  `reader_birthday` date NULL DEFAULT NULL,
  `reader_borrowtotal` int(11) NULL DEFAULT 0,
  PRIMARY KEY (`reader_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = latin1 COLLATE = latin1_swedish_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of t_reader
-- ----------------------------
INSERT INTO `t_reader` VALUES ('101101', '于敏', '男', '1926-08-16', NULL);
INSERT INTO `t_reader` VALUES ('101102', '申纪兰', '女', '1929-12-29', NULL);
INSERT INTO `t_reader` VALUES ('101103', '孙家栋', '男', '1929-04-08', NULL);
INSERT INTO `t_reader` VALUES ('101104', '李延年', '男', '1928-11-01', NULL);
INSERT INTO `t_reader` VALUES ('101105', '张富清', '男', '1924-12-01', NULL);
INSERT INTO `t_reader` VALUES ('101106', '袁隆平', '男', '1930-09-07', NULL);
INSERT INTO `t_reader` VALUES ('101107', '黄旭华', '男', '1924-02-24', NULL);
INSERT INTO `t_reader` VALUES ('101108', '屠呦呦', '女', '1930-12-30', NULL);
INSERT INTO `t_reader` VALUES ('101109', '钟南山', '男', '1936-10-20', NULL);

-- ----------------------------
-- Table structure for t_return_record
-- ----------------------------
DROP TABLE IF EXISTS `t_return_record`;
CREATE TABLE `t_return_record`  (
  `return_id` char(9) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL,
  `borrow_id` char(6) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL,
  `return_date` date NULL DEFAULT NULL,
  `ISBN` char(17) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL,
  `borrow_date` date NULL DEFAULT NULL
) ENGINE = InnoDB CHARACTER SET = latin1 COLLATE = latin1_swedish_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of t_return_record
-- ----------------------------

SET FOREIGN_KEY_CHECKS = 1;
