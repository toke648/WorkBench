/*
 Navicat Premium Data Transfer

 Source Server         : localhost_3306
 Source Server Type    : MySQL
 Source Server Version : 50737
 Source Host           : localhost:3306
 Source Schema         : yggl

 Target Server Type    : MySQL
 Target Server Version : 50737
 File Encoding         : 65001

 Date: 11/04/2022 09:00:22
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for departments
-- ----------------------------
DROP TABLE IF EXISTS `departments`;
CREATE TABLE `departments`  (
  `部门编号` char(3) CHARACTER SET gb2312 COLLATE gb2312_chinese_ci NOT NULL,
  `部门名称` char(20) CHARACTER SET gb2312 COLLATE gb2312_chinese_ci NOT NULL,
  `备注` text CHARACTER SET gb2312 COLLATE gb2312_chinese_ci NULL,
  PRIMARY KEY (`部门编号`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = gb2312 COLLATE = gb2312_chinese_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of departments
-- ----------------------------

-- ----------------------------
-- Table structure for employees
-- ----------------------------
DROP TABLE IF EXISTS `employees`;
CREATE TABLE `employees`  (
  `员工编号` char(6) CHARACTER SET gb2312 COLLATE gb2312_chinese_ci NOT NULL,
  `姓名` char(10) CHARACTER SET gb2312 COLLATE gb2312_chinese_ci NOT NULL,
  `学历` char(4) CHARACTER SET gb2312 COLLATE gb2312_chinese_ci NOT NULL,
  `出生日期` date NOT NULL,
  `性别` char(2) CHARACTER SET gb2312 COLLATE gb2312_chinese_ci NOT NULL,
  `工作年限` tinyint(2) NOT NULL,
  `地址` varchar(20) CHARACTER SET gb2312 COLLATE gb2312_chinese_ci NULL DEFAULT NULL,
  `电话号码` char(12) CHARACTER SET gb2312 COLLATE gb2312_chinese_ci NULL DEFAULT NULL,
  `员工部门号` char(3) CHARACTER SET gb2312 COLLATE gb2312_chinese_ci NULL DEFAULT NULL,
  PRIMARY KEY (`员工编号`) USING BTREE,
  INDEX `fk_depid`(`员工部门号`) USING BTREE,
  CONSTRAINT `fk_depid` FOREIGN KEY (`员工部门号`) REFERENCES `departments` (`部门编号`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = gb2312 COLLATE = gb2312_chinese_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of employees
-- ----------------------------

-- ----------------------------
-- Table structure for salary
-- ----------------------------
DROP TABLE IF EXISTS `salary`;
CREATE TABLE `salary`  (
  `员工编号` char(6) CHARACTER SET gb2312 COLLATE gb2312_chinese_ci NOT NULL,
  `收入` float(8, 2) NOT NULL,
  `支出` float(8, 2) NOT NULL,
  PRIMARY KEY (`员工编号`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = gb2312 COLLATE = gb2312_chinese_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of salary
-- ----------------------------

SET FOREIGN_KEY_CHECKS = 1;
