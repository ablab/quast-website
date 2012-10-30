
function filterAndSumGcInfo(GC_info, condition) {
    var contigs_lengths_cur_bin = [];
    for (var j = 0; j < GC_info.length; j++) {
        var GC = GC_info[j];
        var contig_length = GC[0];
        var GC_percent = GC[1];

        if (condition(GC_percent) == true) {
            contigs_lengths_cur_bin.push(contig_length);
        }
    }
    var val_bp = 0;
    for (var j = 0; j < contigs_lengths_cur_bin.length; j++) {
        val_bp += contigs_lengths_cur_bin[j];
    }
    return val_bp;
}


var gc = {
    maxY: 0,
    plot: null,
    plotsData: null,
    draw: null,
    redraw: null,
    minPow: 0,
    ticks: null,
    placeholder: null,
    legendPlaceholder: null,
    colors: null,
};


function drawInNormalScale(plotsData, colors) {
    if (plotsData == null || gc.maxY == null) {
        return;
    }
    gc.plot = $.plot(gc.placeholder, plotsData, {
            shadowSize: 0,
            colors: colors,
            legend: {
                container: $('useless-invisible-element-that-does-not-even-exist'),
            },
            grid: {
                borderWidth: 1,
            },
            yaxis: {
                min: 0,
//                max: gc.maxY,
                labelWidth: 120,
                reserveSpace: true,
                lineWidth: 0.5,
                color: '#000',
                tickFormatter: getBpTickFormatter(gc.maxY),
                minTickSize: 1,
            },
            xaxis: {
                min: 0,
                max: 100,
                lineWidth: 0.5,
                color: '#000',
                tickFormatter: function (val, axis) {
                    if (val == 100) {
                        return '&nbsp;100%'
                    } else {
                        return val;
                    }
                }
            },
            minTickSize: 1,
        }
    );
}


function drawInLogarithmicScale(plotsData, colors) {
    if (plotsData == null || gc.maxY == null || gc.minPow == null) {
        return;
    }
    gc.plot = $.plot(gc.placeholder, plotsData, {
            shadowSize: 0,
            colors: colors,
            legend: {
                container: $('useless-invisible-element-that-does-not-even-exist'),
            },
            grid: {
                borderWidth: 1,
            },
            yaxis: {
                min: Math.pow(10, gc.minPow),
//                max: gc.maxY,
                labelWidth: 120,
                reserveSpace: true,
                lineWidth: 0.5,
                color: '#000',
                tickFormatter: getBpLogTickFormatter(gc.maxY),
                minTickSize: 1,
                ticks: gc.ticks,

                transform:  function(v) {
                    return Math.log(v + 0.0001)/*move away from zero*/ / Math.log(10);
                },
                inverseTransform: function(v) {
                    return Math.pow(v, 10);
                },
                tickDecimals: 3,
            },
            xaxis: {
                min: 0,
                max: 100,
                lineWidth: 0.5,
                color: '#000',
                tickFormatter: function (val, axis) {
                    if (val == 100) {
                        return '&nbsp;100%'
                    } else {
                        return val;
                    }
                }
            },
            minTickSize: 1,
        }
    );
}


function setLogScale() {
    $('#normal_scale_label').html(normal_scale_a);
    $('#log_scale_label').html(log_scale_span);
    gc.draw = drawInLogarithmicScale;
    gc.redraw();
}


function setNormalScale() {
    $('#normal_scale_label').html(normal_scale_span);
    $('#log_scale_label').html(log_scale_a);
    gc.draw = drawInNormalScale;
    gc.redraw();
}

var normal_scale_span =
    "<span class='selected-switch'>" +
        'Normal' +
        "</span>";
var normal_scale_a =
    "<a class='dotted-link' onClick='setNormalScale()'>" +
        'Normal' +
        "</a>";
var log_scale_span =
    "<span class='selected-switch'>" +
        'logarithmic' +
        "</span>";
var log_scale_a =
    "<a class='dotted-link' onClick='setLogScale()'>" +
        'logarithmic' +
        "</a>";


