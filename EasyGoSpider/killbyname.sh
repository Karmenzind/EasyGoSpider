# kill all phantomjs processes

cmd_name=$0
proc_name=$1
echo $proc_name "is to be killed"

IFS='
'
for i in `ps -aux | grep -i $proc_name`
do
	echo $i 2>&1;
	case $i in
		*grep*|*$cmd_name*) echo '[ignored]';;
		*)kill `echo $i | awk -F' ' '{ print $2 }'`; echo '[to be killed]';;
	esac
done
