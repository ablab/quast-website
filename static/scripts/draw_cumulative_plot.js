
var cumulative = {
    maxX: 0,
    maxY: 0,
    maxYTick: 0,
    series: null,
    draw: null,
    redraw: null,
    colors: [],
};

function drawCumulativePlot(name, colors, filenames, listsOfLengths, referenceLength,
                            placeholder, legendPlaceholder, glossary) {
//    var title = 'Cumulative length';
//    div.html(
//        "<span class='plot-header'>" + addTooltipIfDefinitionExists(glossary, title) + "</span>" +
//        "<div class='plot-placeholder' id='cumulative-plot-placeholder'></div>"
//    );

//    var divName = 'cumulative-plot-placeholder';
//    div.html(
//        "<span class='dotted-link' id='>" + title + "'</span>" +
//        "<div class='plot-placeholder' id='" + divName + "></div>"
//    );

//    div.find('.dotted-link').click(showHidePlot('#' + divName));

//    var colors = ["#FF5900", "#008FFF", "#168A16", "#782400", "#FFDD00", "#FF0080", "#7AE01B", "#7C00FF", "#E01B6A"];

    if (cumulative.series == null || cumulative.draw == null || cumulative.redraw == null) {
        cumulative.series = [];
        var plotsN = filenames.length;

        if (referenceLength) {
            cumulative.maxY = referenceLength;
        }

        cumulative.colors = colors;

        for (var i = 0; i < plotsN; i++) {
            var lengths = listsOfLengths[i];
            var size = lengths.length;

            cumulative.series[i] = {
                data: new Array(size+1),
                label: filenames[i],
                number: i,
                color: colors[i],
            };

            cumulative.series[i].data[0] = [0, 0];

            var y = 0;
            for (var j = 0; j < size; j++) {
                y += lengths[j];
                cumulative.series[i].data[j+1] = [j+1, y];
                if (y > cumulative.maxY) {
                    cumulative.maxY = y;
                }
            }

            if (size > cumulative.maxX) {
                cumulative.maxX = size;
            }
        }

        var lineColors = [];

        for (i = 0; i < colors.length; i++) {
            lineColors.push(changeColor(colors[i], 0.9, false));
        }

        for (i = 0; i < plotsN; i++) {
            cumulative.series[i].lines = {
                show: true,
                lineWidth: 1,
//                color: lineColors[i],
            };
      //    In order to draw dots instead of lines
            cumulative.series[i].points = {
                show: false,
                radius: 1,
                fill: 1,
                fillColor: false,
            };
        }

        for (i = 0; i < plotsN; i++) {
            cumulative.colors.push(cumulative.series[i].color);
        }

        cumulative.maxYTick = getMaxDecimalTick(cumulative.maxY);

        for (i = 0; i < plotsN; i++) {
        }

        if (referenceLength) {
            cumulative.series.push({
                data: [[0, referenceLength], [cumulative.maxX, referenceLength]],
                label: 'Reference,&nbsp;' + toPrettyString(referenceLength, 'bp'),
                isReference: true,
                dashes: {
                    show: true,
                    lineWidth: 1,
                },
                yaxis: 1,
                number: cumulative.series.length,
                color: '#000000',
            });

            cumulative.colors.push('#000000');

    //        plotsData = [({
    //            data: [[0, referenceLength], [maxX, referenceLength]],
    //            dashes: {
    //                show: true,
    //                lineWidth: 1,
    //            },
    //            number: plotsData.length,
    //        })].concat(plotsData);
        }


//    if (referenceLength) {
//        yaxes.push({
//            ticks: [referenceLength],
//            min: 0,
//            max: maxYTick,
//            position: 'right',
////            labelWidth: 50,
//            reserveSpace: true,
//            tickFormatter: function (val, axis) {
//                return '<div style="">' + toPrettyStringWithDimension(referenceLength, 'bp') +
//                    ' <span style="margin-left: -0.2em;">(reference)</span></div>';
//            },
//            minTickSize: 1,
//        });
//    }
        var yaxis = {
            min: 0,
            max: cumulative.maxYTick,
            labelWidth: 120,
            reserveSpace: true,
            lineWidth: 0.5,
            color: '#000000',
            tickFormatter: getBpTickFormatter(cumulative.maxY),
            minTickSize: 1,
        };
        var yaxes = [yaxis];

        cumulative.draw = function(series, colors) {
            var plot = $.plot(placeholder, series, {
                shadowSize: 0,
                colors: cumulative.colors,
                legend: {
                    container: $('useless-invisible-element-that-does-not-even-exist'),
                },
    //            legend: {
    //                container: legendPlaceholder,
    //                position: 'se',
    //                labelBoxBorderColor: '#FFF',
    //                labelFormatter: labelFormatter,
    //            },
                grid: {
                    borderWidth: 1,
                    hoverable: true,
                    autoHighlight: false,
                    mouseActiveRadius: 1000,
                },
                yaxes: yaxes,
                xaxis: {
                    min: 0,
                    max: cumulative.maxX,
                    lineWidth: 0.5,
                    color: '#000',
                    tickFormatter: getContigNumberTickFormatter(cumulative.maxX),
                    minTickSize: 1,
                },
            });

            var prevPoint = null;
            $(placeholder).bind("plothover", function(event, pos, item) {
                if (item) {
                    if (prevPoint != item.dataIndex) {
                        prevPoint = item.dataIndex;

                        var x = item.datapoint[0];

                        showTip(item.pageX, item.pageY, plot.offset(),
                                plot.width(), plot.height(),
                                series, item.seriesIndex, item.dataIndex,
                                ordinalNumberToPrettyString(x, 'contig') + ':',
                                'bottom right');
                    }
                } else {
                    $('#plot_tip').hide();
                    $('#plot_tip_vertical_rule').hide();
                    $('#plot_tip_horizontal_rule').hide();
                    prevPoint = null;
                }
            });
        };

        cumulative.redraw = function() {
            var newSeries = [];
            var newColors = [];

            $('#legend-placeholder').find('input:checked').each(function() {
                var number = $(this).attr('name');
                if (number && cumulative.series && cumulative.series.length > 0) {
                    i = 0;
                    do {
                        var series = cumulative.series[i];
                        i++;
                    } while (series.number != number && i <= cumulative.series.length);

//                    if (i != cumulative.plotsData.length) {
                    newSeries.push(series);
                    newColors.push(series.color);
//                    }
                }
            });

            if (newSeries.length == 0) {
                newSeries.push({
                    data: [],
                });
                newColors.push('#FFF');
            }

            cumulative.draw(newSeries, newColors);
        };
    }

    $.each(cumulative.series, function(i, series) {
        $('#legend-placeholder').find('#label_' + series.number + '_id').click(cumulative.redraw);
    });

    cumulative.redraw();

    $('#contigs_are_ordered').show();

//    placeholder.resize(function () {
//        alert("Placeholder is now "
//            + $(this).width() + "x" + $(this).height()
//            + " pixels");
//    });

    // var o = plot.pointOffset({ x: 0, y: 0});
    // $('#cumulative-plot-placeholder').append(
    //     '<div style="position:absolute;left:' + (o.left + 400) + 'px;top:' + (o.top - 400) + 'px;color:#666;font-size:smaller">Actual measurements</div>'
    // );
}