function drawGCPlot(name, colors, filenames, listsOfGCInfo, reflen,
                    plotPh, legendPh, glossary, scalePh) {
    $(scalePh).html(
        "<div id='change-scale' style='margin-right: 3px; visibility: hidden;'>" +
            "<span id='normal_scale_label'>" +
            normal_scale_span +
            "</span>&nbsp;/&nbsp;" +
            "<span id='log_scale_label'>" +
            log_scale_a +
            "</span> scale" +
        "</div>"
    );

    if (gc.plotsData == null || gc.draw == null || gc.redraw == null) {
        gc.legendPlaceholder = legendPh;
        gc.placeholder = plotPh;
        gc.colors = colors;

        var bin_size = 1.0;
        var plotsN = filenames.length;
        gc.plotsData = new Array(plotsN);

        gc.maxY = 0;
        var minY = Number.MAX_VALUE;

        function updateMinY(y) {
            if (y < minY && y != 0) {
                minY = y;
            }
        }
        function updateMaxY(y) {
            if (y > gc.maxY) {
                gc.maxY = y;
            }
        }

        for (var i = 0; i < plotsN; i++) {
            gc.plotsData[i] = {
                data: [],
                label: filenames[i],
                number: i,
                color: colors[i],
            };

            var GC_info = listsOfGCInfo[i];
            var cur_bin = 0.0;

            var x = cur_bin;
            var y = filterAndSumGcInfo(GC_info, function(GC_percent) {
                return GC_percent == cur_bin;
            });
            gc.plotsData[i].data.push([x, y]);

            updateMinY(y);
            updateMaxY(y);

            while (cur_bin < 100.0 - bin_size) {
                cur_bin += bin_size;

                x = cur_bin;
                y = filterAndSumGcInfo(GC_info, function(GC_percent) {
                    return GC_percent > (cur_bin - bin_size) && GC_percent <= cur_bin;
                });
                gc.plotsData[i].data.push([x, y]);

                updateMinY(y);
                updateMaxY(y);
            }

            x = 100.0;
            y = filterAndSumGcInfo(GC_info, function(GC_percent) {
                return GC_percent > cur_bin && GC_percent <= 100.0;
            });

            gc.plotsData[i].data.push([x, y]);

            updateMinY(y);
            updateMaxY(y);
        }

        for (i = 0; i < plotsN; i++) {
            gc.plotsData[i].lines = {
                show: true,
                lineWidth: 1,
            }
        }

        // Calculate the minimum possible non-zero Y to clip useless bottoms
        // of logarithmic plots.
        var maxYTick = getMaxDecimalTick(gc.maxY);
        gc.minPow = Math.round(Math.log(minY) / Math.log(10));
        gc.ticks = [];
        for (var pow = gc.minPow; Math.pow(10, pow) < maxYTick; pow++) {
            gc.ticks.push(Math.pow(10, pow));
        }
        gc.ticks.push(Math.pow(10, pow));

        gc.draw = drawInNormalScale;

        gc.redraw = function() {
            var newPlotsData = [];
            var newColors = [];

            $('#legend-placeholder').find('input:checked').each(function() {
                var number = $(this).attr('name');
                if (number && gc.plotsData && gc.plotsData.length > 0) {
                    i = 0;
                    do {
                        var series = gc.plotsData[i];
                        i++;
                    } while (series.number != number && i <= gc.plotsData.length);
//                    if (i != gc.plotsData.length) {
                    newPlotsData.push(series);
                    newColors.push(series.color);
//                    }
                }
            });

            if (newPlotsData.length == 0) {
                newPlotsData.push({
                    data: [],
                });
                newColors.push('#FFF');
            }

            gc.draw(newPlotsData, newColors);
        };

        $.each(gc.plotsData, function(i, series) {
            $('#legend-placeholder').find('#label_' + series.number + '_id').click(gc.redraw);
        });

        gc.redraw();

        $('#change-scale').css('visibility', 'visible');
    }
}
