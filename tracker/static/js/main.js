$(document).ready(function() {
    let offset = 0;
    let loading = false;

    function loadMoreCalendars() {
        if (loading) return;
        loading = true;

        $.get(`/load-contribution-calendars?offset=${offset}`, function(data) {
            data.calendars.forEach(function(calendar) {
                const calendarDiv = $("<div>").addClass("calendar-item");

                const userLabel = $("<h3>").addClass("user-label").text(calendar.username + " - " + calendar.university);
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

    // Handle form submission
    $("#uploadForm").submit(function (event) {
        event.preventDefault(); 

        var formData = new FormData(this);
        var uploadUrl = $("#uploadButton").data("upload-url");  // Retrieve the URL from the data attribute

        $.ajax({
            url: uploadUrl,  // Use the URL from the data attribute
            method: "POST",
            data: formData,
            processData: false,
            contentType: false,
            success: function(data) {                
                $(".modal-body").text(data.message);  // Combine message and stringified data
                $('#exampleModal').modal('show');  // Show the modal
            },
            error: function() {
                // Custom text when there's an error
                $(".modal-body").text("An error occurred. Please try again.");  // Update the modal body text
            }
        });
    });

    $(".btn-secondary").click(function() {
        $('#exampleModal').modal('hide');  // This will manually hide the modal when clicked
    });
});
