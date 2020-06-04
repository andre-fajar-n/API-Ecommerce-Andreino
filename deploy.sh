eval "$(ssh-agent -s)" &&
ssh-add -k ~/.ssh/id_rsa &&

source ~/.profile
echo "DOCKER_PASSWORD" | docker login --username $DOCKER_USERNAME --password-stdin
docker stop ecommerce
docker rm ecommerce
docker rmi andresangfajar/be_ecommerce:latest
docker run -d --name ecommerce -p 5050:5050 andresangfajar/be_ecommerce:latest
