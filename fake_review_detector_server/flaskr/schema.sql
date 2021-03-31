### DDL
### Create Database sql:

```
CREATE DATABASE IF NOT EXISTS `smartacus` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
```

### Create Table SQL:

```
create table reviews (
    id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT, # ID
    review_id varchar(1024) DEFAULT NULL, # websites' review id
    review_content TEXT NOT NULL, # reviews' contents
    url varchar(512) DEFAULT NULL, # user visited url
    category VARCHAR(20) DEFAULT NULL, # 'Bar', 'Restaurant', 'Hotel'
    label BOOLEAN NOT NULL, # model returned label: truth(1) or spam(0)
    accuracy DECIMAL(5,2) DEFAULT NULL, # model returned accuracy
    createtime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, # timestamp of inserting/updating this entry
    CONSTRAINT review_chk_accuracy CHECK
    (accuracy > 0 and accuracy <= 100)
) ENGINE = InnoDB DEFAULT CHARSET=utf8;
```

### No index for this table so far.