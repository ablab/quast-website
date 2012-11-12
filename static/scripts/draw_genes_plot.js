
var gns = {
    genes: {
        isInitialized: false,

        maxY: 0,
        maxYTick: 0,
        series: null,
        showWithData: null,

        yAxisLabeled: false,
    },

    operons: {
        isInitialized: false,

        maxY: 0,
        maxYTick: 0,
        series: null,
        showWithData: null,

        yAxisLabeled: false,
    },

    draw: function (name, colors, filenames, data, referenceLength,
                    placeholder, legendPlaceholder, glossary) {
//    div.html(
//        "<span class='plot-header'>" + kind[0].toUpperCase() + kind.slice(1) + "s covered</span>" +
//        "<div class='plot-placeholder' id='" + kind + "s-plot-placeholder'></div>"
//    );

        var info = gns[name];

        info.yAxisLabeled = false;

        if (!info.isInitialized) {
            var contigsInfos = data.contigsInfos;
            var genes = data.genes;
            var found = data.found;
            var kind = data.kind;

            var plotsN = filenames.length;
            info.series = new Array(plotsN);

            info.maxY = 0;
            info.maxX = 0;

            for (var fi = 0; fi < plotsN; fi++) {
                var filename = filenames[fi];
                var contigs = contigsInfos[filename];
                for (var i = 0; i < genes.length; i++) {
                    found[i] = 0
                }

                info.series[fi] = {
                    data: [[0, 0]],
                    label: filenames[fi],
                    number: fi,
                    color: colors[fi],
                };

                var contigNo = 0;
                var totalFull = 0;

                for (var k = 0; k < contigs.length; k++) {
                    var alignedBlocks = contigs[k];
                    contigNo += 1;

                    for (i = 0; i < genes.length; i++) {
                        var g = genes[i];

                        if (found[i] == 0) {
                            for (var bi = 0; bi < alignedBlocks.length; bi++) {
                                var block = alignedBlocks[bi];

                                if (block[0] <= g[0] && g[1] <= block[1]) {
                                    found[i] = 1;
                                    totalFull += 1;
                                    break;
                                }
                            }
                        }
                    }

                    info.series[fi].data.push([contigNo, totalFull]);

                    if (info.series[fi].data[k][1] > info.maxY) {
                        info.maxY = info.series[fi].data[k][1];
                    }
                }

                if (contigs.length > info.maxX) {
                    info.maxX = contigs.length;
                }
            }

            for (i = 0; i < plotsN; i++) {
                info.series[i].lines = {
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


            info.showWithData = function(series, colors) {
                var plot = $.plot(placeholder, series, {
                    shadowSize: 0,
                    colors: colors,
                    legend: {
                        container: $('useless-invisible-element-that-does-not-even-exist'),
                    },
                    grid: {
                        borderWidth: 1,
                        hoverable: true,
                        autoHighlight: false,
                        mouseActiveRadius: 1000,
                    },
                    yaxis: {
                        min: 0,
                        labelWidth: 120,
                        reserveSpace: true,
                        lineWidth: 0.5,
                        color: '#000',
                        tickFormatter: function (val, axis) {
                            if (!info.yAxisLabeled && val > info.maxY) {
                                info.yAxisLabeled = true;
                                var res = val + ' ' + kind;
                                if (val > 1) {
                                    res += 's'
                                }
                                return res;
                            } else {
                                return val;
                            }
                        },
                        minTickSize: 1,
                    },
                    xaxis: {
                        min: 0,
                        max: info.maxX,
                        lineWidth: 0.5,
                        color: '#000',
                        tickFormatter: getContigNumberTickFormatter(info.maxX),
                        minTickSize: 1,
                    },
                });

                bindTip(placeholder, series, plot, ordinalNumberToPrettyString, 'contig', 'bottom right');
            };

            info.isInitialized = true;
        }

        $.each(info.series, function(i, series) {
            $('#legend-placeholder').find('#label_' + i + '_id').click(function() {
                showPlotWithInfo(info);
            });
        });

        showPlotWithInfo(info);

        $('#contigs_are_ordered').show();
    }
};


