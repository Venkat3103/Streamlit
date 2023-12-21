
CREATE DATABASE IF NOT EXISTS GROCERY_SHOPPING;

USE DATABASE GROCERY_SHOPPING;

-- Schema to store user (consumer/shopper) details
CREATE SCHEMA IF NOT EXISTS USER;

USE SCHEMA USER;

CREATE TABLE IF NOT EXISTS user_data (
    user_id          INTEGER AUTOINCREMENT,
    username         VARCHAR(255) NOT NULL,
    email            VARCHAR(255) NOT NULL,
    phone_number     VARCHAR(15) NOT NULL,
    hashed_password  BINARY(60) NOT NULL,
    user_class       VARCHAR(10),
    registration_date TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    PRIMARY KEY (user_id, username)
);


-- Schema to store product information
CREATE SCHEMA IF NOT EXISTS PRODUCT;

USE SCHEMA PRODUCT;

CREATE TABLE IF NOT EXISTS product_catalogue (
    product_id INT,
    product_name VARCHAR(255),
    aisle_id INT,
    department_id INT,
    department VARCHAR(255),
    aisle VARCHAR(255),
    price FLOAT
);

-- Schema to store order details / map shopper and consumer
CREATE SCHEMA IF NOT EXISTS ORDER

USE SCHEMA ORDER

CREATE TABLE IF NOT EXISTS order_details(

);

-- Table to map order_id and shopper_id
CREATE TABLE IF NOT EXISTS order_mapper(

);



