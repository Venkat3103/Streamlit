CREATE DATABASE IF NOT EXISTS GROCERY_SHOPPING;

USE DATABASE GROCERY_SHOPPING;

CREATE SCHEMA IF NOT EXISTS USER;

USE SCHEMA USER;
DROP TABLE user_data;

CREATE TABLE user_data (
    user_id INTEGER AUTOINCREMENT PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone_number VARCHAR(10) NOT NULL,
    hashed_password BINARY(60) NOT NULL,
    user_class VARCHAR(10),
    registration_date TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);


SELECT * FROM USER_DATA;

CREATE SCHEMA IF NOT EXISTS PRODUCT;

USE SCHEMA PRODUCT;
DROP TABLE product_catalogue;


CREATE TABLE product_catalogue (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(255),
    aisle_id INT,
    department_id INT,
    department VARCHAR(255),
    aisle VARCHAR(255),
    price FLOAT
);

UPDATE product_catalogue
SET Price = ROUND(Price, 2);

CREATE SCHEMA IF NOT EXISTS ORDERS;
USE SCHEMA ORDERS;


CREATE TABLE order_details (
    order_id INT PRIMARY KEY,
    total_amount FLOAT,
    consumer_id INT,
    shopper_id INT,
    order_date DATE,
    order_time TIME,
    delivery_date DATE,
    delivery_time TIME,
    delivery_address VARCHAR,
    FOREIGN KEY (consumer_id) REFERENCES user.user_data(user_id),
    FOREIGN KEY (shopper_id) REFERENCES user.user_data(user_id)
);


CREATE TABLE order_items (
    order_id INT,
    product_id INT,
    quantity INT,
    unit_price FLOAT,
    FOREIGN KEY(order_id) REFERENCES orders.order_details(order_id),
    FOREIGN KEY(product_id) REFERENCES product.product_catalogue(product_id)
);


