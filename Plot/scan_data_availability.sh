#!/bin/sh

obspy-scan ../Data/*/*mseed -f MSEED --start-time 20200509 --end-time 20200513 --no-x --no-gaps -o data-availability_scanned_by_obspy.pdf
