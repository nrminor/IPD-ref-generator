#!/usr/bin/env python3

import sys
import os
import subprocess

file_dir = os.getcwd()
animal = sys.argv[1]
in_gbk = sys.argv[2]
exemplar = sys.argv[3]

# -*- coding: utf-8 -*-
"""27453-trim-to-miSeq-amplicon.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1trFTPPoS_EH4qzdGQnZFMPicpTW0fbTv

## Purpose

This notebook removes primers from IPD sequences and then deduplicates identical sequences, so that groups of identical sequences can be used when genotyping.

"""


"""## Functions

Define functions used in workflow.
"""

def createFastaFromGenbank(in_gbk, out_fasta):
  '''create FASTA file from Genbank file'''
  from Bio import SeqIO
  from Bio.Seq import Seq
  from Bio.SeqRecord import SeqRecord

  printStatus('Create FASTA file from Genbank file')

  with open(in_gbk) as input_handle, open(out_fasta, "w") as output_handle:
    sequences = SeqIO.parse(input_handle, "genbank")
    SeqIO.write(sequences, output_handle, "fasta") 

  return out_fasta

def vsearchMapToReference(query, ref, out_sam):
  '''map FASTA sequences to exemplar FASTA for miSeq trimming'''
  # map IPD FASTA reads to exemplar sequences
  # SAM output CIGAR strings define where matches begin and end
  # which allows trimming IPD sequences to miSeq amplicon length
  # write samheader so pysam parsing works correctly
  
  printStatus('Map to reference with vsearch usearch_global algorithm')
  
  os.environ['query'] = query
  os.environ['ref'] = ref
  os.environ['out_sam'] = out_sam
  
  subprocess.run('vsearch --usearch_global $query --db $ref --id 0.8 --samheader --samout $out_sam', shell = True)

  # remove intermediate fasta file
  subprocess.run('rm $query', shell = True)

  return out_sam

def trimQueryByMapping(in_sam):
  '''use CIGAR coordinates to trim SAM file to reference length
  return python list with trimmed sequences and sequence names
  '''
  import pysam
  from Bio import SeqIO
  from Bio.Seq import Seq
  from Bio.SeqRecord import SeqRecord

  printStatus('Deterine location of mapped regions of query')

  # import SAM file as pysam object
  samfile = pysam.AlignmentFile(in_sam, 'r', check_sq=False)
  
  os.environ['in_sam'] = in_sam

  # remove temporary sam file
  subprocess.run('rm $in_sam', shell = True)

  # create empty list of lists to store trimmed sequences
  trimmed_sequence = []

  # iterate over each read to determine trim locations
  # save trimmed sequence to list

  for read in samfile:
      if not read.is_unmapped:
          cigar = read.cigar

          # get number of bases to trim from left
          left_trim = 0 # default when there is no left trim
          
          # if the first entry in cigar string is insertion
          # that number of bases needs to be trimmed from sequence
          if cigar[0][0] == 1:
            left_trim = (cigar[0][1])
            # remove bases from left
            left_trimmed = read.seq[left_trim:]
          else:
            left_trimmed = read.seq

          # get number of bases to trim from right
          right_trim = 0 # default when there is no right trim

          if cigar[-1][0] == 1:
            right_trim = (cigar[-1][1])
            # remove bases from right
            right_trimmed = left_trimmed[:-right_trim]
          else:
            right_trimmed = left_trimmed

          # add to list
          trimmed_sequence.append([read.query_name, right_trimmed])

  return trimmed_sequence

def replaceGenbankSequence(in_gbk, trimmed_sequence_list, out_fasta):
  '''substitute trimmed sequences for original sequences in Genbank file
  expects trimmed_sequence_list object.
  outputs FASTA, since original genbank coordinates make no sense'''

  from Bio import SeqIO
  from Bio.Seq import Seq
  from Bio.SeqRecord import SeqRecord

  printStatus('Create trimmed FASTA')

  # load IPD Genbank file as Biopython object
  ipd = SeqIO.parse(in_gbk, "genbank")

  # replace original IPD sequence with trimmed sequence for miSeq genotyping
  # output as FASTA file
  # (Genbank annotation positions make no sense after trimming)
  # edit FASTA headers to be more informative
  with open(out_fasta, "w") as output_handle:
    for record in ipd:
      for i in trimmed_sequence_list:
        if i[0] == record.description:
          record.seq = Seq(i[1])
          record.id = removeSpecialCharacters(record.name)
          SeqIO.write(record, output_handle, "fasta")

  return out_fasta

