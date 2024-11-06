## Setup + Login Commands

Copy the password from there then run the following to SSH into the server:
`ssh [pennkey]@ssh.wwbp.org`

In the other step, you will be asked for a password. To see the password first run the following command:
`cat ~/.my.cnf`

Then run:
`mysql -u [pennkey] -p`

To use the Reddit database (swap reddit with dobbs_senior_design_db to see our database):
`USE reddit;`

(Optional) To see all tables use:
`SHOW TABLES;`

## Database

Database contains the following tables:
- Bot_users
- Subreddits 
- Users_2006_01 - Users_2017_12
- Sub_2005_05 - Sub_2024_08 (I also assume this is being constantly updated)
- Com_2006_01 - Com_2024_08 (I also assume this is being constantly updated)
