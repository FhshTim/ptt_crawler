# ptt_crawler

This project is a ptt web crawler that can specify the post date range.
Store the required data in the database, skip the fetch if the captured URL is encountered to avoid wasting resources.


# 1. Docker Install


# windows:
https://docs.docker.com/docker-for-windows/install/

Download from Docker Hub -> Get Docker -> Double-click Docker for Windows Install to run the installer.

1.restart

2.Run docker version to check the version.

3.Run docker run hello-world to verify that Docker can pull and run images.


# Linux:
1.Log into your system as a user with sudo privileges.

2.Update your system: sudo yum update -y

3.Install Docker: sudo yum install docker-engine -y.

4.Start Docker: sudo service docker start.

5.Verify Docker: sudo docker run hello-world

# 2. Download this project
Git clone https://github.com/FhshTim/ptt_crawler.git

# 3. Run the PTT crawler project
1.open the folder where the project folder is.

2.open cmd

--> docker image build -t docker_pttcrawler .

--> docker run -ti docker_pttcrawler

_**ENJOY!!**_




