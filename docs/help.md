<a name="top"></a>
## Help

[Submitting your data](#submit)  
[Interpreting the output](#output)  
[Icarus browser basics](#icarus)  
[Browser compatibility](#compatibility)  
[WebQUAST FAQ](#faq)  

This page will guide you step-by-step from submitting your data to interpreting the results. This page also contains info on the [browser compatibility](#compatibility), so if something is not working correctly, please [let us know](contact.md) and consider changing your browser as a possible workaround.

If you are new to QUAST, you may want to check out the [About](about.md) page first.  
If you are an advanced QUAST user, you may want to consult the [online manual](http://cab.cc.spbu.ru/quast/manual.html) instead, e.g., detailed [quality metric descriptions](http://cab.cc.spbu.ru/quast/manual.html#sec3.1) or [general/command-line FAQ](http://cab.cc.spbu.ru/quast/manual.html#sec7). We also have a short [FAQ](#faq) specific to the web version of the tool.   
If you didn't find answers here or there, [ask us](contact.md)!

<a name="submit"></a>
### Submitting your data

1. QUAST expects assemblies in the [FASTA format](https://en.wikipedia.org/wiki/FASTA_format) (typically `.fasta/.fa` files), optionally compressed with gzip. You can upload your files via a file selection dialogue using the "Select files" button, or drag and drop them into the "drop files here" field. 

     ![Main view](img/quast_main_view.png)

2. You can parametrize your QUAST job, e.g., whether your sequences are scaffolds, whether you want to enable gene detection, and whether the genome is circular (typical for bacteria).

3. QUAST can work without a reference genome. However, if a model genome for an organism is available, QUAST would report many more exciting results. You can upload a reference genome through the "Genome" selection menu. A set of popular genomes are already pre-uploaded.

4. Press "Evaluate" to queue a QUAST job. Normally, it will be run immediately; however, it might take longer for a job to start in periods of high load. Before submitting, you can title your job using the "Caption" text field; otherwise, a current timestamp would be used as a default title.

5. Your submitted jobs will appear on the right side of the main page. Clicking on a title will send you to the job page, which will have a QUAST report once it's completed. You can add your email address for heavy jobs, and you will be notified when the jobs are completed.

<a name="output"></a>
### Interpreting the output

1. If a reference genome was provided, its basic characteristics will be shown on the top.

2. The main table summarizes all quality metrics for given assemblies. See the QUAST manual for [details on reported metrics](http://cab.cc.spbu.ru/quast/manual.html#sec3.1). The web page provides some convenient UI that allows you to:
	* Reorder columns using drag and drop.
	* Use the color scheme to range values from the worst (red) to the best (blue).
	* Point over a metric name for a tooltip with an explanation of this metric.

    ![Report view](img/quast_report_view.png)

3. More metrics are available by clicking on "Extended report".
4. Checkboxes on the right allow selecting assemblies displayed on the plots.
5. Users can switch between different plots by clicking on the tabs.
6. A standalone version of the report is available for download. In addition, a tarball contains Latex and tab-separated versions of the table suitable for parsing, along with plots in PDF.
7. You can browser the assembly alignments and contig sizes in the Icarus browser; see the example below and find more details in [Mikheenko et al, 2016](https://doi.org/10.1093/bioinformatics/btw379).

<a name="icarus"></a>
### Icarus browser basics

1. If a reference genome was provided, the default Icarus view is the Contig alignment viewer. Otherwise, the Contig size viewer would be opened. Use the "Main menu" button in the top-left corner to switch between the viewers or return to the QUAST report. Click on "Icarus" to return to the webserver homepage.

    ![Icarus view](img/quast_icarus.png)

2. Click on a contig/aligned block to get the detailed information on it in the right pane. 
3. The controls in the top panel allow moving and zooming and showing/hiding all types of detected misassemblies. The Legend on the right explains the color coding scheme.

<a name="compatibility"></a>
### Browser compatibility

**Note**: we recommend using **Chrome**; we tested this browser most. There are known issues with displaying contigs in Icarus viewers in Firefox; we are working on fixing it asap. 

| OS      | Version           | Chrome | Firefox | Edge | Safari |
| --------| ------------------|--------|---------|------|--------|
| Linux   | Ubuntu 20.04      | 96 | 94 (Icarus issues) | not tested | not tested |
| MacOS   | Big Sur 11.6.1    | 96 | 95 (Icarus issues) | not tested  | 15.2 |
| Windows | 10 	              | 95 | 94 (Icarus issues) | 96 | not tested |

<a name="faq"></a>
### WebQUAST FAQ  

This FAQ is primarily for WebQUAST; the answers to many common questions about the command-line utility and QUAST, in general, are [here](http://cab.cc.spbu.ru/quast/manual.html#sec7). Note that for any WebQUAST report, you can always get the full command-line QUAST output (the standalone report) by pressing the *Download report* button, see step 6 in the [Interpreting the output](#output) section. 

**Q1. How can find out which commands and parameters of the third-party tools (e.g., minimap2, BUSCO) WebQUAST used in my analysis?**  
The standalone report includes the detailed log file (`<downloaded_report>/full_output/quast.log`) listing all used commands.
 
**Q2. Is it possible to get the list of misassemblies for an assembly?**    
Yes! The list of misassemblies in the [GFF3 format](https://www.ensembl.org/info/website/upload/gff3.html) and the sequences of the misassembled contigs in the FASTA format are available in the standalone report. For an assembly labeled `<assembly_name>`, the corresponding files are `<assembly_name>.misassemblies.gff` and `<assembly_name>.mis_contigs.fa` in the `<downloaded_report>/full_output/contigs_reports/` folder. 

**Q3. Can I check whether misassemblies are co-located with specific genomic features, e.g., repeats or gene-dense regions?**  
This feature is not nicely implemented yet, but there is a workaround. You can upload any genome annotation, such as coordinates of repeated regions, as a *Genes* file corresponding to your reference genome (see step 3 in the [Submitting your data](#submit) section). The BEG, GFF, and plain text formats are supported, see more detail in the [online manual](http://cab.cc.spbu.ru/quast/manual.html#sec2.2). When the evaluation against this reference is complete, you might visually match misassemblies to the track with your annotations in the [Icarus browser](#icarus). You might also search for a specific feature by its name using the search field in the top right corner.


[To the top](#top)


