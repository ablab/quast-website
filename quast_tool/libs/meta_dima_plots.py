
def plot(metric, collection_banes:
    results = []
    print 'drawing... '  + metric
    ymax = 0;
    for i in range (datasets_num):
        #    print (i)
        #    print(columns)
        results.append([])
        for j in range(collection_num):
            resultsFileName = folders[i] + '_' + str(j) + "/transposed_report.tsv"
            resultsFile = open(resultsFileName, 'r')
            columns = map(lambda s: s.strip(), resultsFile.readline().split('\t'))
            values = map(lambda s: s.strip(), resultsFile.readline().split('\t'))
            #        print(values)
#            print (values)
            if values[columns.index(metric)].split()[0] == 'None' :
                metr_res = 0
            else:
                metr_res = float(values[columns.index(metric)].split()[0])
            ymax = max(ymax, metr_res)
            results[i].append(metr_res);
    fig = plt.figure()
    ax  = fig.add_subplot(111)
    #ax = fig.add_subplot(1,1,1, aspect='equal')
    plt.xticks(range(1, datasets_num + 1) , dataset_names,  size='small')
    title = metric
    #for j in range(collection_num):
    #    title += colors[j] + "  for " + str(j) + " \n"
    plt.title(title)

    #ax.set_xticks(range(1,datasets_num + 1))
    #ax.set_xticklabels(assemblies[0])
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width*0.8, box.height*1.0])

    for j in range(collection_num):
        to_plot = []
        arr = range(1, datasets_num + 1)
        for i in range(datasets_num):
            to_plot.append(results[i][j])
            arr[i] += 0.07 * (j - (collection_num-1) * 0.5)
        ax.plot( arr, to_plot, 'ro', color=colors[j])
    plt.xlim([0,datasets_num + 1])
    plt.ylim([0, math.ceil(ymax *  1.05)])
    #    ax.plot(range(1, datasets_num + 1), to_plot, 'ro', color=colors[j])
    legend = []
    for j in range(collection_num):
        legend.append(collection_names[j])

    ax.legend(legend, loc = 'center left', bbox_to_anchor = (1.0, 0.5))
    #plt.legend(legend, font='small', loc=(1.1,0.5))

    F = plt.gcf()

    DPI = F.get_dpi()
#    print "DPI:", DPI
    DefaultSize = F.get_size_inches()
    F.set_size_inches(2*DefaultSize)
    plt.savefig(output_dir +'/' + metric+'.jpg')



def plot(metrics):
    for metric in metrics:
        plot(metric)
