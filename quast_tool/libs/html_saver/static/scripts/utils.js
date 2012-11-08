
function isInt(num) {
    return num % 1 === 0;
}

function isFloat(num) {
    return !isInt(num);
}

function toPrettyString(num, unit) {
    if (typeof num === 'number') {
        if (num <= 9999) {
            return num.toString() + (unit ? '<span class="rhs">&nbsp;</span>' + unit : '');
//            if (isFloat(num)) {
//                if (num <= 9) {
//                    return num.toFixed(3);
//                } else {
//                    return num.toFixed(2);
//                }
//            } else {
//                return num.toFixed(0);
//            }
        } else {
            return num.toFixed(0).replace(/(\d)(?=(\d\d\d)+(?!\d))/g,'$1<span class="hs"></span>') +
                (unit ? '<span class="rhs">&nbsp;</span>' + unit : '');
        }
    } else {
        return num;
    }
}

function ordinalNumberToPrettyString(num, unit) {
    var numStr = num.toString();
    var lastDigit = numStr[numStr.length-1];
    var beforeLastDigit = numStr[numStr.length-2];

    var res = toPrettyString(num);

    if (lastDigit == '1' && beforeLastDigit != '1') {
        res += "st";
    } else if (lastDigit == '2' && beforeLastDigit != '1') {
        res += "nd";
    } else if (lastDigit == '3' && beforeLastDigit != '1') {
        res += "rd";
    } else {
        res += 'th';
    }

    res += (unit ? '<span class="rhs">&nbsp;</span>' + unit : '');

    return res;
}

function getMaxDecimalTick(maxY) {
    var maxYTick = maxY;
    if (maxY <= 100000000000) {
        maxYTick = Math.ceil((maxY+1)/10000000000)*10000000000;
    } if (maxY <= 10000000000) {
        maxYTick = Math.ceil((maxY+1)/1000000000)*1000000000;
    } if (maxY <= 1000000000) {
        maxYTick = Math.ceil((maxY+1)/100000000)*100000000;
    } if (maxY <= 100000000) {
        maxYTick = Math.ceil((maxY+1)/10000000)*10000000;
    } if (maxY <= 10000000) {
        maxYTick = Math.ceil((maxY+1)/1000000)*1000000;
    } if (maxY <= 1000000) {
        maxYTick = Math.ceil((maxY+1)/100000)*100000;
    } if (maxY <= 100000) {
        maxYTick = Math.ceil((maxY+1)/10000)*10000;
    } if (maxY <= 10000) {
        maxYTick = Math.ceil((maxY+1)/1000)*1000;
    } if (maxY <= 1000) {
        maxYTick = Math.ceil((maxY+1)/100)*100.
    } if (maxY <= 100) {
        maxYTick = Math.ceil((maxY+1)/10)*10.
    }
    return maxYTick;
}

function getBpTickFormatter(maxY) {
    return function(val, axis) {
        var res;

        if (val == 0) {
            res = 0;

        } else if (val >= 1000000) {
            res = val / 1000000;

            if (val > maxY + 1 || val + axis.tickSize >= 1000000000) {
                res = toPrettyString(res, 'Mbp');
            } else {
                res = toPrettyString(res);
            }
        } else if (val >= 1000) {
            res = val / 1000;

            if (val > maxY + 1 || val + axis.tickSize >= 1000000) {
                res = toPrettyString(res, 'kbp');
            } else {
                res = toPrettyString(res);
            }
        } else if (val >= 1) {
            res = val;

            if (val > maxY + 1 || val + axis.tickSize >= 1000) {
                res = toPrettyString(res, 'bp');
            } else {
                res = toPrettyString(res);
            }
        }
        return '<span style="word-spacing: -1px;">' + res + '</span>';
    }
}

//
//function getWindowsTickFormatter(maxY) {
//    return function(val, axis) {
//        var res;
//
//        if (val == 0) {
//            res = 0;
//
//        } else if (val >= 1000000) {
//            res = val / 1000000;
//            res = myToFixed(res);
//
//            if (val > maxY + 1 || val + axis.tickSize >= 1000000000) {
//                res = res + ' windowes Mbp';
//            }
//        } else if (val >= 1000) {
//            res = val / 1000;
//            res = myToFixed(res);
//
//            if (val > maxY + 1 || val + axis.tickSize >= 1000000) {
//                res = res + ' kbp';
//            }
//        } else if (val >= 1) {
//            res = myToFixed(val);
//
//            if (val > maxY + 1 || val + axis.tickSize >= 1000) {
//                res = res + ' bp';
//            }
//        }
//        return '<span style="word-spacing: -1px;">' + res + '</span>';
//    }
//}

function getBpLogTickFormatter(maxY) {
    return getBpTickFormatter(maxY);
}

function getContigNumberTickFormatter(maxX) {
    return function (val, axis) {
        if (typeof axis.tickSize == 'number' && val > maxX - axis.tickSize) {
            return "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + ordinalNumberToPrettyString(val, 'contig');
        } else {
            return val;
        }
    }
}

function addTooltipIfDefinitionExists(glossary, string, dictKey) {
    if (!dictKey) {
        dictKey = string;
    }
    if (glossary.hasOwnProperty(dictKey)) {
        return '<a class="tooltip-link" href="#" rel="tooltip" title="' +
            dictKey + ' ' + glossary[dictKey] + '">' + string + '</a>';
    } else {
        return string;
    }
}

var tipElementExists = false;
function showTip(pageX, pageY, offset, plotWidth, plotHeight,
                 series, centralSeriesIndex, xIndex, xStr, position) {
    const LINE_HEIGHT = 16; // pixels

    position = ((position != null) ? position : 'bottom right');
//    pageY -= LINE_HEIGHT * (centralSeriesIndex + 1.5);

    if (!tipElementExists) {
        $('<div id="plot_tip" class="white_stroked"></div>').appendTo('body');

        $('<div id="plot_tip_vertical_rule"></div>').css({
            height: plotHeight,
        }).appendTo('body');

        $('<div id="plot_tip_horizontal_rule"></div>').css({
            width: plotWidth,
        }).appendTo('body');

        tipElementExists = true;
    }

    $('#plot_tip').html('').css({
        top: pageY + 5,
        left: pageX + 10,
    }).show();

    $('#plot_tip_vertical_rule').html('').css({
        top: offset.top,
        left: pageX,
    }).show();

    $('#plot_tip_horizontal_rule').html('').css({
        top: pageY,
        left: offset.left,
    }).show();

    $('<div>' + xStr + '</div>').css({
        height: LINE_HEIGHT,
    }).appendTo('#plot_tip');

    var sortedYsAndColors = [];
    for (var i = 0; i < series.length; i++) {
        sortedYsAndColors.push({
            y: (series[i].data[xIndex] || series[i].data[series[i].data.length - 1])[1],
            color: series[i].color,
            label: (series[i].isReference ? 'Reference' : series[i].label),
            isCurrent: i == centralSeriesIndex,
        });
    }
    sortedYsAndColors.sort(function(a, b) { return a.y < b.y;});

    for (i = 0; i < sortedYsAndColors.length; i++) {
        var item =sortedYsAndColors[i];

        $('<div id="tip_line' + i + '">' + toPrettyString(item.y)
            + ', <span style="color: ' + item.color + ';">' + item.label + '</span></div>').css({
            height: LINE_HEIGHT,
            "font-weight": item.isCurrent ? "bold" : "normal",
        }).appendTo('#plot_tip');
    }
}











