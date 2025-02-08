$(document).ready(function() {

    $(".modal").hide();  // Ensure modal is hidden initially


    let offset = 0;
    let loading = false;

    function loadMoreCalendars() {
        if (loading) return;
        loading = true;

        $.get(`/load-contribution-calendars?offset=${offset}`, function(data) {
            data.calendars.forEach(function(calendar) {
                const calendarDiv = $("<div>").addClass("calendar-item");

                const userLabel = $("<h3>").text(calendar.username);
                calendarDiv.append(userLabel);

                const chartDiv = $("<div>").attr("id", `chart-${offset}`);
                calendarDiv.append(chartDiv);

                $("#calendar-container").append(calendarDiv);

                const graphData = JSON.parse(calendar.graph);
                Plotly.newPlot(chartDiv.attr("id"), graphData.data, graphData.layout, { displayModeBar: false });

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
            success: function (data) {
                if (data.error) {
                    showModal(data.error, true);
                } else {
                    showModal(data.message);
                }
            },
            error: function () {
                showModal("An error occurred. Please try again.", true);
            }
        });
    });

    // Show the modal
    function showModal(message, messageClass) {
        let modal = $(".modal");
        let messageText = $("#modalMessage");

        messageText.text(message);
        messageText.removeClass('error-message success-message'); // Remove any previous classes
        messageText.addClass(messageClass); // Add the appropriate message class

        modal.fadeIn(); // Show the modal with a fade-in effect
    }

    // Close the modal when the user clicks the close button
    $(".close").click(function () {
        $(".modal").fadeOut(); // Hide the modal with a fade-out effect
    });

    // Close the modal if the user clicks outside of the modal content
    $(window).click(function (event) {
        if ($(event.target).is(".modal")) {
            $(".modal").fadeOut(); // Hide the modal if clicked outside
        }
    });
});
