import subprocess
import sys
import json
import time
import os
import platform
import yaml
#import pathlib
#import time
#import subprocess
#import sys
#import json

inputArgs=sys.argv

#.start new
def getCurrentRegion(cmd):
  print("r ----------------------------------------------------")
  logString = "About to run cli command: "+cmd
  print(logString)
  process = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, text=True)
  data = process.stdout
  err = process.stderr
  logString = "data string is: " + data
  print(logString)
  logString = "err is: " + str(err)
  print(logString)
  logString = "process.returncode is: " + str(process.returncode)
  print(logString)
  if process.returncode == 0:
    logString = str(data)
    print(logString)
    print("-------")
    return data
  else:
    logString = "process.returncode is not zero.  Halting program so you can diagnose the root cause of the problem.  "
    print(logString)
    sys.exit

def getAccount(cmd='aws sts get-caller-identity'):
#  print("a ----------------------------------------------------")
  logString = "About to run get account id command: "+cmd
  print(logString)
  process = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, text=True)
  data = process.stdout
  err = process.stderr
  if process.returncode == 0:
    mydata = json.loads(data)
    #print("type(mydata) is: ", type(mydata))
    if "Account" in mydata:
      myAccountId = mydata["Account"]
      print("Account Id is: ", myAccountId)
      #print("len(myAccountId) is: ", len(myAccountId))
      #print("str(myAccountId).isdigit() is: ", str(myAccountId).isdigit())
      if ((len(myAccountId)!=12) or (not str(myAccountId).isdigit())):
        logString = "An unexpected value ( "+str(myAccountId)+" ) was returned for the aws account id. Halting program so you can identify the root cause.  "
        print(logString)
        sys.exit(1)
      return myAccountId
    else:
      logString = "The 'Account' key is not included in the response.  Halting program so you can identify the root cause of the problem. "
      print(logString)
      sys.exit(1)
  else:
    logString = str(data)
    print(logString)
    logString = "err is: " + str(err)
    print(logString)
    logString = "process.returncode is: " + str(process.returncode)
    print(logString)
    logString = "The '"+cmd+"' command returned a non-zero return code.  Halting program so that you can identify the root cause of the problem. "
    print(logString)
    sys.exit(1)

def getFileSystems(cmd,account,when,counter=0):
  when = "after"
  print("y when is: ", when)
  logString = "About to get file system ids by running cli command: "+cmd
  print(logString)
  process = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, text=True)
  data = process.stdout
  err = process.stderr
  if process.returncode == 0:
    mydata = json.loads(data)
    fileSystemIds = []
    for thisfs in mydata["FileSystems"]:
      fsarn=thisfs["FileSystemArn"]
      fsowner=thisfs["OwnerId"]
      print("y fsarn is: ", fsarn)
      print("y fsowner is: ", fsowner)
      print("y account is: ", account)
      if (account in fsarn) and (fsowner==account):
#        if "Tags" in thisfs:
#          for fstag in thisfs["Tags"]:
#            fstagkey=fstag["Key"]
#            if fstagkey == "ManagedByAmazonSageMakerResource":
              fsid=thisfs["FileSystemId"]
              print("y fsid is: ", fsid)
              fileSystemIds.append(fsid)
              if when == "before":
                return fileSystemIds
              elif when == "after":
                print("y len(fileSystemIds) is: ", len(fileSystemIds))
                if len(fileSystemIds) == 0:
                  return fileSystemIds
                else:
                  if counter < 5:
                    counter += 1
                    print("Sleeping 60 seconds to allow the deletions of file systems to propagate before checking their status again.")
                    time.sleep(60)
                    print("Attempt number: ", str(counter))
                    print("2x")
#                    getFileSystems(cmd,when,counter)
                    getFileSystems(cmd,account,when,counter)
                  else:
                    logString = "ERROR: File system still present after "+str(counter)+" retries. Stopping program so you can research the root cause of this problem. "
                    print(logString)
                    sys.exit(1)
              else:
                logString = "ERROR: Illegal value for 'when' variable in getFileSystem(): "+when+ ". Stopping program so you can research the root cause of this problem. "
                print(logString)
                sys.exit(1)
  else:
    logString = "process.returncode is: " + str(process.returncode)
    print(logString)
    logString = "err is: " + str(err)
    print(logString)
    logString = str(data)
    print(logString)
    logString = "The '"+cmd+"' command returned a non-zero return code.  Halting program so that you can identify the root cause of the problem. "
    print(logString)
    sys.exit(1)

#def deleteFileSystem(fsid):
#  deleteFileSystemCmd="aws efs delete-file-system --file-system-id "+fsid
#  logString = "About to delete file system by running cli command: "+deleteFileSystemCmd
#  print(logString)
#  process = subprocess.run(deleteFileSystemCmd, shell=True, stdout=subprocess.PIPE, text=True)
#  data = process.stdout
#  err = process.stderr
#  if process.returncode == 0:
#    print("fs2 return code 0")
#  else:
#    logString = "process.returncode is: " + str(process.returncode)
#    print(logString)
#    logString = "err is: " + str(err)
#    print(logString)
#    logString = str(data)
#    print(logString)
#    logString = "The '"+deleteFileSystemCmd+"' command returned a non-zero return code.  Halting program so that you can identify the root cause of the problem. "
#    print(logString)
#    sys.exit(1)


