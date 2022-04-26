#!/usr/bin/perl -w

$phaseSAall = "phaseSA_allday.txt";
open(OUT,">$phaseSAall");

my @hypophase_files = <????????.hypophase.dat>;

$ID = 0;
# this is necessary. otherwise, uninitialized $nn
$nn = 0;
# will be given to already initialized $ID -> error
foreach my $hypophase_file (@hypophase_files){
    open(EV,"<$hypophase_file");
    @par = <EV>;
    close(EV);

    foreach $_(@par){
	    chomp($_);
            $beigin = substr($_,0,1);
            if($beigin eq "#"){
            ($jk,$year,$month,$day,$hour,$min,$sec,$evla,$evlo,$evdp,$evmg,$EH,$EZ,$RMS,$nn) = split(" ",$_);chomp($nn);
            $nn=$nn+$ID;
            printf OUT "%1s %04d %02d %02d %02d %02d %06.3f  %8.4f  %9.4f  %6.3f %5.2f %7.2f %7.2f %7.2f      %06d\n",$jk,$year,$month,$day,$hour,$min,$sec,$evla,$evlo,$evdp,$evmg,$EH,$EZ,$RMS,$nn;
            }else{print OUT "$_\n";}
    }
    $ID=$nn;
}
close(OUT);


#events with large number of picks and small station gap
#can be used for velocity model updation in VELEST
$numps = 3; # minimum number of P and S picks
$gap = 180; # largest station gap

$phaseall = "phase_allday.txt";
$catalogall = "catalog_allday.txt";
$catalogSAall = "catalogSA_allday.txt";
$phasebest = "phase_best_allday.txt";

`cat *.phase_sel.txt > $phaseall`;
`cat *.catalog_sel.txt > $catalogall`;
`cat *.hypolocSA.dat > $catalogSAall`;

&PhaseBest($phaseall,$phasebest,$numps,$gap); # maybe used for velocity model updating in VELEST
&PhaseAll($phaseall); # will be used in VELEST 

sub PhaseAll{
    my($file) = @_;
	open(JK,"<$file");  
	@par = <JK>;
	close(JK);
    
    $num = 0;
    open(OT,">$file");
	foreach $file(@par){
        chomp($file);
		($test,$jk) = split(' ',$file);
		if($test =~ /^\d+$/){
			($jk,$year,$mon,$dd,$time,$ot,$std,$lat,$lon,$dep,$mag,$jk,$nofp,$nofs,$nofps,$nboth,$gap) = split(' ',,$file);
			($hour,$min,$sec) = split('\:',$time);
			$num++;
			print OT "# $year  $mon  $dd   $hour    $min    $sec    $lat    $lon    $dep     $mag     0.0     0.0    0.0    $num\n";
		}else{
			($net,$station,$phase,$traveltime,$pick,$amplitude,$res,$prob,$baz) = split(' ',$file);
			print OT "$station $pick $prob $phase\n";
		}
	}
    close(OT);
}

sub PhaseBest{
    my($filein,$fileout,$numps,$gap0) = @_;
	open(JK,"<$filein");  
	@par = <JK>;
	close(JK);
    
    $num = 0;
    open(OT,">$fileout");
	foreach $file(@par){
		($test,$jk) = split(' ',$file);
        if($test =~ /^\d+$/){
            ($jk,$year,$mon,$dd,$time,$ot,$std,$lat,$lon,$dep,$mag,$jk,$nofp,$nofs,$nofps,$nboth,$gap) = split(' ',,$file);
            ($hour,$min,$sec) = split('\:',$time);
            $iok = 0;
            if($nofps >= $numps && $gap <= $gap0){
			    $num++;
			    print OT "# $year  $mon  $dd   $hour    $min    $sec    $lat    $lon    $dep     $mag     0.0     0.0    0.0   $num\n";
                $iok = 1;
            }
         }else{
             if($iok == 1){
            ($net,$station,$phase,$traveltime,$pick,$amplitude,$res,$prob,$baz) = split(' ',$file);
            print OT "$station $pick $prob $phase\n";
            }
		}
	}
    close(OT);
}


sub Timeadd{
   my($yyear,$mm,$dday,$adday) = @_;
   $dday = $dday + $adday;	
   if (($mm==1) || ($mm==3) || ($mm==5) || ($mm==7) || ($mm==8) || ($mm==10) || ($mm==12)){
      if ($dday >31) {
         $dday = 1;
         $mm = $mm + 1;
         if ($mm > 12) {
            $mm = 1;
            $yyear = $yyear + 1;
         }
      }
   }    
   if (($mm==4) || ($mm==6) || ($mm==9) || ($mm==11)){
      if ($dday >30) {
         $dday = 1;
         $mm = $mm + 1;
         if ($mm > 12) {
            $mm = 1;
            $yyear = $yyear + 1;
         }
      }
   }    
   if ($mm == 2) {
      if ((($yyear%4 == 0) && ($yyear%100 != 0)) || ($yyear%400 == 0)){
         if ($dday >29) {
            $dday = 1;
            $mm = $mm + 1;
         }
      }
      else{
        if ($dday >28) {
            $dday = 1;
            $mm = $mm + 1;
         }
      }
   }

   my @time = ($yyear,$mm,$dday);
   return(@time);
}
