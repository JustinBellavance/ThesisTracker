$(document).ready(function() {
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
        event.preventDefault(); // Prevent the form from submitting normally

        var formData = new FormData(this); // Get the form data

        $.ajax({
            url: "{% url 'upload_docx' %}",  // URL for the view
            method: "POST",
            data: formData,
            processData: false,
            contentType: false,
            success: function (data) {
                if (data.error) {
                    showModal(data.error, 'error-message');  // Show modal with error
                } else {
                    showModal(data.message, 'success-message');  // Show modal with success message
                }
            },
            error: function () {
                showModal("An error occurred. Please try again.", 'error-message');  // Show modal if error occurs
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