def getMountTargets(fsid, when, counter=0):
  getMountTargetsCmd="aws efs describe-mount-targets --file-system-id "+fsid
  logString = "About to get mount target ids by running cli command: "+getMountTargetsCmd
  print(logString)
  process = subprocess.run(getMountTargetsCmd, shell=True, stdout=subprocess.PIPE, text=True)
  data = process.stdout
  err = process.stderr
  if process.returncode == 0:
    mydata = json.loads(data)
    mountTargetIds = []
    for thismt in mydata["MountTargets"]:
      mtid=thismt["MountTargetId"]
      mountTargetIds.append(mtid)
    if when == "before":
      return mountTargetIds
    elif when == "after":
      if len(mountTargetIds) == 0:
        return mountTargetIds
      else:
        if counter < 5:
          counter += 1
          print("Sleeping 60 seconds to allow the deletions of mount ids to propagate before checking their status again.")
          time.sleep(60)
          print("Attempt number: ", str(counter))
          getMountTargets(fsid,when,counter)
        else:
          logString = "ERROR: Mount Ids still present after "+str(counter)+" retries. Stopping program so you can research the root cause of this problem. "
          print(logString)
          sys.exit(1)
    else:
      logString = "ERROR: Illegal value for 'when' variable in getMountTargets(): "+when+ ". Stopping program so you can research the root cause of this problem. "
      print(logString)
      sys.exit(1)
  else:
    logString = "process.returncode is: " + str(process.returncode)
    print(logString)
    logString = "err is: " + str(err)
    print(logString)
    logString = str(data)
    print(logString)
    logString = "The '"+getMountTargetsCmd+"' command returned a non-zero return code.  Halting program so that you can identify the root cause of the problem. "
    print(logString)
    sys.exit(1)

#def deleteMountTargets(mtid):
#  deleteMountTargetsCmd="aws efs delete-mount-target --mount-target-id "+mtid
#  logString = "About to delete mount target by running cli command: "+deleteMountTargetsCmd
#  print(logString)
#  process = subprocess.run(deleteMountTargetsCmd, shell=True, stdout=subprocess.PIPE, text=True)
#  data = process.stdout
#  err = process.stderr
#  if process.returncode == 0:
#    print("mt2 return code 0")
#  else:
#    logString = "process.returncode is: " + str(process.returncode)
#    print(logString)
#    logString = "err is: " + str(err)
#    print(logString)
#    logString = str(data)
#    print(logString)
#    logString = "The '"+deleteMountTargetsCmd+"' command returned a non-zero return code.  Halting program so that you can identify the root cause of the problem. "
#    print(logString)
#    sys.exit(1)

#def checkSecurityGroupRule(sgid, counter=0):
#  cmd = 'aws ec2 describe-security-group-rules --filters Name="group-id",Values="'+sgid+'"'
#  logString = "About to check for presense of security group rules in specified security group by running cli command: "+cmd
#  print(logString)
#  process = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, text=True)
#  data = process.stdout
#  err = process.stderr
#  if process.returncode == 0:
#    print("check for rules cmd return code 0")
#    logString = "rules returned for security group are: "+str(data)
#    print(logString)
#    mydata = json.loads(data)
#    numRules = len(mydata["SecurityGroupRules"])
#    logString = "Number of rules remaining in security group is: "+str(numRules)
#    print(logString)
#    numChecks = 15
#    if numRules > 0:
#      if counter < numChecks:
#        logString = "WARNING: Going to sleep 60 seconds and then check again to see if the security group rules have been deleted from security group with id: "+str(sgid)+". Attempt number "+str(counter)+" of "+str(numChecks)+". "
#        counter +=1
#        time.sleep(60)
#        checkSecurityGroupRule(sgid, counter)
#      else:
#        logString = "ERROR: Security group rules did not delete from security group with id "+str(sgid)+" despite repeading check "+str(numChecks)+" times.  Halting program so you can examine the root cause of the problem. "
#        print(logString)
#        sys.exit(1)
#  else:
#    logString = "process.returncode is: " + str(process.returncode)
#    print(logString)
#    logString = "err is: " + str(err)
#    print(logString)
#    logString = str(data)
#    print(logString)
#    tot = 5
#    if counter < tot:
#      logString = "The '"+cmd+"' command returned a non-zero return code.  Going to sleep 30 seconds and try again.  Attempt "+str(counter)+" out of "+str(tot)+"."
#      print(logString)
#      time.sleep(30)
#      counter += 1
#      checkSecurityGroupRule(cmd, counter)
#    else:
#      logString = "The '"+cmd+"' command returned a non-zero return code.  Halting program so that you can identify the root cause of the problem. "
#      print(logString)
#      sys.exit(1)

