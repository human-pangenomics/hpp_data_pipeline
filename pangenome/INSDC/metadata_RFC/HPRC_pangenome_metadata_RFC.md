# **Pangenome Submission Metadata Proposal (RFC)**


### **Introduction**
This document provides a proposal (from the perspective of the HPRC) for metadata that accompanies pangenome submissions to INSDCs (ENA/SRA/DDBJ). The fields described below are used in the upload of year 1 pangenomes for the HPRC, but they should not be considered final as they will likely change as more projects and submitters upload graph-based structures (assembly graphs and pangenomes) to INSDCs.


## **INSDC metadata fields for analysis object submissions**

_The following fields are already in the [analysis object metadata schema (XSD)](https://ftp.ebi.ac.uk/pub/databases/ena/doc/xsd/sra_1_5/SRA.analysis.xsd). They are listed below to make sure that they are appropriately used in pangenome submissions._


#### Mandatory:

_Note that the fields below are represented in submission XMLs as either attributes or elements and are presented as one table for clarity._

<table>
  <tr>
   <td><strong>TAG</strong>
   </td>
   <td><strong>VALUE</strong>
   </td>
   <td><strong>Rules</strong>
   </td>
   <td><strong>example</strong>
   </td>
  </tr>
  <tr>
   <td>filename
   </td>
   <td>Name of pangenome file
   </td>
   <td>Free text
   </td>
   <td>hprc-v1.0-mc-grch38-maxdel.10mb.gfa.gz
   </td>
  </tr>
  <tr>
   <td>SAMPLE_REF
   </td>
   <td>Samples used in the creation of the pangenome. See ANALYSIS::SAMPLE_REF element in XSD.
   </td>
   <td>[Free text] (Array of BioSample accessions)
   </td>
   <td>[SAMN03283347, SAMN03255769]
   </td>
  </tr>
  <tr>
   <td>Assembly Accession
   </td>
   <td>INSDC accession of the assembly(ies) used in the pangenome.
   </td>
   <td>[Free text] (Array of assembly accessions)
   </td>
   <td>[GCA_009914755.3, GCA_018471515.1]
   </td>
  </tr>
  <tr>
   <td>STUDY_REF
   </td>
   <td>Parent study that the pangenome will be housed in. See ANALYSIS::STUDY_REF element in XSD.
   </td>
   <td>[Free text]
   </td>
   <td>PRJNA730822
   </td>
  </tr>
  <tr>
   <td>filetype
   </td>
   <td>The type of file. 
<p>
Pre-existing requirement, but will add GFA. See filetype attribute of AnalysisFileType in XSD.
   </td>
   <td>Enumerated type {gfa}
   </td>
   <td>gfa
   </td>
  </tr>
  <tr>
   <td>checksum_method
   </td>
   <td>The checksum method. See checksum_method attribute of AnalysisFileType in XSD.
   </td>
   <td>MD5
   </td>
   <td>MD5
   </td>
  </tr>
  <tr>
   <td>checksum
   </td>
   <td>Checksum value. See checksum attribute of AnalysisFileType in XSD.
   </td>
   <td>String
   </td>
   <td>0a5ae55ceb250b6a866261bb67c41cae
   </td>
  </tr>
</table>



## **INSDC metadata fields for Pangenome submissions**

_The following fields are not in the pre-existing XSD (as of July2022). They will not be added to the XSD, but will be included in XML files under the `ANALYSIS_ATTRIBUTES` section (encoded as TAG/VALUE pairs). While not required to create a valid XML, INSDCs may require that some of the fields below (in the mandatory section) are included on their backends._

#### **Mandatory:**


<table>
  <tr>
   <td><strong>TAG</strong>
   </td>
   <td><strong>VALUE</strong>
   </td>
   <td><strong>Rules</strong>
   </td>
   <td><strong>example</strong>
   </td>
  </tr>
  <tr>
   <td>graph type
   </td>
   <td>Type of GFA
   </td>
   <td>Enumerated {assembly graph | pangenome}
   </td>
   <td>pangenome
   </td>
  </tr>
  <tr>
   <td>pangenome name
   </td>
   <td>Name of the pangenome
   </td>
   <td>Free text
   </td>
   <td>hprc-v1.0-mc-chm13-maxdel.10mb
   </td>
  </tr>
  <tr>
   <td>file format version
   </td>
   <td>The format specification and version number of the file
   </td>
   <td>Enumerated type: {GFAv1.0 | GFAv1.1}
   </td>
   <td>GFAv1.1
   </td>
  </tr>
  <tr>
   <td>pipeline
   </td>
   <td>Pipeline used for creating pangenome
   </td>
   <td>Free-text
   </td>
   <td>PGGB
   </td>
  </tr>
  <tr>
   <td>resolution
   </td>
   <td>Asserted precision of the pangenome structure.
   </td>
   <td>Enumerated type:
<p>
{base level | structural Variant}
   </td>
   <td>Base level
   </td>
  </tr>
</table>



#### **Recommended:**


<table>
  <tr>
   <td><strong>TAG</strong>
   </td>
   <td><strong>VALUE</strong>
   </td>
   <td><strong>Rules</strong>
   </td>
   <td><strong>example</strong>
   </td>
  </tr>
  <tr>
   <td>sample name
   </td>
   <td>Common name of sample.
   </td>
   <td>[Free text] (Array of sample names)
   </td>
   <td>[CHM13, GRCh38]
   </td>
  </tr>
  <tr>
   <td>number of nodes
   </td>
   <td>Number of segments, or S lines, in the GFA file.
   </td>
   <td>numeric
   </td>
   <td>424,643
   </td>
  </tr>
  <tr>
   <td>number of components
   </td>
   <td>Connected components in the graph
   </td>
   <td>numeric
   </td>
   <td>25
   </td>
  </tr>
  <tr>
   <td>number of edges
   </td>
   <td>Number of edges/links (GFA L lines) in the pangenome
   </td>
   <td>numeric
   </td>
   <td>637,628
   </td>
  </tr>
  <tr>
   <td>length (bp)
   </td>
   <td>Total number of nucleotides in the nodes/segments in the graph
   </td>
   <td>numeric
   </td>
   <td>3,239,764,787
   </td>
  </tr>
  <tr>
   <td>total path length (bp)
   </td>
   <td>Number of bases in all paths included in the graph
   </td>
   <td>numeric
   </td>
   <td>3,239,764,787
   </td>
  </tr>
  <tr>
   <td>number of paths
   </td>
   <td>Number of paths in the graph.
   </td>
   <td>numeric
   </td>
   <td>230
   </td>
  </tr>
  <tr>
   <td>number of path steps
   </td>
   <td>Total number of visits to nodes by paths
   </td>
   <td>numeric
   </td>
   <td>8,424,643
   </td>
  </tr>
</table>



#### Optional:


<table>
  <tr>
   <td><strong>TAG</strong>
   </td>
   <td><strong>VALUE</strong>
   </td>
   <td><strong>Rules</strong>
   </td>
   <td><strong>example</strong>
   </td>
  </tr>
  <tr>
   <td>primary reference assembly
   </td>
   <td>INSDC accession of the primary reference assembly used (if any). 
   </td>
   <td>Free-text
   </td>
   <td>GCA_000001405.29
   </td>
  </tr>
  <tr>
   <td>reference based
   </td>
   <td>Does the pangenome rely on a reference, or is the pangenome created with all sequences treated equally? (A pangenome can include a reference assembly but not be reference based.)
   </td>
   <td>Boolean
   </td>
   <td>true
   </td>
  </tr>
  <tr>
   <td>cyclic
   </td>
   <td>Is the graph cyclic?
   </td>
   <td>Boolean
   </td>
   <td>true
   </td>
  </tr>
  <tr>
   <td>cyclic reference
   </td>
   <td>Does any reference path have cycles?
   </td>
   <td>Boolean
   </td>
   <td>true
   </td>
  </tr>
  <tr>
   <td>masked region types
   </td>
   <td>Region types (genomic/DNA elements) in the pangenome that are masked or omitted. Example values include: centromeres, telomeres, mitochondrial DNA.
   </td>
   <td>Free text
   </td>
   <td>Centromeres, mitochondrial DNA
   </td>
  </tr>
  <tr>
   <td>masking procedure
   </td>
   <td>Tools that were used to identify region types that were masked or omitted.
   </td>
   <td>Free text
   </td>
   <td>DNA-BRNN
   </td>
  </tr>
</table>

