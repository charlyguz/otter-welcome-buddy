CREATE TABLE IF NOT EXISTS `interview_match` (
  `guild_id` VARCHAR(20) PRIMARY KEY,
  `author_id` VARCHAR(20) NOT NULL,
  `channel_id` VARCHAR(20) NOT NULL,
  `day_of_the_week` INTEGER NOT NULL,
  `emoji` VARCHAR(2),
  `message_id` VARCHAR(20)
);
