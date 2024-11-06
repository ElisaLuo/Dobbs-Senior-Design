-- Creating a table
INSERT INTO sub_2022 (subreddit)
SELECT subreddit
FROM reddit.sub_2022_12
WHERE message REGEXP '[iI] \\([0-9]{2}[fF]\\) '
  AND subreddit NOT IN (SELECT subreddit FROM sub_2022)
GROUP BY subreddit
HAVING COUNT(*) = 1;

-- Extract user age and gender using regex
INSERT INTO dobbs_senior_design_db.users (user_id, age, gender)
SELECT 
    user_id, 
    SUBSTRING(REGEXP_SUBSTR(message, '[iI]\\s*\\(([0-9]{2})[fFmM]\\)'), 4, 2) AS age,
    UPPER(SUBSTRING(REGEXP_SUBSTR(message, '[iI]\\s*\\(([0-9]{2})[fFmM]\\)'), 6, 1)) AS gender
FROM 
    reddit.sub_2022_12
WHERE 
    message REGEXP '[iI] \\([0-9]{2}[fFmM]\\) ' 
GROUP BY 
    user_id, message
HAVING 
    COUNT(*) = 1
ON DUPLICATE KEY UPDATE 
    age = VALUES(age), 
    gender = VALUES(gender);
