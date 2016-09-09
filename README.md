# dbgate
The layer that between hadoop sqoop and mysql servers which used ip filter policy.

# Situation 1
In one department, that uses hadoop sqoop to import or output data to mysql, and the mysql servers use IP source filter policy. 

Just watch the situation above that does't matter, but 

if we want to scale out the hadoop cluster > we should add the all the new IPs with the server that use. 
  if we have 100 mysql dbs, how long will we get this thing done!

if we want to add new mysql, we should add all the hadoop cluster IP with the mysql ip source filter policy.

The dbgate is a method, that we have two servers that running haproxy, proxy the backend mysql db servers, open ip source filter policy that for the hadoop cluster.
