# New In Town CS50X Final Project

The project is a web application where you can seach for events places and aricles. The implementation is fairly simple,
to keep the project scope in check. I wanted to make a project like this to expand my knowledge of Flask, database,
role based authentications, etc.

---
## Program Language used: ##

- Python
- Flask
- Javascript
- sqlite
- css
- html5

---
## How the web application works?

The idea is simple, the user can register, during registration you need to enter these fields:

- Username
- Email
- Password
- Confirm Password
- Checkbox for agree registration

Once user is register can search for event in USA, and citys with aricles, allowing a user to save interested events. Also the user is able to change the password 

---
## Routing ##

Each route checks if the user is authenticated. It means if correct user_id were supplied. So for example a user can not access other users save events.

---
## Sessions ##

The webpage uses sessions to confirm that user is registered. Once the user logins, his credentials are checked with werkzeug.security library.

---
## Database ##

The web app uses Database which stores all users, places, save events, and deletes events. The tables, like user uses foreign keys to relate users to display all the events from that user key.

---
## API ##

The app used three API_KEY, the first one is from GOOGLE API to diplay the map, second one is from TICKET MASTER API to get the events, and the last one is from OPEN WEATHER API to display the current weather.

### In windows:

> c:/home> set GOOGLE_API_KEY=your_api_key

> c:/home> set TM_API_KEY=your_api_key

> c:/home> set WETHER_API_KEY=your_api_key

### In MacOs:

> ~/ $ export GOOGLE_API_KEY=your_api_key

> ~/ $ export TM_API_KEY=your_api_key

> ~/ $ export WETHER_API_KEY=your_api_key

---
## Possible improvements ##

### As all applications and all in life always is a space for improve. Possible improvements:

- Auto reminder by email 2 days before the event occur.
- Ability to purchase the events tickets from the app or redirect.
- Send message or email to friends about an event from the app.

---
## How to launch application ##
1. Check that you have Python 3 installed.
2. 

