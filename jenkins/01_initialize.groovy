sh '''
echo "development" | su -c "/etc/init.d/mariadb start" root
until mysqladmin ping --silent; do sleep 3; done
echo "ALTER USER 'root'@'localhost' IDENTIFIED BY '';" > setup.sql
echo "FLUSH PRIVILEGES;" >> setup.sql
echo "CREATE SCHEMA spillmanapi;" >> setup.sql
echo "development" | su -c "mysql -u root < setup.sql" root
python3.10 -m venv venv
. venv/bin/activate
'''