sudo docker build -t http-server .
sudo docker run -p 81:8080 -v /home/fedor/Documents/Projects/Study/http-server/default.conf:/etc/httpd.conf:ro -v /home/fedor/Documents/Projects/Study/http-server/http-test-suite:/var/www/html:ro --rm --name http-server http-server
