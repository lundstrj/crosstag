sudo killall python
cd /home/crosstag

sudo pip uninstall requests
sudo pip uninstall pyserial
sudo pip uninstall flask-security 
sudo pip uninstall flask-sqlalchemy
sudo pip uninstall Flask-WTF
rm crosstag.db
cd
sudo deluser crosstag
sudo rm -r /home/crosstag
