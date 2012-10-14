
function drawCumulativePlot(filenames, listsOfLengths, referenceLength,
                            div, legendPlaceholder, glossary) {
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

    var plotsN = listsOfLengths.length;
    var plotsData = new Array(plotsN);

    var maxX = 0;
    var maxY = 0;

    if (referenceLength) {
        maxY = referenceLength;
    }

    for (var i = 0; i < plotsN; i++) {
        var lengths = listsOfLengths[i];
        var size = lengths.length;

        plotsData[i] = {
            data: new Array(size+1),
            label: filenames[i],
        };

        plotsData[i].data[0] = [0, 0];

        var y = 0;
        for (var j = 0; j < size; j++) {
            y += lengths[j];
            plotsData[i].data[j+1] = [j+1, y];
            if (y > maxY) {
                maxY = y;
            }
        }

        if (size > maxX) {
            maxX = size;
        }
    }

    for (i = 0; i < plotsN; i++) {
        plotsData[i].lines = {
            show: true,
            lineWidth: 1,
        }
    }

    var maxYTick = getMaxDecimalTick(maxY);

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

    var colors = ["#FF5900", "#008FFF", "#168A16", "#7C00FF", "#00B7FF", "#FF0080", "#7AE01B", "#782400", "#E01B6A"];

    if (referenceLength) {
        plotsData = [({
            data: [[0, referenceLength], [maxX, referenceLength]],
            label: 'Reference, ' + toPrettyStringWithDimension(referenceLength, 'bp'),
            dashes: {
                show: true,
                lineWidth: 1,
            },
            yaxis: 2,
        })].concat(plotsData);

        plotsData = [({
            data: [[0, referenceLength], [maxX, referenceLength]],
            dashes: {
                show: true,
                lineWidth: 1,
            },
        })].concat(plotsData);

        colors = ["#000000"].concat(colors);
        colors = ["#000000"].concat(colors);
    }

    var yaxis = {
        min: 0,
        max: maxYTick,
        labelWidth: 120,
        reserveSpace: true,
        lineWidth: 0.5,
        color: '#000',
        tickFormatter: getBpTickFormatter(maxY),
        minTickSize: 1,
    };

    var yaxes = [yaxis];

    if (referenceLength) {
        yaxes.push({
            ticks: [referenceLength],
            min: 0,
            max: maxYTick,
            position: 'rigth',
            labelWidth: 50,
            reserveSpace: true,
            tickFormatter: function (val, axis) {
                return '<div style="">' + toPrettyStringWithDimension(referenceLength, 'bp') +
                    ' <span style="margin-left: -0.2em;">(reference)</span></div>';
            },
            minTickSize: 1,
        });
    }

    var plot = $.plot(div, plotsData, {
            shadowSize: 0,
            colors: colors,
            legend: {
                container: legendPlaceholder,
                position: 'se',
                labelBoxBorderColor: '#FFF',
            },
            grid: {
                borderWidth: 1,
            },
            yaxes: yaxes,
            xaxis: {
                min: 0,
                lineWidth: 0.5,
                color: '#000',
                tickFormatter: getContigNumberTickFormatter(maxX),
                minTickSize: 1,
            },
        }
    );

    // var o = plot.pointOffset({ x: 0, y: 0});
    // $('#cumulative-plot-placeholder').append(
    //     '<div style="position:absolute;left:' + (o.left + 400) + 'px;top:' + (o.top - 400) + 'px;color:#666;font-size:smaller">Actual measurements</div>'
    // );
}