#def revokeSecurityGroupRule(revokeCmd, sgid, counter=0):
#  logString = "About to revoke security group rule by running cli command: "+revokeCmd
#  print(logString)
#  process = subprocess.run(revokeCmd, shell=True, stdout=subprocess.PIPE, text=True)
#  data = process.stdout
#  err = process.stderr
#  if process.returncode == 0:
#    print("revoke cmd return code 0")
#    return
#  else:
#    logString = "process.returncode is: " + str(process.returncode)
#    print(logString)
#    logString = "err is: " + str(err)
#    print(logString)
#    logString = str(data)
#    print(logString)
#    tot = 5
#    if counter < tot:
#      logString = "The '"+revokeCmd+"' command returned a non-zero return code.  Going to sleep 30 seconds and try again.  Attempt "+str(counter)+" out of "+str(tot)+"."
#      print(logString)
#      time.sleep(30)
#      counter += 1
#      revokeSecurityGroupRule(revokeCmd, sgid, counter)
#    else:
#      logString = "The '"+revokeCmd+"' command returned a non-zero return code.  Halting program so that you can identify the root cause of the problem. "
#      print(logString)
#      sys.exit(1)

#def getSecurityGroups(vpcid, when, counter=0):
#  getSecurityGroupsCmd="aws ec2 describe-security-groups"
#  logString = "About to get security groups by running cli command: "+getSecurityGroupsCmd
#  print(logString)
#  process = subprocess.run(getSecurityGroupsCmd, shell=True, stdout=subprocess.PIPE, text=True)
#  data = process.stdout
#  err = process.stderr
#  if process.returncode == 0:
#    mydata = json.loads(data)
#    securityGroupIds = []
#    for thissg in mydata["SecurityGroups"]:
##      if (thissg["VpcId"] == vpcid) and ("Cloud9" not in thissg["Description"]) and ("default VPC" not in thissg["Description"]) and ("Allow TLS for VPC" not in thissg["Description"]):
#      if (thissg["VpcId"] == vpcid) and (("[DO NOT DELETE]" in thissg["Description"]) or ("for Elastic MapReduce created on" in thissg["Description"])):
#        sgid=thissg["GroupId"]
#        securityGroupIds.append(sgid)
#    if when == "before":
#      return securityGroupIds
#    elif when == "after":
#      if len(securityGroupIds) == 0:
#        return securityGroupIds
#      else:
#        if counter < 5:
#          counter += 1
#          print("Sleeping 60 seconds to allow the deletions of security groups to propagate before checking their status again.")
#          time.sleep(60)
#          print("Attempt number: ", str(counter))
#          getSecurityGroups(vpcid,when,counter)
#        else:
#          logString = "ERROR: Security Groups still present after "+str(counter)+" retries. Stopping program so you can research the root cause of this problem. "
#          print(logString)
#          sys.exit(1)
#    else:
#      logString = "ERROR: Illegal value for 'when' variable in getSecurityGroups(): "+when+ ". Stopping program so you can research the root cause of this problem. "
#      print(logString)
#      sys.exit(1)
#  else:
#    logString = "process.returncode is: " + str(process.returncode)
#    print(logString)
#    logString = "err is: " + str(err)
#    print(logString)
#    logString = str(data)
#    print(logString)
#    logString = "The '"+getSecurityGroupsCmd+"' command returned a non-zero return code.  Halting program so that you can identify the root cause of the problem. "
#    print(logString)
#    sys.exit(1)

#def deleteSecurityGroups(sgid, vpcid, counter=0):
#  deleteSecurityGroupCmd="aws ec2 delete-security-group --group-id "+sgid
#  logString = "About to delete security group by running cli command: "+deleteSecurityGroupCmd
#  print(logString)
#  process = subprocess.run(deleteSecurityGroupCmd, shell=True, stdout=subprocess.PIPE, text=True)
#  data = process.stdout
#  err = process.stderr
#  if process.returncode == 0:
#    print("sgdelete return code 0")
#  else:
#    max = 20
#    if counter < max:
#      counter+=1
#      logString = "INFO: The '"+deleteSecurityGroupCmd+"' command returned a non-zero return code.  Sleeping 60 seconds before retrying in case this is caused by a latency problem delaying the deletion of dependent objects. Attempt "+str(counter)+" out of "+str(max)+"."
#      print(logString)
#      print("Inside deleteSecurityGroups(), vpcid is: ", vpcid)
#      print("Going to try to delete security group rules in the security group one more time before sleeping and then trying to delete the security group again. ")
#      emptyOneSecurityGroup(sgid)
#      time.sleep(60)
#      deleteSecurityGroups(sgid, counter)
#    logString = "process.returncode is: " + str(process.returncode)
#    print(logString)
#    logString = "err is: " + str(err)
#    print(logString)
#    logString = str(data)
#    print(logString)
#    logString = "ERROR: The '"+deleteSecurityGroupCmd+"' command returned a non-zero return code.  Halting program so that you can identify the root cause of the problem. "
#    print(logString)
#    sys.exit(1)


