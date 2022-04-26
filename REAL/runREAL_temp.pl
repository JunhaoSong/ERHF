#!/usr/bin/perl -w
$year = "2020";
$mon = "05";
$day = "12";

$D = "$year/$mon/$day/29.40";
$R = "0.3/20/0.02/1/3";
$G = "1.4/20/0.01/1";
$V = "6.0/3.3";
$S = "2/0/4/1/0.5/0.2/1.5/0.5/1.0";

$dir = "./Pick/Eqt/20200512";
$station = "./Locations/staloc/stations.real";
$ttime = "./REAL/tt_db/ttdb.txt";

system("REAL -D$D -R$R -G$G -S$S -V$V $station $dir $ttime");
print"REAL -D$D -R$R -G$G -S$S -V$V $station $dir $ttime\n";
