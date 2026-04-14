# HappyRobot_Test

Installation steps on EC2 : 
```
sudo yum install docker
sudo service docker start
sudo usermod -aG docker ec2-user
newgrp docker
docker build -t streamlit .
docker images
docker run -d -p 8501:8501 streamlit
```

# additional : 
open port in security group
