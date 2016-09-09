#!/bin/bash

function gengxin() {
	for ip in `cat dbgate.cn.txt`
	do
		echo $ip
		scp -p -o StrictHostKeyChecking=no * root@$ip:/usr/local/scripts/
	done
}

gengxin
