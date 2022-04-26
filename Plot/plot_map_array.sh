#!/bin/bash
# bash plot_map_array.sh

# study region
lamin=29.2
lamax=29.6
lomin=104.3
lomax=104.7
# relief dataset
earth_relief=earth_relief_03s
# elevation
elmin=-4000
elmax=4000
elstp=500
# scale location and length in km
lasca=29.55
losca=104.40
lesca=5
# station locations
stafile="../Locations/staloc/stations.txt"
# inset region
inlamin=28
inlamax=31
inlomin=102
inlomax=107
# inset map ype
iscoast=0

gmt begin map_array pdf

# main topographic map
gmt basemap -JM6c -R$lomin/$lomax/$lamin/$lamax -Baf
gmt makecpt -Cgeo -T$elmin/$elmax/$elstp -D -Z -H > elevation.cpt
gmt grdimage @$earth_relief -Celevation.cpt -I+
gmt coast -W0.2p,black -Da -Lg$losca/$lasca+jMC+c$lasca+w${lesca}k+f+u -F+glightgray -t30 --FONT_ANNOT_PRIMARY=8p --MAP_SCALE_HEIGHT=3p
gawk -F, '{if (NR>1) print $5,$4}' $stafile | gmt plot -St0.2c -W0.1p,black -Gpink

# inset zoom-out map
gmt basemap -JM1.5c -R$inlomin/$inlomax/$inlamin/$inlamax -Bwesn --MAP_FRAME_TYPE=plain --MAP_FRAME_PEN=0.5p
if [[ $iscoast == 1 ]]
then
gmt coast -W0.2p,black -Da -Slightblue -Gwhitesmoke -A1000 -N1 -N2
else
gmt grdimage @earth_relief_01m -Celevation.cpt -I+
fi

gmt plot -W0.5p,red << EOF
$lomin $lamin
$lomax $lamin
$lomax $lamax
$lomin $lamax
$lomin $lamin
EOF

gmt end show

rm elevation.cpt
