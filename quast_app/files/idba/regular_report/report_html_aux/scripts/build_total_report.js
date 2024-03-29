String.prototype.trunc =
    function(n){
        return this.substr(0, n-1) + (this.length > n ? '&hellip;' : '');
    };

function buildTotalReport(assembliesNames, report, date, minContig, glossary, qualities, mainMetrics) {
    $('#subheader').html('<p>' + date + '</p>');
    $('#mincontig').html('<p>All statistics are based on contigs of size >= ' + minContig +
        '<span class="rhs">&nbsp;</span>bp, unless otherwise noted (e.g., "# contigs (>= 0 bp)" and "Total length (>= 0 bp)" include all contigs.)</p>');

//    $('#extended_link').css('width', '183');

    $('#extended_link').append('' +
        '<div id="extended_report_link_div" style="float: left;"><a class="dotted-link" id="extended_report_link">Extended report</a>' +
        '</div>' +
        '<div style="float: left;"><span id="report_legend" style="display: none;"></span>' +
        '</div>' +
        '<div style="clear: both;">' +
        '</div>');

    $('#extended_report_link').click(function() {
        $('.row_hidden').fadeToggle('fast');

        var link = $('#extended_report_link');
        if (link.html() == 'Extended report') {
            link.html('Short report');
        } else {
            link.html('Extended report');
        }
    });

    var table = '';
    table += '<table cellspacing="0" class="report-table draggable">';

    for (var group_n = 0; group_n < report.length; group_n++) {
        var group = report[group_n];
        var groupName = group[0];
        var metrics = group[1];
        var width = assembliesNames.length + 1;

        if (group_n == 0) {
            table += '<tr class="header-tr"><td id="first_td">' + groupName + '</td>';

            for (var assembly_n = 0; assembly_n < assembliesNames.length; assembly_n++) {
                var assemblyName = assembliesNames[assembly_n];
                if (assemblyName.length > 30) {
                    assemblyName =
                        '<span class="tooltip-link" rel="tooltip" title="' + assemblyName + '">' +
                            assemblyName.trunc(30) +
                            '</span>'
                }

                table += '<td>' + assemblyName + '</td>';
            }

        } else {
            table +=
                '<tr class="subheader-tr row_hidden" id="group_' + group_n + '">' +
                    '<td>' + groupName + '</td>'; //colspan="' + width + '"
            for (var i = 0; i < width - 1; i++) {
                table += '<td></td>';
            }
            table += '</tr>';
        }

        for (var metric_n = 0; metric_n < metrics.length; metric_n++) {
            var metric = metrics[metric_n];
            var metricName = metric.metricName;
            var quality = metric.quality;
            var values = metric.values;

            var trClass = 'content-row';
            if (metric.isMain || $.inArray(metricName, mainMetrics) > -1) {
                (function(group_n) {
                    var id = '#group_' + group_n;
                    $(function() {
                        $(id).removeClass('row_hidden');
                    });
                })(group_n);
            } else {
                trClass = 'content-row row_hidden';
            }

            table +=
                '<tr class="' + trClass + '" quality="' + quality + '">' +
                    '<td><span class="metric-name">' +
                    addTooltipIfDefinitionExists(glossary, metricName) +
                    '</span>' +
                    '</td>';

            for (var value_n = 0; value_n < values.length; value_n++) {
                var value = values[value_n];

                if (value === null || value === '') {
                    table += '<td><span>-</span></td>';
                } else {
                    if (typeof value === 'number') {
                        table +=
                            '<td number="' + value + '"><span>'
                                + toPrettyString(value) + '</span></td>';
                    } else {
                        var result = /([0-9\.]+)(.*)/.exec(value);
                        var num = parseFloat(result[1]);
                        var rest = result[2];
//                        alert('value = ' + value + ' result = ' + result);

//                        var num = parseFloat(value);

                        if (num !== null) {
                            table += '<td number="' + num + '"><span>' + toPrettyString(num) + rest + '</span></td>';
                        } else {
                            table += '<td><span>' + value + '</span></td>';
                        }
                    }
                }
            }
        }
        table += '</tr>';
    }
    table += '</table>';

    $('#report').append(table);

    var RED_HUE = 0;
    var GREEN_HUE = 120;
    var GREEN_HSL = 'hsl(' + GREEN_HUE + ', 80%, 40%)';

    var legend = '<span>';
    var step = 6;
    for (var hue = RED_HUE; hue < GREEN_HUE + step; hue += step) {
        var lightness = (Math.pow(hue-75, 2))/350 + 35;
        legend += '<span style="color: hsl(' + hue + ', 80%, ' + lightness + '%);">';

        switch (hue) {
            case RED_HUE:
                legend += 'w'; break;
            case RED_HUE + step:
                legend += 'o'; break;
            case RED_HUE + 2 * step:
                legend += 'r'; break;
            case RED_HUE + 3 * step:
                legend += 's'; break;
            case RED_HUE + 4 * step:
                legend += 't'; break;

            case GREEN_HUE - 3 * step:
                legend += 'b'; break;
            case GREEN_HUE - 2 * step:
                legend += 'e'; break;
            case GREEN_HUE - step:
                legend += 's'; break;
            case GREEN_HUE:
                legend += 't'; break;

            default:
                legend += '.';
        }
        legend += '</span>';
    }
    legend += '</span>';
    $('#extended_report_link_div').width($('#first_td').outerWidth());

    $('#report_legend').append(legend);

    $(".report-table td[number]").mouseenter(function() {
        var cells = $(this).parent().find('td[number]');
        var numbers = $.map(cells, function(cell) { return $(cell).attr('number'); });
        var quality = $(this).parent().attr('quality');

        var min = Math.min.apply(null, numbers);
        var max = Math.max.apply(null, numbers);

        var maxHue = GREEN_HUE;
        var minHue = RED_HUE;

        if (quality == 'Less is better') {
            maxHue = RED_HUE;
            minHue = GREEN_HUE;
        }

        if (max == min) {
            $(cells).css('color', GREEN_HSL);
        } else {
            var k = (maxHue - minHue) / (max - min);
            var hue = 0;
            var lightness = 0;
            cells.each(function(i) {
                var number = numbers[i];
                hue = Math.round(minHue + (number - min)*k);
                lightness = Math.round((Math.pow(hue-75, 2))/350 + 35);
//                $(this).css('color', 'hsl(' + hue + ', 80%, 35%)');
                $(this).css('color', 'hsl(' + hue + ', 80%, ' + lightness + '%)');
            });
        }

        if (numbers.length > 1)
            $('#report_legend').show('fast');

    }).mouseleave(function() {
            $(this).parent().find('td[number]').css('color', 'black');
        });

    $(function() {
        jQuery.each($(".report-table tr"), function() {
//            $(this).children(":eq(1)").after($(this).children(":eq(0)"));
        });
    });

//    });
}
//
//function buildNewTotalReport(report, glossary) {
//    var table = '';
//    table += '<table cellspacing="0" class="report-table">';
//
//    for (var col = 0; col < report.header.length; col++) {
//        var keyCell;
//
//        if (report.header[col] == '# misassemblies') {
//            table += '<tr class="subheader-tr"><td colspan="' + (report.results.length+1) + '"><b>Structural variations</b></td></tr>'
//        }
//        if (report.header[col] == 'Genome fraction (%)') {
//            table += '<tr class="subheader-tr"><td colspan="' + (report.results.length+1) + '"><b>Genes and operons</b></td></tr>'
//        }
//        if (report.header[col] == 'NA50') {
//            table += '<tr class="subheader-tr"><td colspan="' + (report.results.length+1) + '"><b>Aligned</b></td></tr>'
//        }
//
//        if (col == 0) {
//            keyCell = '<span class="report-table-header">Basic stats</span>';
//            table += '<tr><td><span style="">' + keyCell + '</span></td>';
//        } else {
//            keyCell = addTooltipIfDefinitionExists(glossary, report.header[col]);
//            table += '<tr class="content-row"><td><span style="">' + keyCell + '</span></td>';
//        }
//
//        for (var row = 0; row < report.results.length; row++) {
//            var value = report.results[row][col];
//            var valueCell = value;
//
//            if (col == 0) {
//                valueCell = '<span class="report-table-header">' + value + '</span>';
//                table += '<td><span>' + valueCell + '</span></td>';
//
//            } else {
//                if (value == 'None' /* && report.header[i].substr(0,2) == 'NG' */) {
//                    valueCell = '-';
//                    table += '<td><span>' + valueCell + '</span></td>';
//
//                } else {
//                    if (typeof value == 'number') {
//                        valueCell = toPrettyString(value);
//                        table += '<td number="' + value + '"><span>' + valueCell + '</span></td>';
//                    } else {
//                        valueCell = toPrettyString(value);
//                        table += '<td><span>' + valueCell + '</span></td>';
//                    }
//                }
//            }
//        }
//        table += '</tr>\n';
//    }
//    table += '</table>';
//
//    $(document).ready(function() {
//        $(".report-table td:[number]").mouseenter(function() {
//            var cells = $(this).parent().find('td:[number]');
//            var numbers = $.map(cells, function(cell) { return $(cell).attr('number'); });
//
//            var min = Math.min.apply(null, numbers);
//            var max = Math.max.apply(null, numbers);
//
//            var RED_HUE = 0;
//            var GREEN_HUE = 130;
//
//            if (max == min) {
//                $(cells).css('color', 'hsl(' + GREEN_HUE + ', 80%, 50%)');
//            } else {
//                var k = (GREEN_HUE - RED_HUE) / (max - min);
//
//                cells.each(function(i) {
//                    var number = numbers[i];
//                    var hue = (number - min)*k;
//                    $(this).css('color', 'hsl(' + hue + ', 80%, 50%)');
//                });
//            }
//        }).mouseleave(function() {
//            $(this).parent().find('td:[number]').css('color', 'black');
//        });
//    });
//
//    $('#report').append(table);
//}
//
//