#def getSecurityGroupRules(sgid, when, counter=0):
#  getSecurityGroupRulesCmd="aws ec2 describe-security-group-rules"
#  logString = "About to get security group rules by running cli command: "+getSecurityGroupRulesCmd
#  print(logString)
#  process = subprocess.run(getSecurityGroupRulesCmd, shell=True, stdout=subprocess.PIPE, text=True)
#  data = process.stdout
#  err = process.stderr
#  if process.returncode == 0:
#    mydata = json.loads(data)
#    securityGroupRuleRevokeCmds = []
#    securityGroupRuleIds = []
#    for thissgr in mydata["SecurityGroupRules"]:
#      if (thissgr["GroupId"] == sgid):
#        sgrid=thissgr["SecurityGroupRuleId"]
#        if when == "before":
#          if thissgr["IsEgress"] == True:
#            revokeCmd="aws ec2 revoke-security-group-egress --group-id "+sgid+" --security-group-rule-ids "+sgrid
#          elif thissgr["IsEgress"] == False:
#            revokeCmd="aws ec2 revoke-security-group-ingress --group-id "+sgid+" --security-group-rule-ids "+sgrid
#          else:
#            print("ERROR: Illegal value for IsEgress")
#            sys.exit(1)
#          securityGroupRuleRevokeCmds.append(revokeCmd)
#        elif when == "after":
#          securityGroupRuleIds.append(sgrid)
#    if when == "before":
#      print("INFO: Before returning getSecurityGroupRules(), securityGroupRuleRevokeCmds is: ", securityGroupRuleRevokeCmds)
#      print("INFO: Before returning getSecurityGroupRules(), len(securityGroupRuleRevokeCmds) is: ", str(len(securityGroupRuleRevokeCmds)))
#      return securityGroupRuleRevokeCmds
#    elif when == "after":
#      if len(securityGroupRuleIds) == 0:
#        print("INFO: Before returning getSecurityGroupRules(), sgid is: ", sgid)
#        print("INFO: Before returning getSecurityGroupRules(), securityGroupRuleIds is: ", securityGroupRuleIds)
#        print("INFO: Before returning getSecurityGroupRules(), len(securityGroupRuleIds) is: ", str(len(securityGroupRuleIds)))
#        return securityGroupRuleIds
#      else:
#        logString = "For sgid "+str(sgid)+". len(securityGroupRuleIds) is: "+str(len(securityGroupRuleIds))
#        print(logString)
#        if counter < 5:
#          counter += 1
#          print("Sleeping 60 seconds to allow the deletions of security group rules to propagate before checking their status again.")
#          time.sleep(60)
#          print("Attempt number: ", str(counter))
#          getSecurityGroupRules(sgid,when,counter)
#        else:
#          logString = "ERROR: Security Group rules still present after "+str(counter)+" retries. Stopping program so you can research the root cause of this problem. "
#          print(logString)
#          sys.exit(1)
#    else:
#      logString = "ERROR: Illegal value for 'when' variable in getSecurityGroupRules(): "+when+ ". Stopping program so you can research the root cause of this problem. "
#      print(logString)
#      sys.exit(1)
#  else:
#    logString = "process.returncode is: " + str(process.returncode)
#    print(logString)
#    logString = "err is: " + str(err)
#    print(logString)
#    logString = str(data)
#    print(logString)
#    logString = "The '"+getSecurityGroupRulesCmd+"' command returned a non-zero return code.  Halting program so that you can identify the root cause of the problem. "
#    print(logString)
#    sys.exit(1)


def getVPC(vname, counter=0):
  getVPCCmd='aws ec2 describe-vpcs --filters "Name=tag-value,Values='+vname+'"'
  logString = "About to get VPC by running cli command: "+getVPCCmd
  print(logString)
  process = subprocess.run(getVPCCmd, shell=True, stdout=subprocess.PIPE, text=True)
  data = process.stdout
  err = process.stderr
  if process.returncode == 0:
    mydata = json.loads(data)
    vpcIds = []
    for thisvpc in mydata["Vpcs"]:
      if (thisvpc["State"] == "available"):
        vid=thisvpc["VpcId"]
        print('INFO: Inside getVPC(), thisvpc["VpcId"] is: ', thisvpc["VpcId"])
        vpcIds.append(vid)
    if len(vpcIds) >1:
      logString = "ERROR: More than one VPC contains the tag with value "+vname+". The value is intended to be unique in your account to avoid deleting unintended resources outside the intended vpc.  Halting program so you can identify the root cause of the problem. "
      print(logString)
      sys.exit(1)
    elif len(vpcIds) == 1:
      print("INFO: Before returning getVPC(), vpcIds is: ", vpcIds)
      print("INFO: Before returning getVPC(), vpcIds[0] is: ", vpcIds[0])
      return vpcIds[0]
    else:
      if counter < 5:
        counter += 1
        print("INFO: A vpc with tag value "+vname+" was not found.  Sleeping 60 seconds before checking again in case a latency problem is causing a delay in the appearance of a matching VPC.")
        time.sleep(60)
        print("Attempt number: ", str(counter))
        getVPC(vname,counter)
      else:
        logString = "ERROR: VPC containing tag with value "+vname+" was not found after "+str(counter)+" attempts, with 60 second wait between each attempt.  Program will continue to run assuming you have already deleted the VPC separately.  Check your logs to make sure the VPC has been deleted.  "
        print(logString)
        return -1
  else:
    logString = "process.returncode is: " + str(process.returncode)
    print(logString)
    logString = "err is: " + str(err)
    print(logString)
    logString = str(data)
    print(logString)
    logString = "The '"+getVPCCmd+"' command returned a non-zero return code.  Halting program so that you can identify the root cause of the problem. "
    print(logString)
    sys.exit(1)


