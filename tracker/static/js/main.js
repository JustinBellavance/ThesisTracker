$(document).ready(function() {
    let offset = 0;
    let loading = false;

    function loadMoreCalendars() {
        if (loading) return;
        loading = true;

        $.get(`/load-contribution-calendars?offset=${offset}`, function(data) {
            data.calendars.forEach(function(calendar) {
                const calendarDiv = $("<div>").addClass("calendar-item");

                const userLabel = $("<h3>").addClass("user-label").text(calendar.username + " - " + calendar.university + " - " + calendar.thesis_title);
                calendarDiv.append(userLabel);

                const chartDiv = $("<div>").attr("id", `chart-${offset}`);
                calendarDiv.append(chartDiv);

                $("#calendar-container").append(calendarDiv);

                const graphData = JSON.parse(calendar.graph);
                
                setTimeout(() => {
                    Plotly.newPlot(chartDiv.attr("id"), graphData.data, graphData.layout, { displayModeBar: false });
                }, 100);

                offset++;
            });
            loading = false;
        });
    }

    loadMoreCalendars();
    $("#calendars").on("scroll", function() {
        if ($(this).scrollTop() + $(this).innerHeight() >= $(this)[0].scrollHeight - 50) {
            loadMoreCalendars();
        }
    });

    const fileInput = $("input[name='docx_file']");
    const uploadButton = $("#uploadButton");

    // Disable the button by default
    uploadButton.prop("disabled", true);

    // Enable the button when a file is selected
    fileInput.on("change", function () {
        if (fileInput[0].files.length > 0) {
            uploadButton.prop("disabled", false);
        } else {
            uploadButton.prop("disabled", true);
        }
    });

    $("#uploadForm").submit(function (event) {
        event.preventDefault();

        var formData = new FormData(this);
        var uploadUrl = $("#uploadButton").data("upload-url");

        // Show the loading spinner when upload starts
        $("#loadingSpinner").show();
        uploadButton.prop("disabled", true);

        $.ajax({
            url: uploadUrl,
            method: "POST",
            data: formData,
            processData: false,
            contentType: false,
            success: function (data) {
                $(".modal-body").text(data.message);
                $('#exampleModal').modal('show');

                // Hide the spinner and re-enable the button after the upload completes
                $("#loadingSpinner").hide();
                uploadButton.prop("disabled", false);

                // Refresh the page after the modal is closed
                $('#exampleModal').on('hidden.bs.modal', function () {
                    location.reload();
                });
            },
            error: function () {
                $(".modal-body").text("An error occurred. Please try again.");

                // Hide the spinner and re-enable the button in case of error
                $("#loadingSpinner").hide();
                uploadButton.prop("disabled", false);
            }
        });
    });
    

    $(".btn-secondary").click(function() {
        $('#exampleModal').modal('hide');  // This will manually hide the modal when clicked
    });

    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});
