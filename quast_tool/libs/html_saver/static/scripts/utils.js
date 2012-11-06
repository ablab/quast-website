
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
//
//function toPrettyStringWithUnit(num, unit) {
//    if (num <= 9999) {
//        return num.toString() + '<span class="rhs">&nbsp;</span>' + unit;
//    } else {
//        return num.toString().replace(/(\d)(?=(\d\d\d)+(?!\d))/g,'$1<span class="hs"></span>')
//            + '<span class="rhs">&nbsp;</span>' + unit;
//    }
//}
//
//function twoDigitsAfterDot(num) {
//    if (typeof num === 'number') {
//        if (isFloat(num)) {
//            return num.toFixed(2);
//        } else {
//            return num;
//        }
//    } else {
//        return num;
//    }
//}

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
            var valStr = val.toString();
            var lastDigit = valStr[valStr.length-1];
            var beforeLastDigit = valStr[valStr.length-2];

            var res = val + "th";

            if (lastDigit == '1' && beforeLastDigit != '1') {
                res = val + "st";
            } else if (lastDigit == '2' && beforeLastDigit != '1') {
                res = val + "nd";
            } else if (lastDigit == '3' && beforeLastDigit != '1') {
                res = val + "rd";
            }
            return "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + res + "&nbsp;contig";
        }
        return val;
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