#.end new

def find(d, tag):
  if tag in d:
    yield d[tag]

#def runRegistrationCommand(cmd):
#  print("r ----------------------------------------------------")
#  logString = "About to run registration cli command: "+cmd
#  print(logString)
#  process = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, text=True)
#  data = process.stdout
#  err = process.stderr
#  logString = "data string is: " + data
#  print(logString)
#  logString = "err is: " + str(err)
#  print(logString)
#  logString = "process.returncode is: " + str(process.returncode)
#  print(logString)
#  if process.returncode == 0:
#    logString = str(data)
#    print(logString)
#    print("-------")
#    return data
#  if ('deregister-resource') in cmd and (process.returncode==254):
#    logString = "WARNING: Examine the error message above to understand the cause of the 254 return code.  Program will continue on the assumption that the resource has already been deregistered properly.  "
#    print(logString)
#  else:
#    logString = "WARNING: Examine the error message above to understand the cause of the 254 return code.  Program will continue on the assumption that the resource has already been registered properly.  "
#    print(logString)

#def runEmptyS3BucketCommand(cmd):
#  print("r ----------------------------------------------------")
#  logString = "About to run cli command to empty s3 bucket: "+cmd
#  print(logString)
#  process = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, text=True)
#  data = process.stdout
#  err = process.stderr
#  logString = "data string is: " + data
#  print(logString)
#  logString = "err is: " + str(err)
#  print(logString)
#  logString = "process.returncode is: " + str(process.returncode)
#  print(logString)
#  if process.returncode == 0:
#    logString = str(data)
#    print(logString)
#    print("-------")
#    return data
#  else:
#    logString = "process.returncode is not zero.  Halting program so you can diagnose the root cause of the problem.  "
#    print(logString)
#    sys.exit


#def isS3Registered(cmd):
#  print("r ----------------------------------------------------")
#  logString = "About to check if s3 is registered by running command: "+cmd
#  print(logString)
#  process = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, text=True)
#  data = process.stdout
#  err = process.stderr
#  logString = "data string is: " + data
#  print(logString)
#  logString = "err is: " + str(err)
#  print(logString)
#  logString = "process.returncode is: " + str(process.returncode)
#  print(logString)
#  if process.returncode == 0:
#    logString = str(data)
#    print(logString)
#    print("-------")
#    return True
#  else:
#    ## NOTE: Error message returned by CLI should read "An error occurred (EntityNotFoundException) when calling the DescribeResource operation: Entity not found"
#    logString = "process.returncode is not zero.  Therefore we are assuming that the s3 is not registered.  "
#    print(logString)
#    return False

def createConfigAndCredentialsAWS():
#start
  # The following assumes that you only have one set of AWS credentials in keys.yaml, and that they have the key names given below.  
  if platform.system() == "Windows":
    osChar = '\\'
  else:
    osChar = '/'
  keyFile = os.path.expanduser('~')+osChar+'acm'+osChar+'keys'+osChar+'starter'+osChar+'keys.yaml'
  print("keyFile is: ", keyFile)
  if os.path.isfile(keyFile):
    print(keyFile, " is a file. ") 
  stream = open(keyFile, 'r')
  data = yaml.load(stream, yaml.SafeLoader)
  access_key=''
  secret_key=''
  for val in find(data, 'AWSAccessKeyId'):
    access_key = "aws_access_key_id = "+val+"\n"
  for val in find(data, 'AWSSecretKey'):
    secret_key = "aws_secret_access_key = "+val+"\n"
  if access_key != '':
#COMMENTING THIS LINE FOR SECURITY REASONS    print(access_key)
    pass
  else:
    quit("ERROR: AWSAccessKeyId was not found in keys.yaml.")
  if secret_key != '':
#COMMENTING THIS LINE FOR SECURITY REASONS    print(secret_key)
    pass
  else:
    quit("ERROR: AWSSecretKey was not found in keys.yaml.")
  credFile = os.path.expanduser('~')+osChar+'.aws'+osChar+'credentials'
  print("credFile is: ", credFile)
  if not os.path.isfile(credFile):
    print(credFile, " is NOT a file. ") 
    with open(credFile, 'w') as out_file:
      out_file.write("[default]\n")
      out_file.write(access_key)
      out_file.write(secret_key)
  acmConfigFile = os.path.expanduser('~')+osChar+'acm'+osChar+'keys'+osChar+'starter'+osChar+'config.yaml'
  print("acmConfigFile is: ", acmConfigFile)
  if os.path.isfile(acmConfigFile):
    print(acmConfigFile, " is a file. ") 
  stream = open(acmConfigFile, 'r')
  data = yaml.load(stream, yaml.SafeLoader)
  awsregion=''
  for val in find(data, 'region'):
    awsregion = "region = "+val+"\n"
  configFile = os.path.expanduser('~')+osChar+'.aws'+osChar+'config'
  print("configFile is: ", configFile)
  if not os.path.isfile(configFile):
    print(configFile, " is NOT a file. ") 
    with open(configFile, 'w') as out_file2:
      out_file2.write("[default]\n")
      out_file2.write(awsregion)
