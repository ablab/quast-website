$(document).ready(function() {
    $("#add-dataset-toggle-link").mouseenter(function() {
        $(this).find('a').css('color', '#b33');
        $(this).find('a').css('border-bottom', '1px dashed #ffcccc');
        $(this).find('a').css('border-color', '1px dashed #ffcccc');
        $(this).find('a').css('border-color', 'rgba(255, 0, 0, 0.2)');
    }).mouseleave(function() {
            /*TODO*/
            $(this).find('a').css('color', '#0c4f72');
            $(this).find('a').css('border-bottom', '1px dashed #487b95');
            $(this).find('a').css('border-color', '#487b95');
            $(this).find('a').css('border-color', 'rgba(12, 79, 114, 0.2)');
        });
});

$(function() {
    var uploaders = [];

    var paramters = [{
        action: '{% url contigs_ajax_upload %}',
        removeLink: '{% url contigs_ajax_remove %}',
        initializeUploadsLink: '{% url contigs_ajax_initialize_uploads %}',
        elementId: '#contigs-uploader',
        multiple: true,
        btnText: 'Select files with contigs',
        areaText: 'or drop files with contigs here',
        areaClass: 'upload-drop-area',
        uploaded: '{% for fname in contigs_fnames %}<li>{{ fname }} &nbsp;' +
//                    '<a class="dotted-link" style="font-size: 0.8em;" href="#">Remove</a>' +
                  '</li>{% endfor %}',
    },];

    for (var i = 0; i < paramters.length; i++) {
        uploaders.push(new qq.FileUploader({
            action: paramters[i].action,
            removeLink: paramters[i].removeLink,
            initializeUploadsLink: paramters[i].initializeUploadsLink,
            element: $(paramters[i].elementId)[0],
            multiple: paramters[i].multiple,
            onComplete: function(id, fileName, responseJSON) {
                if (responseJSON.success) {
                    $('#evaluate-button').prop('disabled', false);
                    $('#evaluate-button').removeClass('disabled');
                }
            },
            onAllComplete: function(uploads) {
                if (uploads.length > 0) {
                    $('#evaluate-button').prop('disabled', false);
                    $('#evaluate-button').removeClass('disabled');
                }
                // uploads is an array of maps
                // the maps look like this: {file: FileObject, response: JSONServerResponse}
            },
            onRemove: function() {
                var number_of_files = -1;
                $('.qq-upload-file').each(function(index) {
                    number_of_files++;
                });

                if (number_of_files <= 0) {
                    $('#evaluate-button').prop('disabled', true);
                    $('#evaluate-button').addClass('disabled');
                }
            },
            onInitFiles: function(files){
                if (!files || files.length == 0) {
                    $('#evaluate-button').prop('disabled', true);
                    $('#evaluate-button').addClass('disabled');
                } else {
                    $('#evaluate-button').prop('disabled', false);
                    $('#evaluate-button').removeClass('disabled');
                }
            },
            params: {
                'csrf_token': '{{ csrf_token }}',
                'csrf_name': 'csrfmiddlewaretoken',
                'csrf_xname': 'X-CSRFToken',
            },
            messages: {
            },
            template:
                '<div class="qq-uploader">' +
                    '<button class="btn">' + paramters[i].btnText + '</button>' +
                    '<div>' +
                    '<div class="' + paramters[i].areaClass + '">' +
                    '<p>' + paramters[i].areaText + '</p>' +
                    '</div>' +
                    '<div class="upload-list-div">' +
                    '<ul class="upload-list"></ul>' +
                    '</div>' +
                    '</div>' +
                    '</div>',
            fileTemplate:
                '<li>' +
                    '<span class="qq-upload-file"></span>' +
                    '<span class="qq-upload-spinner"></span>' +
                    '<span class="qq-upload-size"></span>' +
                    '<a class="dotted-link qq-upload-cancel" href="#">Cancel</a>' +
                    '<a class="dotted-link qq-upload-remove" href="#">Remove</a>' +
                    '<span class="qq-upload-failed-text">Failed</span>' +
//                            '<a class="dotted-link" style="font-size: 0.8em;" href="#">Remove</a>' +
                '</li>',
            classes: {
                // used to get elements from templates
                button: 'btn',
                drop: paramters[i].areaClass,
                dropActive: 'upload-drop-area-active',
                list: 'upload-list',

                file: 'qq-upload-file',
                spinner: 'qq-upload-spinner',
                size: 'qq-upload-size',
                cancel: 'qq-upload-cancel',
                remove: 'qq-upload-remove',

                // added to list item when upload completes
                // used in css to hide progress spinner
                success: 'qq-upload-success',
                fail: 'qq-upload-fail'
            }
        }));
    }
});

//        $('#add-dataset-wrapper').click(
//            $('#add-dataset-toggle-link').
//        );

function showHideAddDataset() {
    if ($('#add-dataset').is(':visible')) {
        $('#add-dataset').hide('fast');
        $('#dataset-name-select-input').prop('disabled', false);
        set_selected();
    } else {
        $('#add-dataset').show('fast');
        $('#dataset-name-select-input').prop('disabled', true);
        set_created();
    }
}

function set_selected() {
    $('#id_created_or_selected').prop('value', 'selected');
}

function set_created() {
    $('#id_created_or_selected').prop('value', 'created');
}