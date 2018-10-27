#!/bin/bash

# for FILE in *; do
#     gnuplot <<- EOF
#         set xlabel "Label"
#         set ylabel "Label2"
#         set title "Graph title"
#         set term png
        # set output "${1}.png"
#         plot "${FILE}" using 1:2:3:4 with errorbars
# EOF
# # done

# for FILE in histosDir/gpltFilesFrozen/*
# do

plotType=""

function findOptVar {
    opt2Look="$1"
    shift

    while [[ $# -gt 0 ]]
    do
        key="$1"
        if [ "$key" = "$opt2Look" ]
        then
            echo "true"
            return
        fi
        shift
    done
    echo "false"
}

function getOptVar {
    opt2Look="$1"
    shift
    optVal=""

    while [[ $# -gt 0 ]]
    do
        key="$1"
        if [ "$key" = "$opt2Look" ]
        then
            optVal="$2"
            echo "$optVal"
            return
        fi
        shift
    done
    echo ""
}

function checkIfDir {
    dName=$1
    if [ ! -d "$dName" ]
    then
        echo "error: $dName is not a directory" >&2
        exit 666
    fi
}

function checkIfRegFile {
    fName=$1
    if [ ! -f "$fName" ]
    then
        echo "error: $fName is not a regular file" >&2
        exit 667
    fi
}

function handleArgs {
    if [ $# -eq 0 ]
    then
        echo "usage: $0 (options) <files> [extraOptions]"
	echo ""
	echo "Fits straight lines to data prints out their parameters."
	echo ""
	echo "options:"
	echo -e "\t-f:\texpects a single txt file as argument."
	echo -e "\t-d:\texpects directory (containing txt files) as an argument."
	echo ""
	echo "extraOptions:"
	echo -e "\t--pdfDir:\texpects a directory to store the pdf plots. Exclusive with --pngDir.\n"
	echo -e "\t--pngDir:\texpects a directory to store the png plots. Exclusive with --pdfDir.\n"
	echo -e "\t-p:\t\twill make a plot and display it inmediately (can't be used with --p*Dir)."
	echo ""
    fi

    plotBool=$(findOptVar '-p' $@)
    opt4getTxt=""
    [ "$plotBool" = "true" ] &&\
        opt4getTxt="-p"

    plotDir=""
    outPdfBool=$(findOptVar '--pdfDir' $@)
    [ "$outPdfBool" = "true" ] &&\
        plotDir=$(getOptVar '--pdfDir' $@) &&\
        checkIfDir $plotDir &&\
	plotDir="$(truncate_leadingSlash $plotDir)/" &&\
        opt4getTxt="-p" &&\
	plotType="pdf"

    outPngBool=$(findOptVar '--pngDir' $@)
    [ "$outPdfBool" = "true" ] && [ "$outPngBool" = "true" ] &&\
	echo "error: inconsistent options, use either png or pdf" && exit 666
    
    [ "$outPngBool" = "true" ] &&\
        plotDir=$(getOptVar '--pngDir' $@) &&\
        checkIfDir $plotDir &&\
	plotDir="$(truncate_leadingSlash $plotDir)/" &&\
        opt4getTxt="-p" &&\
	plotType="png"


    dirBool=$(findOptVar '-d' $@)
    if [ "$dirBool" = "true" ]
    then
        optVar=$(getOptVar '-d' $@)
	optVar=$(truncate_leadingSlash $optVar)
        checkIfDir $optVar
        echo -e "#filename\ta\ta_err\taErrPer\tb\tb_err\tbErrPerr"
        for file in "$optVar/"*.txt
        do
            parVar=$(getTxtFilePar $opt4getTxt $file\
                                   $plotType $plotDir)
            name=$(basename $file)
            echo -e "$name\t$parVar"
        done
        exit 0
    fi
    fileBool=$(findOptVar '-f' $@)
    if [ "$fileBool" = "true" ]
    then
        fileVar=$(getOptVar '-f' $@)
        checkIfRegFile $fileVar
        echo -e "#a\ta_err\taErrPer\tb\tb_err\tbErrPerr"
        getTxtFilePar $opt4getTxt $fileVar $plotType $plotDir
        exit 0
    fi
}

function truncate_leadingSlash()
{
 local string="$1"
 local len=${#string}
 while [[ "${string:$(expr $len - 1)}" == "/" ]]
 do
  string=${string:0:$(expr $len - 1)}
  len=${#string}
 done
 echo $string
}

function getTxtFilePar {
    specialVar=""
    mySetTerm=""
    setOutFN=""
    if [ "$1" = "-p" ]
    then
        shift
        specialVar="print \"Happiness is here\""
        specialVar="plot \"${1}\", f(x)"
        myVarName=""
        if [ "${2}" = "pdf" ]
        then
            myFileName="${3}$(basename ${1} .txt).pdf"
	    mySetTerm="set terminal pdf"
            setOutFN="set output '${myFileName}'"
	elif [ "${2}" = "png" ]
	then
	    myFileName="${3}$(basename ${1} .txt).png"
	    mySetTerm="set terminal png"
            setOutFN="set output '${myFileName}'"
        fi
    fi

    gnuplot --persist  <<- EOF
        set print "-"
        set xlabel "CsI [chan]"
        set ylabel "Energy sum [MeV]"
        set title "Graph title"
        a=10
        b=3
        f(x)=a*x+b
        set fit quiet # too much output
        fit f(x) "${1}" via a,b
        # plot "${1}" w lp, f(x)
        # print  a,b,a_err,b_err
        aErrP=100*(a_err/a)
        bErrP=100*(b_err/b)
        myStrForm = sprintf("%0.4f\t%0.4f\t%0.4f\t%0.4f\t%0.4f\t%0.4f", a,a_err,aErrP,b,b_err,bErrP)
        print myStrForm

        set label sprintf("a = %3.5g",a) at graph 0.5,0.7 right
        # bfit = gprintf("b = %s*10^%S",b)
        bfit = gprintf("b = %3.5g",b)
        set label bfit  at graph 0.5,0.6 right

        ${mySetTerm} # only if pdf or png option was used
        ${setOutFN}
        ${specialVar} # the plotting but only if the option was used
        # print FIT_STDFIT
        # printf "%0.3f" % a
EOF
}

# done

# aVar=$(plotTxtFile $1)
# echo "aVar=$aVar"

# plotTxtFile $1

handleArgs $@
