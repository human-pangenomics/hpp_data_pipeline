#! /usr/bin/env python3

# I know, should use pandas. But pandas is big and this is not that hard.

import sys, os, re, argparse, textwrap, csv

parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=textwrap.dedent('''\

Creates a table with SRA info of released HPRC data.
Input is the result of 
aws s3 ls s3://human-pangenomics/working --recursive --profile <your_profile> > s3.files
and one or more metadata files as created by SRA (metadata-<number>-processed-ok.tsv)
TODO: Add optional Readstats info from QC

        '''))
group = parser.add_argument_group('required arguments')
group.add_argument('--flist', type=str, help='s3 file list')
group.add_argument('--srafile', action='store', nargs='+', type=str, help='one or more SRA metadata files')
group.add_argument('--prepend', type=str, default='s3://human-pangenomics/')

if len(sys.argv)==1:
    parser.print_help()
    sys.exit(1)
args = parser.parse_args()

def collectSra(sfile):
    reader = csv.DictReader(open(sfile), delimiter='\t')
    fnameKeys = None
    for row in reader:
        if not fnameKeys:
            fnameKeys = [x for x in row.keys() if x.startswith('filename')]
        row['found'] = 'no'
        # store the sra info by filename
        for fkey in fnameKeys:
            sraFileInfo[row[fkey]] = row

def addSra(fname, fnamePath, sraDict):
    fields = fnamePath.split('/')
    hprctype = fields[4]
    sample = fields[5]
    # TODO: add more options
    method='PacBio_HiFi' if 'PacBio_HiFi' in fields else 'other'
    return (sample, '\t'.join([fnamePath, sample, method, hprctype, sraDict['accession'], sraDict['study'], sraDict['bioproject_accession'], sraDict['biosample_accession']]))
                 

# Main
sraFileInfo = dict()

for sfile in args.srafile:
    collectSra(sfile)

sampleDict = dict()
# matching bam files look like this 
# 2023-05-03 08:22:13 129136646212 working/HPRC/HG00140/raw_data/PacBio_HiFi/m64136_220717_152248-bc1018.5mc.hifi_reads.bam
print(('\t').join(['file', 'sample', 'method', 'hprc_type', 'accession', 'study', 'bioproject_accession', 'biosample_accession']))
with open(args.flist, 'r') as gs:
    for line in gs:
        line = line.strip()
        if line.endswith('bam'):
            # remove the file info
            line = line.split()[-1]
            fname = os.path.basename(line)
            if fname in sraFileInfo:
                sample, outline = addSra(fname, args.prepend+line, sraFileInfo[fname])
                sraFileInfo[fname]['found'] = 'yes'
                # these samples are already sorted by the gsutil ls command
                print(outline)

for fname in sraFileInfo:
    if sraFileInfo[fname]['found'] == 'no':
        print('WARNING, not found in released files:', fname, file=sys.stderr)
