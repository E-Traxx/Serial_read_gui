CREATE TABLE IF NOT EXISTS exp_01 (
    id INT PRIMARY KEY AUTO_INCREMENT,
    names VARCHAR(20) NOT NULL UNIQUE,
    bio TEXT,
    kgs VARCHAR(3)
);


-- @block
insert ignore into APPS(time)
Values
(1)

-- @block
SELECT * FROM APPS;

