#!/usr/bin/env python3

import sys
from Bio import SeqIO
import requests
from datetime import datetime

protein_count = int(sys.argv[1])

# create output genbank file for entire database
with open("ipd-mhc-nhp-prot-" + datetime.today().strftime('%Y-%m-%d') + ".fasta", "a") as all_nhp:

  # create output genbank file for rhesus only
  with open("ipd-mhc-mamu-prot-" + datetime.today().strftime('%Y-%m-%d') + ".fasta", "a") as mamu:

    # create output genbank file for cyno only
    with open("ipd-mhc-mafa-prot-" + datetime.today().strftime('%Y-%m-%d') + ".fasta", "a") as mafa:

      # create output genbank file for mane only
      with open("ipd-mhc-mane-prot-" + datetime.today().strftime('%Y-%m-%d') + ".fasta", "a") as mane:
        
        # make range of ids to download from ebi
        nhp_id = range(1, protein_count)
        
        # add leading zeros and nhp prefix
        # this is the EBI dbfetch format
        nhp_id = ['NHP' + str(item).zfill(5) for item in nhp_id]
        
        # iterate over all NHP files to retrieve
        for i in nhp_id:     
          
          # get record
          u = requests.get("https://www.ebi.ac.uk/Tools/dbfetch/dbfetch?db=ipdmhcpro;id=" + i + ";style=raw")
          
          ipd_fasta = u.text # read content
          
          ipd_fasta.write(record, all_nhp, "fasta")
          
          # if rhesus sequence
          if 'Mamu' in record.id:
            ipd_fasta.write(record, mamu, "fasta")
          
          # if cyno sequence
          if 'Mafa' in record.id:
            ipd_fasta.write(record, mafa, "fasta")
          
          # if mane sequence
          if 'Mane' in record.id:
            ipd_fasta.write(record, mane, "fasta")

