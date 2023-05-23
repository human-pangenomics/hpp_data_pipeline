#! /usr/bin/env python3

# from a submitter metadata file, create a metadata table like this
# https://github.com/human-pangenomics/hpp_data_pipeline/blob/main/sequencing_data/INSDC/Metadata_Example.tsv

# this means, for every sample, put hifi files in individual columns
# add pedigree info (sex) and population info 

import sys, os, re, argparse, textwrap
import urllib.request

parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=textwrap.dedent('''\

This program creates two tables needed for SRA submissions:
    The Biosample table includes pedigree and family information
    The Metadata table contains one line per unique sample+library combination

Input is the submitter metadata table that contains a number of expected fields (see
these files: https://github.com/human-pangenomics/hpp_data_pipeline/tree/main/sequencing_data/INSDC)
Any additional fields are added to the end of the expected fields.
Empty columns are deleted with a warning (often the 'notes' column). 
Expected inputs (hardcoded in the program) are these two files:
   20131219.populations.tsv
   20130606_g1k.ped
They will be downloaded if needed.

   Outputs: sra_biosample_<infile>
            sra_metadata_<infile>
        '''))
group = parser.add_argument_group('required arguments')
group.add_argument('inputfile', type=str, help='Submitter metadata converted to tsv, e.g. HPRC_PacBio_HiFi_Metadata_Submission_UW_Yr3.tsv')

if len(sys.argv)==1:
    parser.print_help()
    sys.exit(1)
args = parser.parse_args()

def slistAdd(sList, line, colDict):
    '''Add new line to sample info if the sample+library combination exists '''
    fields = line.strip('\n').split("\t")
    sidloc = colDict['sample_name']
    libloc = colDict['library_ID']
    for s in sList:
        if fields[sidloc] == s.sName and fields[libloc] == s.libName:
            s.add(fields)
            return sList
    s = Sample(fields, colDict)
    sList.append(s)
    return sList

class Sample():
    '''Sample object keeps track of all files for this sample'''
    def __init__(self, fields, colDict):
        self.fnameloc = colDict['filename']
        sidloc = colDict['sample_name']
        libloc = colDict['library_ID']
        self.sFiles = [fields[self.fnameloc]]
        self.sName = fields[sidloc]
        self.libName = fields[libloc]
        self.fields = fields # only for initial since all relevant fields are the same
    def add(self, fields):
        self.sFiles.append(fields[self.fnameloc])
    def print_biosample(self, sraFields, pedigree):
        sraFields['sample_name'] = sraFields['isolate'] = self.sName
        sraFields['sex'] = pedigree[self.sName]['sex']
        sraFields['population'] = pedigree[self.sName]['population']
        sraFields['family id'] = pedigree[self.sName]['family id']
        return('\t'.join([v for v in sraFields.values()]))
    def print_metadata(self, filenameList, colDict):
        # remove any paths
        for i in range(len(self.sFiles)):
            filenameList[i] = os.path.basename(self.sFiles[i])
        # print every index in colDict, but replace filename with the filenameList
        for c in colDict:
            if c == 'title':
                colDict[c] = 'PacBio HiFi sequencing of ' + self.sName
            elif c == 'assembly':
                colDict[c] = 'unaligned'
            elif c == 'fasta_file':
                colDict[c] = ''
            elif c == 'filename':
                colDict[c] = '\t'.join(filenameList)
            else:
                entry = self.fields[colDict[c]]
                colDict[c] = entry 
        return('\t'.join(v for v in colDict.values()))

def special_changes(sampleList):
    '''special sample'''
    for s in sampleList:
        if s.sName == 'MGISTL_PAN027_HG06807':
            fields = ['HG06807' if x == 'MGISTL_PAN027_HG06807' else x for x in s.fields]
            s.fields = fields
            s.sName = 'HG06807'

def download_if_needed(pedfile, popfile):
    '''get the pedigree and population files if we don't already have them'''
    if not os.path.exists(pedfile):
        print('cannot find {}, downloading'.format(pedfile))
        urllib.request.urlretrieve('ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/technical/working/20130606_sample_info/20130606_g1k.ped', 
            filename = pedfile)
    if not os.path.exists(popfile):
        print('cannot find {}, downloading'.format(popfile))
        urllib.request.urlretrieve('ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/phase3/20131219.populations.tsv',
            filename = popfile)

