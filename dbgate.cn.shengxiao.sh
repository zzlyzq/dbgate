#!/bin/bash

function fabu() {
	for ip in `cat dbgate.cn.txt`
	do
		echo $ip
		scp -o StrictHostKeyChecking=no common.cfg root@$ip:/etc/haproxy/
		ssh -o StrictHostKeyChecking=no root@$ip "service haproxy reload || service haproxy restart"
	done
}

python dbgate.cn.shengxiao.py && fabu
./dbgate.cn.allupdate.sh
