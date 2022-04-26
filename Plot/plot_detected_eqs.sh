#!bin/bash
# bash plot_detected_eqs.sh
mkdir ../Locations/evtloc
cp ../REAL/catalog_allday.txt ../Locations/evtloc/
cp ../REAL/catalogSA_allday.txt ../Locations/evtloc/
cp ../Hypoinv/new.cat ../Locations/evtloc/

fig_format=png

# station list
stations='../Locations/staloc/stations.real'

# earthquake catalog
realloc01=1
realloc='../Locations/evtloc/catalog_allday.txt'
realSAloc01=1
realSAloc='../Locations/evtloc/catalogSA_allday.txt'
hypinvloc01=1
hypinvloc='../Locations/evtloc/new.cat'

# study region and depth range
minlon=104.3
maxlon=104.7
inclon=0.1
minlat=29.2
maxlat=29.6
inclat=0.1
mindep=0
maxdep=20
incdep=2

# REAL
if [ $realloc01 == 1 ]
then
gmt begin real_eqs $fig_format
gmt basemap -JM10c -R$minlon/$maxlon/$minlat/$maxlat -BWSen -Bxfa$inclon -Byfa$inclat --MAP_FRAME_TYPE=plain --MAP_TITLE_OFFSET=-6p --FORMAT_GEO_MAP=ddd.xF
awk '{print $1,$2}' $stations | gmt plot -Si0.4c -Gblack -W0.1p,black
gmt makecpt -Ccool -T$mindep/$maxdep/$incdep -D
awk '{print $9,$8,$10}' $realloc | gmt plot -Sc0.15c -W0.5p+cl -C
gmt colorbar -C -Dn0.95/0.1+jBR+h+w5c/0.3c+e+ml -Bxa$incdep+l"Depth (km)"
echo $minlon $minlat "REAL results" | gmt text -F+f14p+jBL -Dj0.2c/1.1c -Glightgray
gmt end show
fi

# REAL RA
if [ $realSAloc01 == 1 ]
then
gmt begin realSA_eqs $fig_format
gmt basemap -JM10c -R$minlon/$maxlon/$minlat/$maxlat -BWSen -Bxfa$inclon -Byfa$inclat --MAP_FRAME_TYPE=plain --MAP_TITLE_OFFSET=-6p --FORMAT_GEO_MAP=ddd.xF
awk '{print $1,$2}' $stations | gmt plot -Si0.4c -Gblack -W0.1p,black
gmt makecpt -Ccool -T$mindep/$maxdep/$incdep -D
awk '{print $8,$7,$9}' $realSAloc | gmt plot -Sc0.15c -W0.5p+cl -C
gmt colorbar -C -Dn0.95/0.1+jBR+h+w5c/0.3c+e+ml -Bxa$incdep+l"Depth (km)"
echo $minlon $minlat "REAL SA results" | gmt text -F+f14p+jBL -Dj0.2c/1.1c -Glightgray
gmt end show
fi

# Hypoinverse
if [ $hypinvloc01 == 1 ]
then
gmt begin hypinv_eqs $fig_format
gmt basemap -JM10c -R$minlon/$maxlon/$minlat/$maxlat -BWSen -Bxfa$inclon -Byfa$inclat --MAP_FRAME_TYPE=plain --MAP_TITLE_OFFSET=-6p --FORMAT_GEO_MAP=ddd.xF
awk '{print $1,$2}' $stations | gmt plot -Si0.4c -Gblack -W0.1p,black
gmt makecpt -Ccool -T$mindep/$maxdep/$incdep -D
awk '{print $6,$5,$7}' $hypinvloc | gmt plot -Sc0.15c -W0.5p+cl -C
gmt colorbar -C -Dn0.95/0.1+jBR+h+w5c/0.3c+e+ml -Bxa$incdep+l"Depth (km)"
echo $minlon $minlat "Hyp1.40 results" | gmt text -F+f14p+jBL -Dj0.2c/1.1c -Glightgray
gmt end show
fi
