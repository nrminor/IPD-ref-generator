#!/usr/bin/env python3

# -*- coding: utf-8 -*-
"""27453-download-ipd.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1FuxOmf46uVM9-kYeO27YBJF8AzJs2_0P
"""

# requests installed by default in google colab
# install biopython
# !pip install biopython

import sys
from Bio import SeqIO
import requests
from datetime import datetime

embl_accession = sys.argv[1]
allele_name = sys.argv[2]

# create output genbank file for entire database
with open("ipd-mhc-nhp-" + datetime.today().strftime('%Y-%m-%d') + "_" + str(embl_accession) + ".gbk", "a") as all_nhp:

  if allele_name.startswith('Mamu'):
    # create output genbank file for rhesus only
    with open("ipd-mhc-mamu-" + datetime.today().strftime('%Y-%m-%d') + "_" + str(embl_accession) + ".gbk", "a") as mamu:

      # get record
        u = requests.get("https://www.ebi.ac.uk/Tools/dbfetch/dbfetch?db=embl&id=" + embl_accession + "&style=raw")

        
        ipd_embl = u.text # read content
        
        # handle missing records
        # these don't have identifiers and can be skipped
        if not ipd_embl.startswith('ID'):
          all_nhp.close()
          mamu.close()
        else:
          # IPD MHC uses non-standard ID line
          # need to remove first two semicolons in ID line
          ipd_line = ipd_embl.splitlines() # split by line
          id_line = ipd_line[0] # get ID line
          id_line_split = id_line.split(';') # split elements by semicolon
  
          # reconstruct ID line in EMBL format that can be parsed by biopython
          ipd_line[0] = id_line_split[0] + ' ' + id_line_split[1] + ' ' + id_line_split[4] + '; ' + id_line_split[3] + '; ' + id_line_split[5] + '; ' + id_line_split[6]
  
          # join lines to create embl file
          embl_file = ('\n').join(ipd_line)
  
          # create temporary file in correct EMBL format
          # i tried to use tempfile but couldn't get it to work
          with open("response.embl", "w") as f:
              f.write(embl_file)
  
          # read EMBL file and export as Genbank
          for record in SeqIO.parse("response.embl", "embl"):
            
              record.description = record.name
              record.name = allele_name
              
              SeqIO.write(record, all_nhp, "genbank")
  
              # write rhesus only genbank file
              SeqIO.write(record, mamu, "genbank")
  
  # if cyno sequence
  elif allele_name.startswith('Mafa'):
    # create output genbank file for cyno only
    with open("ipd-mhc-mafa-" + datetime.today().strftime('%Y-%m-%d') + "_" + str(embl_accession) + ".gbk", "a") as mafa:
      # get record
        u = requests.get("https://www.ebi.ac.uk/Tools/dbfetch/dbfetch?db=embl&id=" + embl_accession + "&style=raw")
        
        ipd_embl = u.text # read content
        
        # handle missing records
        # these don't have identifiers and can be skipped
        if not ipd_embl.startswith('ID'):
          all_nhp.close()
          mafa.close()
        else:
          # IPD MHC uses non-standard ID line
          # need to remove first two semicolons in ID line
          ipd_line = ipd_embl.splitlines() # split by line
          id_line = ipd_line[0] # get ID line
          id_line_split = id_line.split(';') # split elements by semicolon
  
          # reconstruct ID line in EMBL format that can be parsed by biopython
          ipd_line[0] = id_line_split[0] + ' ' + id_line_split[1] + ' ' + id_line_split[4] + '; ' + id_line_split[3] + '; ' + id_line_split[5] + '; ' + id_line_split[6]
  
          # join lines to create embl file
          embl_file = ('\n').join(ipd_line)
  
          # create temporary file in correct EMBL format
          # i tried to use tempfile but couldn't get it to work
          with open("response.embl", "w") as f:
              f.write(embl_file)
  
          # read EMBL file and export as Genbank
          for record in SeqIO.parse("response.embl", "embl"):
            
              record.description = record.name
              record.name = allele_name
              
              SeqIO.write(record, all_nhp, "genbank")
  
              # write cyno specific genbank file
              SeqIO.write(record, mafa, "genbank")

  # if mane sequence
  else:

    # create output genbank file for mane only
      with open("ipd-mhc-mane-" + datetime.today().strftime('%Y-%m-%d') + "_" + str(embl_accession) + ".gbk", "a") as mane:

        # get record
        u = requests.get("https://www.ebi.ac.uk/Tools/dbfetch/dbfetch?db=embl&id=" + embl_accession + "&style=raw")
        
        ipd_embl = u.text # read content
        
        # handle missing records
        # these don't have identifiers and can be skipped
        if not ipd_embl.startswith('ID'):
          all_nhp.close()
          mamu.close()
          mafa.close()
          mane.close()
        else:
          # IPD MHC uses non-standard ID line
          # need to remove first two semicolons in ID line
          ipd_line = ipd_embl.splitlines() # split by line
          id_line = ipd_line[0] # get ID line
          id_line_split = id_line.split(';') # split elements by semicolon
  
          # reconstruct ID line in EMBL format that can be parsed by biopython
          ipd_line[0] = id_line_split[0] + ' ' + id_line_split[1] + ' ' + id_line_split[4] + '; ' + id_line_split[3] + '; ' + id_line_split[5] + '; ' + id_line_split[6]
  
          # join lines to create embl file
          embl_file = ('\n').join(ipd_line)
  
          # create temporary file in correct EMBL format
          # i tried to use tempfile but couldn't get it to work
          with open("response.embl", "w") as f:
              f.write(embl_file)
  
          # read EMBL file and export as Genbank
          for record in SeqIO.parse("response.embl", "embl"):
            
              record.description = record.name
              record.name = allele_name
              
              SeqIO.write(record, all_nhp, "genbank")
  
              # write mane specific genbank file
              SeqIO.write(record, mane, "genbank")

