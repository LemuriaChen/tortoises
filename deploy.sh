# this is for system update and deploy

# update software
echo 'updating software ...'

sudo apt-get update -y
sudo apt-get dist-upgrade -y
sudo apt-get dist-upgrade -y --fix-missing
sudo apt autoremove -y

echo 'done .'

# sudo apt install ubuntu-release-upgrader-core -y
cat /etc/lsb-release

# download google chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt install -f -y --fix-missing
sudo apt-get -f install -y

/usr/bin/google-chrome-stable --version

wget https://npm.taobao.org/mirrors/chromedriver/80.0.3987.106/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/bin/

chromedriver --version
