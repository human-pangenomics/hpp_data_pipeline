#! /bin/bash

# Follow Julian's example for transfering files from submission to working

subm=$1
case $subm in
    UW2) 
        # UW year 2
        uuid='57361110-d079-4bb0-ac49-b4f6e0407fc0--UW_HPRC_HiFi_Y2'
        EXP='UW_HPRC_HiFi_Y2'
        SUBMISSION_ID='57361110-d079-4bb0-ac49-b4f6e0407fc0'
        ;;
    UW3) 
        # UW year 3
        uuid='5c68b972-8534-402f-9861-11c93558765f--UW_HPRC_HiFi_Y3'
        EXP='UW_HPRC_HiFi_Y3'
        SUBMISSION_ID='5c68b972-8534-402f-9861-11c93558765f'
        ;;
    WUSTL2) 
        # WUSTL year 2
        uuid='b544dcc2-9e98-4cfb-b19e-0cda52a97541--WUSTL_HPRC_HiFi_Year2'
        EXP='WUSTL_HPRC_HiFi_Year2'
        SUBMISSION_ID='b544dcc2-9e98-4cfb-b19e-0cda52a97541'
        ;;
    WUSTL3) 
        # WUSTL year 3
        uuid='c0de0f97-f422-4057-90bd-12b40869d30a--WUSTL_HPRC_HiFi_Year3'
        EXP='WUSTL_HPRC_HiFi_Year3'
        SUBMISSION_ID='c0de0f97-f422-4057-90bd-12b40869d30a'
        ;;
    *)
        echo "PLEASE give argument [UW2, UW3, WUSTL2, WUSTL3]"
        exit;
        ;;
esac
        
EC2='35.167.52.209' # this changes every time you start a machine, so update this
profile='pgdev'     # set this to your own s3 profile
keyfile="~/.ssh/jeltje-key1.pem" # key file for EC2 instance

###############################################################################
##                        Local: Create Transfer CSVs                        ##
###############################################################################


## Pull all files in directory
if [ ! -f "$EXP.source_ec2.txt" ]; then 
  aws s3 ls --recursive --profile $profile\
    s3://human-pangenomics/submissions/$uuid/ \
    | awk '{ print $4 }' | grep bam  > $EXP.source_ec2.txt
fi


# UW Y3 has mc files; use only those
if [[ $EXP == 'UW_HPRC_HiFi_Y3' ]]; then
    sed -i  '/5mc/!d' $EXP.source_ec2.txt
fi

## Add in bucket name (EC2)
sed -i  's/^submissions/s3:\/\/human-pangenomics\/submissions/' $EXP.source_ec2.txt

## Create destination file and then reorganize structure
cp $EXP.source_ec2.txt $EXP.destination_ec2.txt

## copy the 5mc files to the correct location
## we ran primrose ourselves on this submission so we're releasing our files, which we
## first uploaded to the correct submissions directory under a 5mc_bam subdir
if [[ $EXP == 'UW_HPRC_HiFi_Y3' ]]; then
    sed 's/5mc_bam/PacBio_HiFi/' $EXP.source_ec2.txt > $EXP.destination_ec2.txt

fi

sed -i  "s/submissions\/$uuid/working\/HPRC/" \
    $EXP.destination_ec2.txt

# WU Y2 is already in a raw_data subdir on the submissions side
if [[ $EXP != 'UW_HPRC_HiFi_Y2' ]]; then
    sed -i  "s/\/PacBio_HiFi/\/raw_data\/PacBio_HiFi/" \
        $EXP.destination_ec2.txt
fi

if [[ $EXP == 'WUSTL_HPRC_HiFi_Year3' ]]; then
    # the MGISTL files are the only ones that need to be in HPRC_PLUS
    sed -i 's/working\/HPRC\/MGISTL_PAN027_HG06807/working\/HPRC_PLUS\/HG06807/' $EXP.destination_ec2.txt
fi

## Combine into one transfer manifest; delete intermediate files
paste -d ',' $EXP.source_ec2.txt $EXP.destination_ec2.txt  \
    | grep bam | grep hifi >$EXP.transfer_ec2.csv

#rm $EXP.source_ec2.txt $EXP.destination_ec2.txt

## Create GCP version
sed 's/s3:\/\/human-pangenomics/gs:\/\/fc-4310e737-a388-4a10-8c9e-babe06aaf0cf/g' \
    $EXP.transfer_ec2.csv \
    | grep bam | grep hifi >$EXP.transfer_gcp.csv

###############################################################################
##                           Segregate By Cohort                             ##
###############################################################################

## Uncomment when the submission contains both HPRC and HPRC_PLUS samples
## also update the ssds command accordingly

#cat $EXP.transfer_ec2.csv | grep -f HPRC_samples.txt >  $EXP.transfer_ec2_HPRC.csv 
#cat $EXP.transfer_gcp.csv | grep -f HPRC_samples.txt >  $EXP.transfer_gcp_HPRC.csv 
#
#cat $EXP.transfer_ec2.csv | grep -f HPRC_PLUS_samples.txt >  $EXP.transfer_ec2_HPRC_PLUS.csv 
#cat $EXP.transfer_gcp.csv | grep -f HPRC_PLUS_samples.txt >  $EXP.transfer_gcp_HPRC_PLUS.csv 
#
#sed -i  's/HPRC/HPRC_PLUS/' \
#    $EXP.transfer_ec2_HPRC_PLUS.csv 
#
#sed -i  's/HPRC/HPRC_PLUS/' \
#    $EXP.transfer_gcp_HPRC_PLUS.csv 
#

###############################################################################
##                           Launch EC2 Instance                             ##
###############################################################################
cat <<TOEND

#GET ON THE EC2 INSTANCE

ssh -i $keyfile ubuntu@$EC2

#AND RUN

. py37-venv/bin/activate

export AWS_PROFILE=s3-upload

pip3 install --upgrade --no-cache-dir git+https://github.com/DataBiosphere/ssds@dev
TOEND


###############################################################################
##                          Upload Transfer CSVs                             ##
###############################################################################

#scp -i $keyfile \
#    $EXP.transfer_ec2.csv \
#    ubuntu@$EC2:~

#scp -i $keyfile \
#    $EXP.transfer_gcp.csv \
#    ubuntu@$EC2:~

###############################################################################
##                           EC2: Execute Transfers                          ##
###############################################################################

# print the command
cat <<TOEND 
RUN THIS ON THE EC2 INSTANCE:

ssds staging release \
    --deployment default \
    --submission-id $SUBMISSION_ID \
    --transfer-csv $EXP.transfer_ec2.csv \
    &>$EXP.transfer_aws.stdout &

ssds staging release \
    --deployment gcp \
    --submission-id $SUBMISSION_ID \
    --transfer-csv $EXP.transfer_gcp.csv \
    &>$EXP.transfer_gcp.stdout &

grep -i 'ERROR' $EXP.transfer_aws_HPRC.stdout
grep -i 'ERROR' $EXP.transfer_gcp_HPRC.stdout
TOEND



###############################################################################
##                                 DONE                                      ##
###############################################################################
