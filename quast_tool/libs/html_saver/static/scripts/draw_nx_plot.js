
var nx = {
    maxY: 0,
    maxYTick: 0,
    plotsData: null,
    draw: null,
    redraw: null,
    kind: null,
};

function drawNxPlot(name, colors, filenames, listsOfLengths, refLength,
                    div, legendPlaceholder, glossary) {

//    var titleHtml = title;
//    if (glossary.hasOwnProperty(title)) {
//        titleHtml = "<a class='tooltip-link' href='#' rel='tooltip' title='" + title + " "
//            + glossary[title] + "'>" + title + "</a>"
//    }

//    div.html(
//        "<span class='plot-header'>" + titleHtml + "</span>" +
//        "<div class='plot-placeholder' id='" + title + "-plot-placeholder'></div>"
//    );

    if (nx.kind != name) {
        nx = {
            maxY: 0,
            maxYTick: 0,
            plotsData: null,
            draw: null,
            redraw: null,
            kind: name,
        };
    }

    if (nx.plotsData == null || nx.draw == null || nx.redraw == null) {
        var plotsN = filenames.length;
        nx.plotsData = new Array(plotsN);

        for (var i = 0; i < plotsN; i++) {
            var lengths = listsOfLengths[i];

            var size = lengths.length;

            var sumLen = 0;
            for (var j = 0; j < lengths.length; j++) {
                sumLen += lengths[j];
            }
            if (refLength) {
                sumLen = refLength;
            }

            nx.plotsData[i] = {
                data: [],
                label: filenames[i],
                number: i,
                color: colors[i],
            };
            nx.plotsData[i].data.push([0.0, lengths[0]]);
            var currentLen = 0;
            var x = 0.0;

            for (var k = 0; k < size; k++) {
                currentLen += lengths[k];
                nx.plotsData[i].data.push([x, lengths[k]]);
                x = currentLen * 100.0 / sumLen;
                nx.plotsData[i].data.push([x, lengths[k]]);
            }

            if (nx.plotsData[i].data[0][1] > nx.maxY) {
                nx.maxY = nx.plotsData[i].data[0][1];
            }

            var lastPt = nx.plotsData[i].data[nx.plotsData[i].data.length-1];
            nx.plotsData[i].data.push([lastPt[0], 0]);
        }

        for (i = 0; i < plotsN; i++) {
            nx.plotsData[i].lines = {
                show: true,
                lineWidth: 1,
            }
        }

//    for (i = 0; i < plotsN; i++) {
//        plotsData[i].points = {
//            show: true,
//            radius: 1,
//            fill: 1,
//            fillColor: false,
//        }
//    }

        nx.draw = function(plotsData, colors) {
            var plot = $.plot(div, plotsData, {
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
//                        max: nx.maxY,
                        labelWidth: 120,
                        reserveSpace: true,
                        lineWidth: 0.5,
                        color: '#000',
                        tickFormatter: getBpTickFormatter(nx.maxY),
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
        };

        nx.redraw = function() {
            var newPlotsData = [];
            var newColors = [];

            $('#legend-placeholder').find('input:checked').each(function() {
                var number = $(this).attr('name');
                if (number && nx.plotsData && nx.plotsData.length > 0) {
                    i = 0;
                    do {
                        var series = nx.plotsData[i];
                        i++;
                    } while (series.number != number && i <= nx.plotsData.length);
                    if (i != nx.plotsData.length) {
                        newPlotsData.push(series);
                        newColors.push(series.color);
                    }
                }
            });

            if (newPlotsData.length == 0) {
                newPlotsData.push({
                    data: [],
                });
                newColors.push('#FFF');
            }

            nx.draw(newPlotsData, newColors);
        }
    }

    $.each(nx.plotsData, function(i, series) {
        $('#legend-placeholder').find('#label_' + series.number + '_id').click(nx.redraw);
    });

    nx.redraw();
}