#end

def deleteConfigAndCredentialsAWS():
  if platform.system() == "Windows":
    osChar = '\\'
  else:
    osChar = '/'
  #Delete files
  credFile = os.path.expanduser('~')+osChar+'.aws'+osChar+'credentials'
  print("aws credFile is: ", credFile)
  try:
    os.remove(credFile)
  except OSError:
    pass
  configFile = os.path.expanduser('~')+osChar+'.aws'+osChar+'config'
  print("aws configFile is: ", configFile)
  try:
    os.remove(configFile)
  except OSError:
    pass


def getAccount(cmd='aws sts get-caller-identity'):
#  print("a ----------------------------------------------------")
  logString = "About to run get account id command: "+cmd
  print(logString)
  #  quit()

  process = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, text=True)
  data = process.stdout
  err = process.stderr
  if process.returncode == 0:
    mydata = json.loads(data)
    #print("type(mydata) is: ", type(mydata))
    if "Account" in mydata:
      myAccountId = mydata["Account"]
      print("Account Id is: ", myAccountId)
      #print("len(myAccountId) is: ", len(myAccountId))
      #print("str(myAccountId).isdigit() is: ", str(myAccountId).isdigit())
      if ((len(myAccountId)!=12) or (not str(myAccountId).isdigit())):
        logString = "An unexpected value ( "+str(myAccountId)+" ) was returned for the aws account id. Halting program so you can identify the root cause.  "
        print(logString)
        sys.exit(1)
      return myAccountId
    else:
      logString = "The 'Account' key is not included in the response.  Halting program so you can identify the root cause of the problem. "
      print(logString)
      sys.exit(1)
  else:
    logString = str(data)
    print(logString)
    logString = "err is: " + str(err)
    print(logString)
    logString = "process.returncode is: " + str(process.returncode)
    print(logString)
    logString = "The '"+cmd+"' command returned a non-zero return code.  Halting program so that you can identify the root cause of the problem. "
    print(logString)
    sys.exit(1)

#def getErrorString():
#  logString = "ERROR: Illegal syntax.  Command must look like either of the following options:"
#  print(logString)
#  print()
#  logString = 'registerS3AndRole.py reg role=roleName bucket=bucketName'
#  print(logString)
#  logString = 'registerS3AndRole.py dereg bucket=bucketName bucket2=bucket2Name'
#  print(logString)
#  print()
#  logString = 'Also, for either version of the command, you can alternatively have the script append your AWS account id if you use bucket=bucketName$awsAccountId and bucket2=bucket2Name$awsAccountId .'
#  print(logString)
#  print()
#  logString = 'If you are running this from the Agile Cloud Manager, you must use the syntax given for preprocessors and postprocessors given in the documentation at AgileCloudInstitute.io .  The Agile Cloud Manager will translate the correct preprocessor/postprocessor syntax into the correct syntax for this command. '
#  print(logString)
#  print()
#  sys.exit(1)

##The following function will set all the values for the returned properties
#def processInputArgs(inputArgs):
#    print("str(inputArgs) is: ", inputArgs)
#    n=-1
#    n2=-2
#    role = ""
#    bucket2 = ""
#    if (inputArgs[1]=='reg'):
#      regCmd = (inputArgs[1])
#      n=3
##      n2=4
#      print("regCmd 1 is: ", regCmd)
#    elif ((inputArgs[1]=='dereg')):
#      regCmd = (inputArgs[1])
#      n=2
#      n2=3
#      print("regCmd 2 is: ", regCmd)
#    else:
#      getErrorString()
#    if (inputArgs[2].startswith('role=')) and (inputArgs[1]=='reg'):
#      role = (inputArgs[2])[5:]
#      print("role is: ", role)
#    else:
#      if (inputArgs[2].startswith('role=')) and (not inputArgs[1]=='reg'):
##        print("x")
#        getErrorString()
#    if (inputArgs[n].startswith('bucket=')):
#      bucket = (inputArgs[n])[7:]
#      if "$awsAccountId" in bucket:
#        accountNumber = getAccount()
#        bucket = bucket.replace("$awsAccountId",accountNumber)
#      print("bucket is: ", bucket)
#    else:
#      getErrorString()
#    print("len(inputArgs)", len(inputArgs))
#    if (len(inputArgs) == 4): #Avoid error related to index not found
#      print("inputArgs is: ", inputArgs)
#      print("n2 is: ", n2)
#      if (inputArgs[n2].startswith('bucket2=')):
#        bucket2 = (inputArgs[n2])[8:]
#        if "$awsAccountId" in bucket2:
#          accountNumber = getAccount()
#          bucket2 = bucket2.replace("$awsAccountId",accountNumber)
#        print("bucket2 is: ", bucket2)
##      else:
##        getErrorString()
#    return regCmd, role, bucket, bucket2

