#!/bin/bash

set -e

# Check for merge conflicts before proceeding
python -m compileall -f "${GITHUB_WORKSPACE}"
if grep -lr --exclude-dir=node_modules "^<<<<<<< " "${GITHUB_WORKSPACE}"
    then echo "Found merge conflicts"
    exit 1
fi

cd ~ || exit

sudo apt update && sudo apt install redis-server libcups2-dev

pip install capkpi-bench

git clone https://github.com/capkpi/capkpi --branch "${GITHUB_BASE_REF:-${GITHUB_REF##*/}}" --depth 1
bench init --skip-assets --capkpi-path ~/capkpi --python "$(which python)" capkpi-bench

mkdir ~/capkpi-bench/sites/test_site
cp -r "${GITHUB_WORKSPACE}/.github/helper/site_config.json" ~/capkpi-bench/sites/test_site/

mysql --host 127.0.0.1 --port 3306 -u root -e "SET GLOBAL character_set_server = 'utf8mb4'"
mysql --host 127.0.0.1 --port 3306 -u root -e "SET GLOBAL collation_server = 'utf8mb4_unicode_ci'"

mysql --host 127.0.0.1 --port 3306 -u root -e "CREATE USER 'test_capkpi'@'localhost' IDENTIFIED BY 'test_capkpi'"
mysql --host 127.0.0.1 --port 3306 -u root -e "CREATE DATABASE test_capkpi"
mysql --host 127.0.0.1 --port 3306 -u root -e "GRANT ALL PRIVILEGES ON \`test_capkpi\`.* TO 'test_capkpi'@'localhost'"

mysql --host 127.0.0.1 --port 3306 -u root -e "UPDATE mysql.user SET Password=PASSWORD('travis') WHERE User='root'"
mysql --host 127.0.0.1 --port 3306 -u root -e "FLUSH PRIVILEGES"

wget -O /tmp/wkhtmltox.tar.xz https://github.com/capkpi/wkhtmltopdf/raw/master/wkhtmltox-0.12.3_linux-generic-amd64.tar.xz
tar -xf /tmp/wkhtmltox.tar.xz -C /tmp
sudo mv /tmp/wkhtmltox/bin/wkhtmltopdf /usr/local/bin/wkhtmltopdf
sudo chmod o+x /usr/local/bin/wkhtmltopdf

cd ~/capkpi-bench || exit

sed -i 's/watch:/# watch:/g' Procfile
sed -i 's/schedule:/# schedule:/g' Procfile
sed -i 's/socketio:/# socketio:/g' Procfile
sed -i 's/redis_socketio:/# redis_socketio:/g' Procfile

bench get-app erp "${GITHUB_WORKSPACE}"
bench start &> bench_run_logs.txt &
bench --site test_site reinstall --yes
