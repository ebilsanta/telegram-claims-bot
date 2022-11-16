# telegram-claims-bot
was @MotherClaimsBot on Telegram  
Use this to keep track of claims  

Not live anymore as Heroku no longer has a free tier

## To run locally
1. Create a new Telegram Bot by contacting @BotFather on Telegram. Take note of the **API Token**
2. Create a MySQL Database locally and note the **database name**
3. Clone this project locally
4. Rename the **.env.sample** file in the root folder to **.env** and fill up the following:  
 
DB_DATABASE= {_database name you created earlier_}  
DB_HOST=localhost  
DB_USERNAME=root  
DB_PASSWORD= {_'root' if mac-user, else ''_}  
BOT_TOKEN= {_your bot token from BotFather_}  
  
5. Open a terminal in the root folder and run 'python3 bot.py'  
6. Message /start to your bot on telegram!