#def checkRegistrationStatus(bucketName, regCmd, counter = 0):
#  checkRegStatusCmd = "aws lakeformation describe-resource --resource-arn arn:aws:s3:::"+bucketName
#  regStatus = isS3Registered(checkRegStatusCmd)
#  if regCmd == "reg":
#    if not regStatus:
#      if counter < 4:
#        counter += 1
#        logString = "About to sleep 60 seconds before retrying cli command in case a latency problem is causing delayed response. "
#        print(logString)
#        time.sleep(60)
#        checkRegistrationStatus(bucketName, regCmd, counter)
#      else:
#        logString = "ERROR: s3 Bucket is not registered with lake formation even though we ran the registration command. "
#        print(logString)
#        sys.exit(1)
#  elif regCmd == "dereg":
#    if regStatus:
#      if counter < 6:
#        counter += 1
#        logString = "About to sleep 60 seconds before retrying cli command in case a latency problem is causing delayed response. "
#        print(logString)
#        time.sleep(60)
#        checkRegistrationStatus(bucketName, regCmd, counter)
#      else:
#        logString = "ERROR: s3 Bucket has not been deregistered despite having run the deregistration command. "
#        print(logString)
#        sys.exit(1)

#def emptyTheSecurityGroups(sgids):
#  for sgid in sgids:
#    sgrCmds = getSecurityGroupRules(sgid,"before")
#    for sgrCmd in sgrCmds:
#      revokeSecurityGroupRule(sgrCmd, sgid)
#    #print("sgrs is: ", sgrCmds)

#def emptyOneSecurityGroup(sgid):
#  sgrCmds = getSecurityGroupRules(sgid,"before")
#  for sgrCmd in sgrCmds:
#    logString = "DELETE ATTEMPT: About to call revokeSecurityGroupRule(sgrCmd, sgid).  Command sent into function is: "+sgrCmd
#    print(logString)
#    revokeSecurityGroupRule(sgrCmd, sgid)
#  #print("sgrs is: ", sgrCmds)

#def deleteAllFileSystemsThatHaveTag(getFsCmd, account):
#  print("3x")
#  fileSystemIds=getFileSystems(getFsCmd,account,"before")
#  print("1 fileSystemIds contains: ", fileSystemIds)
#  if fileSystemIds:
#    print("INFO: About to get and delete mount targets for each file system. ")
#    for fsid in fileSystemIds:
#      print("a fsid is: ", fsid)
#      mountTargetIds=getMountTargets(fsid, "before")
#      print("a mountTargetIds contains: ", mountTargetIds)
#      for mtid in mountTargetIds:
#        deleteMountTargets(mtid)
#    #fileSystemIds=getFileSystems(getFsCmd,account)
#    print("INFO: Finished getting and deleting mount targets for each file system.  Sleeping 60 seconds to allow deletions to propagate to reduce likelihood of latency problems downstream.")
#    time.sleep(60)
#    print("INFO: About to report results of deleting mount points.  If there are any mountTargetIds below, then a latency problem is still preventing propagation of the deletions we ran above.  ")
#    print("2 fileSystemIds contains: ", fileSystemIds)
#    for fsid in fileSystemIds:
#      print("b fsid is: ", fsid)
#      mountTargetIds=getMountTargets(fsid, "after")
#      print("b mountTargetIds contains: ", mountTargetIds)
#    print("INFO: About to delete file systems.  Sleeping an additional 60 seconds to allow more time for the dependencies of each file system to complete deletion, and thus to reduce risk of failure to delete file systems. ")
#    time.sleep(60)
#    print("3 fileSystemIds contains: ", fileSystemIds)
#    for fsid in fileSystemIds:
#      print("c fsid is: ", fsid)
#      deleteFileSystem(fsid)
#    print("4x")
#    print("INFO: Finished deleting file systems. About to sleep 60 seconds to allow the deletions to propagate. ")
#    time.sleep(60)
#    fileSystemIds=getFileSystems(getFsCmd,account,"after")
#    print("4 fileSystemIds contains: ", fileSystemIds)



# Run script with: python aws-building-blocks\scripts\registerS3AndRole.py reg role="LF-GlueServiceRole" bucket="lf-data-lake-$awsAccountId" bucket2="lf-workshop-"$awsAccountId"
# Run script with: python aws-building-blocks\scripts\registerS3AndRole.py dereg bucket="lf-data-lake-$awsAccountId"

####################################################################################################
### Set Up
####################################################################################################
print("script 1")
createConfigAndCredentialsAWS()
print("script 2")
accountNumber = getAccount()
print("script 3")
#regCmd, roleName, bucketName, bucket2Name= processInputArgs(inputArgs)
#print("regCmd 3 is: ", regCmd)
#print("bucketName is: ", bucketName)
#print("bucket2Name is: ", bucket2Name)
#sys.exit(1)

