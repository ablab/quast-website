<a name="top"></a>
## About

[Short intro](#intro)  
[Further reading](#further)  
[How to cite](#citations)  
[Brief project history](#history)  
[Authors](#authors)  
[Funding](#funding)  
[License and Terms of use](#license)

<a name="intro"></a>
### Short intro

**QUAST evaluates genome assemblies by computing various metrics, including**

* N50, length for which the collection of all contigs of that length or longer covers at least 50% of assembly length
* NG50, where length of the reference genome is being covered
* NA50 and NGA50, where aligned blocks instead of contigs are taken
* misassemblies, misassembled and unaligned contigs or contigs bases
* genes and operons covered

**.. and builds convenient plots for different metrics**

* cumulative contigs length
* all kinds of N-metrics
* genes and operons covered
* GC content

**QUAST can work with and without a reference genome**, though the output is considerably smaller in the latter case. The pipeline relies on multiple open-source tools, including [minimap2](https://github.com/lh3/minimap2) and [GlimmerHMM](https://ccb.jhu.edu/software/glimmerhmm/).  

<a name="further"></a>
### Further reading

More details are on the [project page](http://cab.spbu.ru/software/quast) and in [Gurevich et al., Bioinformatics, 2013](http://dx.doi.org/10.1093/bioinformatics/btt086).  
You may also want to check out the [Help](help.md) page with a step-by-step tutorial on using this website and interpreting its output.  
Thorough metric descriptions are available in the [online manual](http://cab.cc.spbu.ru/quast/manual.html#sec3.1). A nice illustrated explanation of N50 and similar metrics by Elin Videvall (with assistance from the QUAST team) is [here](https://www.molecularecologist.com/2017/03/29/whats-n50/).  
Finally, we invite you to read all QUAST publications listed [below](#citations) to understand the algorithms behind the tool and its applicability to various domains.

Don't hesitate to [contact us](contact.md) if you still have any questions!


<a name="citations"></a>
### How to cite
If you have found QUAST useful in your research, please cite:

**Versatile genome assembly evaluation with QUAST-LG**  
Alla Mikheenko, Andrey Prjibelski, Vladislav Saveliev, Dmitry Antipov, Alexey Gurevich  
*Bioinformatics* (2018) DOI: [10.1093/bioinformatics/bty266](https://doi.org/10.1093/bioinformatics/bty266)

**Icarus: visualizer for de novo assembly evaluation**  
Alla Mikheenko, Gleb Valin, Andrey Prjibelski, Vladislav Saveliev, Alexey Gurevich  
*Bioinformatics* (2016) DOI: [10.1093/bioinformatics/btw379](https://doi.org/10.1093/bioinformatics/btw379)

**MetaQUAST: evaluation of metagenome assemblies**  
Alla Mikheenko, Vladislav Saveliev, Alexey Gurevich  
*Bioinformatics* (2016) DOI: [10.1093/bioinformatics/btv697](https://doi.org/10.1093/bioinformatics/btv697)

**QUAST: quality assessment tool for genome assemblies**  
Alexey Gurevich, Vladislav Saveliev, Nikolay Vyahhi and Glenn Tesler  
*Bioinformatics* (2013) DOI: [10.1093/bioinformatics/btt086](https://doi.org/10.1093/bioinformatics/btt086)

<a name="history"></a>
### Brief project history

**2011, July** — project start  
**2012, August 14** — first public release at [SourceForge](https://sourceforge.net/projects/quast/files/) (QUAST v.1.0.0)  
**2012, September 27** — the web server first launch (at http://quast.bioinf.spbau.ru/, shut down in January 2020)  
**2013, February 19** — the first [QUAST publication](http://dx.doi.org/10.1093/bioinformatics/btt086) was out in *Bioinformatics*  
**2013, April 15** — Prof. Steven Salzberg [recommended QUAST](https://facultyopinions.com/prime/717981369?bd=1&ui=24116) at Faculty Opinions (former F1000)  
**2015, July 13** — the [QUAST repository](https://github.com/ablab/quast) was opened for public access on GitHub, the tool became fully open sourced  
**2018, November 2** — the total number of QUAST downloads exceeded 100,000 ([bioconda](https://anaconda.org/bioconda/quast) & [SourceForge](https://sourceforge.net/projects/quast/files/))  
**2020, April 4** — the web server relauched at its [current location](http://cab.cc.spbu.ru/quast/)  
**2021, August 31** — [CZI acknowledged](https://chanzuckerberg.com/newsroom/czi-awards-16-million-for-foundational-open-source-software-tools-essential-to-biomedicine/) QUAST as an essential software tool for biomedicine and supported with a grant (jointly with [SPAdes](https://cab.spbu.ru/software/spades))

<a name="authors"></a>
### Authors 

**Core developers** (in alphabetical order):  
Alexey Gurevich (since 2011)  
Alla Mikheenko (since 2015)  
Vlad Saveliev (2012-2017) 

**Also contributed** (in alphabetical order):  
Dmitry Antipov  
Aleksey Komissarov  
Andrey Prjibelski  
Glenn Tesler  
Gleb Valin  
Irina Vasilinetc  
Nikolay Vyahhi  
.. and dozens of QUAST users who provided their feedback


**Logo design** by Elena Strelnikova

<a name="funding"></a>
### Funding

Over the years, the QUAST development was supported by many funding agencies/sources:  

* The [mega-grant program](https://p220.ru/en/) of the Government of the Russian Federation
* [Russian Science Foundation](https://rscf.ru/en/)
* [St. Petersburg State University](https://english.spbu.ru/science-4)
* [The EOSS program](https://chanzuckerberg.com/eoss/) of The Chan Zuckerberg Initiative

The server is running using computational resources provided by the [Computer Center of Research park](http://www.cc.spbu.ru/en) of St. Petersburg State University.

<a name="license"></a>
### License and Terms of use

QUAST is licensed under GPL v2 and it is free to use for everybody; there is no login requirement for the web server. However, some of build-in third-party tools are not under GPL v2. See [LICENSE](http://cab.cc.spbu.ru/quast/LICENSE.txt) for details. In particular, the [GeneMark](http://opal.biology.gatech.edu/GeneMark/) gene prediction software has a stricter license, so it is not included in the web server pipeline, but can be used with the command-line version if you are eligible. 

**Liability**: the QUAST webserver is developed and maintained in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 

[To the top](#top)