def biodata(pedfile, popfile):
    '''Extract info needed to populate biosample table'''
    #these are the required column headers in Biosample_example.xlsx
    sra_biodata = { 'sample_name': None,
        'organism': 'Homo sapiens',
        'isolate': None,
        'age': 'No data',
        'biomaterial_provider': 'Coriell Institute',
        'sex': None,
        'tissue': 'B-Lymphocyte',
        'population': None,
        'family id': None }
    download_if_needed(pedfile, popfile)
    # isolate and sample_name are the same thing and can be derived from the metadata
    # population is defined in 20131219.populations.tsv
    population = dict() # code as key, full description as value
    with open(popfile, 'r') as f:
        f.readline() # skip header
        for line in f:
            if re.match(r'\s', line):
                break
            fields = line.strip().split("\t")
            population[fields[1]] = fields[0]
    # sex and family id can be found in 20130606_g1k.ped
    pedigree = dict()
    with open(pedfile, 'r') as f:
        f.readline() # skip header
        for line in f:
            if re.match(r'\s', line):
                break
            fields = line.strip().split("\t")
            pedigree[fields[1]] = dict()
            pedigree[fields[1]]['family id'] = fields[0]
            pedigree[fields[1]]['sex'] = 'female' if fields[4] == '2' else 'male'
            pedigree[fields[1]]['population'] = population[fields[6]]
    # manual addition
    sample = 'HG06807'
    pedigree[sample] = dict()
    pedigree[sample]['family id'] = '3559'
    pedigree[sample]['sex'] = 'female' 
    pedigree[sample]['population'] = 'No data'
    return sra_biodata, pedigree

def map_cols(header, colDict):
    '''Get header index of every expected column'''
    colnames = header.strip().split("\t")
    colDict = {k:v for (k,v) in colDict.items() if not k in ['filename2', 'filename3', 'filename4']}
    for c in colDict.keys():
        if c == 'sample_name':
            colDict[c] = colnames.index('sample_ID')
        elif c in ['title', 'assembly', 'fasta_file']:
            # 'PacBio HiFi sequencing of <sample_ID>'
            # 'unaligned'
            # ''
            pass
        elif c in colnames:
            colDict[c] = colnames.index(c)
        else:
            print('WARNING, notfound', c)
    removeIdx = [ k for k in colDict.values() if k is not None ] 
    # we don't want these two
    for c in ['md5sum','file_size']:
        if c in colnames:
            removeIdx.append(colnames.index(c))
    for loc in range(len(colnames)):
        if not loc in removeIdx:
            colDict[colnames[loc]] = loc 
    return(colDict)
    
def removeEmpty(colMapDict):
    # check if any columns are empty
    emptyCols = []
    for k,v in colMapDict.items():
        if v == None:
            continue
        empty=True
        for s in samplesList:
            if s.fields[v] != '':
                empty=False
                break
        if empty is True:
            print('WARNING, empty colunn, skipping:', k, file=sys.stderr)
            emptyCols.append(k)
    for c in emptyCols:
        del colMapDict[c]
    return colMapDict


# Main

# these are the colnames in the github example
expected_meta = ['sample_name', 'library_ID', 'title', 'library_strategy', 'library_source', 'library_selection', 'library_layout', 'platform', 'instrument_model', 'design_description', 'filetype', 'filename', 'filename2', 'filename3', 'filename4', 'assembly', 'fasta_file', 'shear_method', 'size_selection', 'ccs_algorithm']

popfile = '20131219.populations.tsv'
pedfile = '20130606_g1k.ped'
sra_biodata, pedigreedict = biodata(pedfile, popfile)

# Parse the metadata file
# we don't know if the columns are in the same order, so we'll be mapping the expected names
# to the header of the input metadata file (keeping track of them by index)
samplesList = []
with open(args.inputfile, 'r') as f:
    colMapDict = map_cols(f.readline(), dict.fromkeys(expected_meta))
    for line in f:
        samplesList = slistAdd(samplesList, line, colMapDict)
f.close
# rename non-standard sample in WUSTL
special_changes(samplesList)

# first print the biosample data
sampleIDs = []
with open('sra_biosample_'+args.inputfile, 'w') as outf:
    # header
    print('\t'.join([k for k in sra_biodata.keys()]), file=outf)
    for s in samplesList:
        if not s.sName in sampleIDs:
            print(s.print_biosample(sra_biodata.copy(), pedigreedict), file=outf)
            sampleIDs.append(s.sName)
outf.close()

# metadata table
# Remove any columns that have no info at all
colMapDict = removeEmpty(colMapDict)

# a sample/library combination may have any number of bam files, each of which needs its
# own column in the final table
# get max number of files for a single sample
totalFileNr = max([len(s.sFiles) for s in samplesList])
filenamelist = ['filename']
for i in range(2,totalFileNr +1):
    colname = 'filename' + str(i)
    filenamelist.append(colname)
# create the correct number of columns
fnames = '\t'.join(filenamelist)
# empty the list so we can fill it with actual filenames later
filenamelist = ['' for f in filenamelist]

# header
with open('sra_metadata_'+args.inputfile, 'w') as outf:
    # header
    print('\t'.join([fnames if k=='filename' else k for k in colMapDict.keys()]), file=outf)
    for s in samplesList:
        print(s.print_metadata(filenamelist.copy(), colMapDict.copy()), file=outf)


