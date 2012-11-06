
var cumulative = {
    maxX: 0,
    maxY: 0,
    maxYTick: 0,
    plotsData: null,
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

    if (cumulative.plotsData == null || cumulative.draw == null || cumulative.redraw == null) {
        cumulative.plotsData = [];
        var plotsN = filenames.length;

        if (referenceLength) {
            cumulative.maxY = referenceLength;
        }

        for (var i = 0; i < plotsN; i++) {
            var lengths = listsOfLengths[i];
            var size = lengths.length;

            cumulative.plotsData[i] = {
                data: new Array(size+1),
                label: filenames[i],
                number: i,
                color: colors[i],
            };

            cumulative.plotsData[i].data[0] = [0, 0];

            var y = 0;
            for (var j = 0; j < size; j++) {
                y += lengths[j];
                cumulative.plotsData[i].data[j+1] = [j+1, y];
                if (y > cumulative.maxY) {
                    cumulative.maxY = y;
                }
            }

            if (size > cumulative.maxX) {
                cumulative.maxX = size;
            }
        }

        for (i = 0; i < plotsN; i++) {
            cumulative.plotsData[i].lines = {
                show: true,
                lineWidth: 1,
            }
        }

        for (i = 0; i < plotsN; i++) {
            cumulative.colors.push(cumulative.plotsData[i].color);
        }

        cumulative.maxYTick = getMaxDecimalTick(cumulative.maxY);

    //    In order to draw dots instead of lines
    //
    //    for (i = 0; i < plotsN; i++) {
    //        plotsData[i].points = {
    //            show: true,
    //            radius: 1,
    //            fill: 1,
    //            fillColor: false,
    //        }
    //    }

        if (referenceLength) {
            cumulative.plotsData.push({
                data: [[0, referenceLength], [cumulative.maxX, referenceLength]],
                label: 'Reference,&nbsp;' + toPrettyStringWithDimension(referenceLength, 'bp'),
                dashes: {
                    show: true,
                    lineWidth: 1,
                },
                yaxis: 1,
                number: cumulative.plotsData.length,
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

        cumulative.draw = function(plotsData, colors) {
            var plot = $.plot(placeholder, plotsData, {
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

            $(placeholder).bind("plothover", function(event, pos, item) {
               if (item) {
                   var x = item.datapoint[0];

                   $("#clickdata").text("")
               }
            });
        };

        cumulative.redraw = function() {
            var newPlotsData = [];
            var newColors = [];

            $('#legend-placeholder').find('input:checked').each(function() {
                var number = $(this).attr('name');
                if (number && cumulative.plotsData && cumulative.plotsData.length > 0) {
                    i = 0;
                    do {
                        var series = cumulative.plotsData[i];
                        i++;
                    } while (series.number != number && i <= cumulative.plotsData.length);
//                    if (i != cumulative.plotsData.length) {
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

            cumulative.draw(newPlotsData, newColors);
        };
    }

    $.each(cumulative.plotsData, function(i, series) {
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