CREATE TABLE scheduled_messages
(
    id        INT          NOT NULL PRIMARY KEY AUTO_INCREMENT,
    channel   BIGINT       NOT NULL,
    message   VARCHAR(500) NOT NULL,
    timestamp BIGINT       NOT NULL
)