####################################################################################################
### Register or De-Register bucket and role
####################################################################################################
#if regCmd == "reg":
#  myCmd = 'aws lakeformation register-resource --resource-arn arn:aws:s3:::'+bucketName+' --no-use-service-linked-role --role-arn "arn:aws:iam::'+accountNumber+':role/'+roleName+'"'
#  print("myCmd register-resource is: ", myCmd)
#  runRegistrationCommand(myCmd)
#  if (bucketName==''):
#    logString = "ERROR: bucketName does not contain a value.  Please check your parameters.  Halting program so you can identify the root cause of the problem and avoid downstream errors. "
#    print(logString)
#    sys.exit(1)
#elif regCmd == "dereg":
#  myCmd = 'aws lakeformation deregister-resource --resource-arn arn:aws:s3:::'+bucketName
#  print("myCmd deregister-resource is: ", myCmd)
#  runRegistrationCommand(myCmd)

####################################################################################################
### Empty the s3 Buckets.
####################################################################################################
#  print("bucketName is: ", bucketName)
#  print("bucket2Name is: ", bucket2Name)
#  emptyCmd1 = 'aws s3 rm s3://'+bucketName+' --recursive'
#  runEmptyS3BucketCommand(emptyCmd1)
#  emptyCmd2 = 'aws s3 rm s3://'+bucket2Name+' --recursive'
#  runEmptyS3BucketCommand(emptyCmd2)


############################### Indenting next 50 lines as test

vpcid=getVPC("LF-Workshop-VPC")
print("1 vpcid is: ", vpcid)
if vpcid == -1:
  print("WARNING:  Unable to find VPC after several tries.  Program will continue execution based on the assumption that the VPC has already been deleted.  ")
else:
####################################################################################################
### Delete security group rules.  Doing this early to Leave time to accommodate latency issues.
####################################################################################################
#  print("INFO: About to delete security group rules. First attempt.  ")
#  #Delete security group rules the first time.
#  sgids=getSecurityGroups(vpcid, "before")
#  print("1 sgids is: ", sgids)
#  print("1 len(sgids) is: ", str(len(sgids)))
#  print("INFO: About to revoke security group rules. Doing this before deleting file systems in order to allow more time to propagate. ")
#  emptyTheSecurityGroups(sgids)

####################################################################################################
### Delete File Systems
####################################################################################################
  getFsCmd="aws efs describe-file-systems"
  account=getAccount()
#  deleteAllFileSystemsThatHaveTag(getFsCmd, account)
  print("Sleep 60 seconds before checking again to confirm file systems are deleted. ")
  time.sleep(60)
  print("About to check again to confirm file systems are deleted. ")
  fileSystemIds=getFileSystems(getFsCmd,account,"after")
  print("5 fileSystemIds contains: ", fileSystemIds)
#start section to delete
  if fileSystemIds != None:
    for fsid in fileSystemIds:
       print("b fsid is: ", fsid)
       mountTargetIds=getMountTargets(fsid, "after")
       print("b mountTargetIds contains: ", mountTargetIds)
#end section to delete

#  if fileSystemIds != None:
#    print("About to delete file systems again, given that some still exist.")
#    deleteAllFileSystemsThatHaveTag(getFsCmd, account)

##########################

####################################################################################################
### Delete security group rules a second time in case latency caused problems in previous attempt
####################################################################################################
#  print("INFO: About to delete security group rules. Second attempt.  ")
#  #Delete security group rules the first time.
#  sgids=getSecurityGroups(vpcid, "before")
#  print("1 sgids is: ", sgids)
#  print("1 len(sgids) is: ", str(len(sgids)))
#  print("INFO: About to revoke security group rules. Second attempt. ")
#  emptyTheSecurityGroups(sgids)

#  print("INFO: About to delete security group rules. ")
#  for sgid in sgids:
#    sgrids = getSecurityGroupRules(sgid,"after")
#    print("sgids for ", sgid," after deleting rules is: ", len(sgrids))

####################################################################################################
### Confirm whether or not security group rules have been deleted
####################################################################################################
#  #Check to confirm whether each security group rule has been deleted.
#  sgids=getSecurityGroups(vpcid, "before")
#  print("1 sgids is: ", sgids)
#  print("1 len(sgids) is: ", str(len(sgids)))
#  print("INFO: About to check whether or not each security group rule has been deleted. ")
#  for sgid in sgids:
#    checkSecurityGroupRule(sgid)

####################################################################################################
### Delete security groups 
####################################################################################################
#  print("INFO: About to delete security groups.  But going to try to delete the security group rules in each security group one at a time one more time because sometimes the rules resist deletion or have latency problems with deletion. ")
#  print("2 vpcid is: ", vpcid)
#  for sgid in sgids:
#    emptyOneSecurityGroup(sgid)
#    deleteSecurityGroups(sgid, vpcid)

#.......end indent

#deleteConfigAndCredentialsAWS()