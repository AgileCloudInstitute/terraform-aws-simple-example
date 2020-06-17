## Copyright 2020 Green River IT (GreenRiverIT.com) as described in LICENSE.txt distributed with this project on GitHub.  
## Start at https://github.com/AgileCloudInstitute?tab=repositories    
  
####################################################  
# Below we create the USERDATA to get the instance ready to run.
# The Terraform local simplifies Base64 encoding.  
locals {

  example-host-userdata = <<USERDATA
#!/bin/bash -xe
### Install software
yum -y update

##Put any other startup commands you want to put here.
##Remember there are other approaches such as configuration tools like Ansible, Chef, Puppet, etc.

#SECURITY HOLE: Just for easy testing, the following enables password login and creates a testuser with a password in version control. 
#Remove the following lines when you establish a secrets management system.
/usr/sbin/useradd testuser
echo testuser:just-for-test123 | chpasswd
sed -i 's/PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config
#Configure user to not require password to execute sudo commands.  
cat << 'EOF' > /etc/sudoers.d/testuser
testuser ALL=(ALL) NOPASSWD: ALL
EOF  
systemctl restart sshd  

USERDATA

}
