#!/bin/sh
MACHINE=`uname`
PROC=`uname -p`
SCRIPT_PATH=$0
SCRIPT_PATH=`dirname $SCRIPT_PATH`
JAVA_PATH=$SCRIPT_PATH:.
MUMMER_PATH=$SCRIPT_PATH/../MUMmer3.23-osx

if [ `uname -s` = "Linux" ]; then
    MUMMER_PATH=$SCRIPT_PATH/../MUMmer3.23-linux;
fi

REF=$1
CONTIGS=$2
OUTPUT_FOLDER=$3
MIN_CONTIG=$4
MIN_CONTIG=`expr $MIN_CONTIG - 1`

create_tmp=0
if [ ! -e $OUTPUT_FOLDER ]; then
    create_tmp=1
    mkdir $OUTPUT_FOLDER
fi

CONTIG_FILE=$OUTPUT_FOLDER/$(basename $CONTIGS)

CUR_DIR=`pwd`
cd $SCRIPT_PATH
if [ ! -e GetFastaStats.class ]; then
    javac GetFastaStats.java
fi
if [ ! -e SizeFasta.class ]; then
    javac SizeFasta.java
fi
if [ ! -e Utils.class ]; then
    javac Utils.java
fi
if [ ! -e $MUMMER_PATH/nucmer ]; then
    cd $MUMMER_PATH
    make >/dev/null 2>/dev/null    
fi
cd $CUR_DIR

GENOMESIZE=`java -cp $JAVA_PATH SizeFasta $REF |awk '{SUM+=$NF; print SUM}'|tail -n 1`

echo "Contig Stats"
java -cp $JAVA_PATH GetFastaStats -o -min $MIN_CONTIG -genomeSize $GENOMESIZE $CONTIGS 2>/dev/null

$MUMMER_PATH/nucmer --maxmatch -p $CONTIG_FILE -l 30 -banded -D 5 $REF $CONTIGS
$MUMMER_PATH/delta-filter -o 95 -i 95 $CONTIG_FILE.delta > $CONTIG_FILE.fdelta
$MUMMER_PATH/dnadiff -d $CONTIG_FILE.fdelta -p $CONTIG_FILE

$SCRIPT_PATH/getMummerStats.sh $CONTIGS $SCRIPT_PATH $CONTIG_FILE $MIN_CONTIG
cat $CONTIG_FILE.1coords |awk '{print NR" "$5}' > $CONTIG_FILE.matches.lens

echo ""
echo "Corrected Contig Stats"
java -cp $JAVA_PATH:. GetFastaStats -o -min $MIN_CONTIG -genomeSize $GENOMESIZE $CONTIG_FILE.matches.lens 2> /dev/null

if [ $create_tmp -eq 1 ]; then
    rm -rf $OUTPUT_FOLDER
fi
