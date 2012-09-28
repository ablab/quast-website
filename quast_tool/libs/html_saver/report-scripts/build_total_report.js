
function buildTotalReport(report, glossary) {
    var table = '';
    table += '<table cellspacing="0" class="report-table">';

    for (var i = 0; i < report.header.length; i++) {
        var keyCell;

        if (i == 0) {
            keyCell = '<span class="report-table-header"></span>';
            table += '<tr><td><span style="">' + keyCell + '</span></td>';
        } else {
            keyCell = addTooltipIfDefenitionExists(glossary, report.header[i]);
            table += '<tr class="content-row"><td><span style="">' + keyCell + '</span></td>';
        }

        for (var j = 0; j < report.results.length; j++) {
            var value = report.results[j][i];
            var valueCell = value;

            if (i == 0) {
                valueCell = '<span class="report-table-header">' + value + '</span>';
                table += '<td><span>' + valueCell + '</span></td>';
            } else {
                if (value == 'None' /* && report.header[i].substr(0,2) == 'NG' */) {
                    valueCell = '-';
                    table += '<td><span>' + valueCell + '</span></td>';

                } else {
                    if (typeof value == 'number') {
                        valueCell = toPrettyString(value);
                        table += '<td number="' + value + '"><span>' + valueCell + '</span></td>';
                    } else {
                        valueCell = toPrettyString(value);
                        table += '<td><span>' + valueCell + '</span></td>';
                    }
                }
            }
        }
        table += '</tr>\n';
    }
    table += '</table>';

    $(document).ready(function() {
        $(".report-table td:[number]").mouseenter(function() {
            var cells = $(this).parent().find('td:[number]');
            var numbers = $.map(cells, function(cell) { return $(cell).attr('number'); });

            var min = Math.min.apply(null, numbers);
            var max = Math.max.apply(null, numbers);

            var RED_HUE = 0;
            var GREEN_HUE = 130;

            if (max == 0) {
                var a = 0;
            }

            if (max == min) {
                $(cells).css('color', 'hsl(' + GREEN_HUE + ', 80%, 50%)');
            } else {
                var k = (GREEN_HUE - RED_HUE) / (max - min);

                cells.each(function(i) {
                    var number = numbers[i];
                    var hue = (number - min)*k;
                    $(this).css('color', 'hsl(' + hue + ', 80%, 50%)');
                });
            }

        }).mouseleave(function() {
            $(this).parent().find('td:[number]').css('color', 'black');
        });
    });

    $('#report').append(table);
}