def deduplicate_fasta(in_fasta, out_fasta):
  '''manually deduplicate FASTA records with identical sequences
  create new FASTA file named with all matching sequences'''

  from Bio import SeqIO
  from Bio.Seq import Seq
  from Bio.SeqRecord import SeqRecord

  printStatus('Remove duplicates in FASTA sequence and rename to retain duplicate names')

  # create dictionary to store names and sequences

  deduplicated = dict()
  unique_seqs = set()

  ipd = SeqIO.parse(in_fasta, "fasta")

  # create a set of unique sequences
  for record in ipd:
    unique_seqs.add(str(record.seq))

  # create another biopython object
  ipd = SeqIO.parse(in_fasta, "fasta")

  # iterate over object.
  # add list elements when sequences match
  for record in ipd:
      for i in unique_seqs:
        if record.seq == i:
          # if key does not exist, add it
          if i not in deduplicated:
            deduplicated[i] = [record.id]
          else:
            deduplicated[i].append(record.id)

  # create deduplicated FASTA file from dictionary
  with open(out_fasta, "w") as output_handle:
    for item in deduplicated.items():
      # concatenate identical sequence names
      seq_name = '|'.join(item[1])
      # get sequence
      deduplicated_sequence = item[0]
      # create biopython object
      record = SeqRecord(
      Seq(deduplicated_sequence),
      id=seq_name,
      description=''
      )
      SeqIO.write(record, output_handle, "fasta")

    return out_fasta

def createMiseqTrimmedFasta(in_gbk, exemplar_fasta):
  '''given an IPD genbank file and an exemplar fasta
  chain together above functions to create FASTA file trimmed to exemplar sequences'''

  # create output file names
  IPD_BASENAME = os.path.basename(in_gbk[:-4])
  IPD_TRIMMED_FASTA = IPD_BASENAME + '.miseq.trimmed.fasta'
  IPD_TRIMMED_DEDUPLICATED_FASTA = IPD_BASENAME + '.miseq.trimmed.deduplicated.fasta'
  
  # make sure file names are available to subprocess environment
  os.environ['IPD_BASENAME'] = IPD_BASENAME
  os.environ['IPD_TRIMMED_FASTA'] = IPD_TRIMMED_FASTA
  os.environ['IPD_TRIMMED_DEDUPLICATED_FASTA'] = IPD_TRIMMED_DEDUPLICATED_FASTA

  # make FASTA
  ipd_fasta = createFastaFromGenbank(in_gbk, 'tmp.fasta')

  # map to reference
  vsearch = vsearchMapToReference('tmp.fasta', exemplar_fasta, 'tmp.sam')

  # calculate trim
  trim_list = trimQueryByMapping('tmp.sam')

  # apply trim to FASTA
  replaceGenbankSequence(in_gbk, trim_list, IPD_TRIMMED_FASTA)

  # deduplicate
  deduplicate_fasta(IPD_TRIMMED_FASTA, IPD_TRIMMED_DEDUPLICATED_FASTA)

  # remove unnecessary intermediate file
  subprocess.run('rm $IPD_TRIMMED_FASTA', shell = True)

  # check status
  printStatus('Workflow complete!')

"""## Generic utility functions"""

from datetime import datetime
import logging
import os

# import logger
log = logging.getLogger(__name__)

def printStatus(status):
    '''print timestamped status update'''
    print('--[' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '] ' + status + '--')
    log.info(status)
    
def createOutputFolder(cwd):
    '''create timestamped output folder at specified location'''
    
    # fetch current time
    CURRENT_TIME = datetime.now().strftime("%Y%m%d%H%M%S")

    # path to output folder
    OUTPUT_FOLDER = cwd + '/' + CURRENT_TIME

    # create folder if it doesn't already exist
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    # print output folder name
    printStatus('Output folder: ' + OUTPUT_FOLDER)
    
    return OUTPUT_FOLDER

def removeSpecialCharacters(in_str, special_characters='*|: ', replace_character='_'):
    '''remove specified special characters from input str'''
    
    out_str = in_str.translate ({ord(c): replace_character for c in special_characters})
    
    return out_str

"""## Trim and deduplicate rhesus IPD MHC alleles to miSeq exemplar length

The resulting deduplicated FASTA file can be used as a genotyping target for miSeq amplicon sequences.
"""

# run workflow
createMiseqTrimmedFasta(in_gbk, exemplar)

"""## Trim and deduplicate IPD MHC alleles"""


