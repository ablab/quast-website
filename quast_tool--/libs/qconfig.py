############################################################################
# Copyright (c) 2011-2013 Saint-Petersburg Academic University
# All Rights Reserved
# See file LICENSE for details.
############################################################################

import datetime
import os

LIBS_LOCATION = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))

# support of large genomes
MAX_REFERENCE_LENGTH = 536870908  # Nucmer's max length of a reference file
splitted_ref = []

# available options
long_options = "output-dir= save-json-to= genes= operons= reference= contig-thresholds= min-contig= "\
               "gene-thresholds= save-json gage eukaryote no-plots no-html help debug "\
               "allow-ambiguity scaffolds threads= mincluster= est-ref-size= use-all-alignments gene-finding strict-NA".split()
short_options = "o:G:O:R:t:M:S:J:jehdsaT:c:ufn"

# default values for options
contig_thresholds = "0,1000"
min_contig = 500
genes_lengths = "0,300,1500,3000"
reference = ''
genes = ''
operons = ''
with_gage = False
prokaryote = True # former cyclic
gene_finding = False
allow_ambiguity = False
use_all_alignments = False
max_threads = None
mincluster = 65
estimated_reference_size = None
strict_NA = False
scaffolds = False
draw_plots = True
html_report = True
save_json = False
debug = False


default_results_root_dirname = "quast_results"
output_dirname = "results_" + datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
make_latest_symlink = True

default_json_dirname = "json"

# names of reports, log, etc.
logfile = "quast.log"
corrected_dirname = "corrected_input"
plots_filename = "plots.pdf"
report_prefix="report"
transposed_report_prefix="transposed_report"
gage_report_prefix="gage_"
html_aux_dir="report_html_aux"

# other settings (mostly constants). Can't be changed by command-line options

# for separating indels into short and long ones
SHORT_INDEL_THRESHOLD = 5

# for parallelization
DEFAULT_MAX_THREADS = 4  # this value is used if QUAST fails to determine number of CPUs
assemblies_num = 1

# genome analyzer
min_gap_size = 50 # for calculating number or gaps in genome coverage
min_gene_overlap = 100 # to partial genes/operons finding

# basic_stats
GC_bin_size = 1.0

# plotter and maybe other modules in the future
legend_names = None

# for scaffolds
list_of_broken_scaffolds = []
Ns_break_threshold = 10