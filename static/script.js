document.addEventListener("DOMContentLoaded", function() {

    document.getElementById('contact-form').addEventListener('submit', function(e) {
        e.preventDefault();
        console.log("Event triggers");

        document.getElementById('responseMessage').innerHTML = "";

        const formData = new FormData(this);

        axios.post(window.location.href, formData)
            .then((response) => {
                let message = response.data.message;
                let messageType = response.data.message_type || 'success';

                let alertType = messageType === 'error' ? 'alert-danger' : 'alert-success';

                document.getElementById('responseMessage').innerHTML = `
                    <div class="alert ${alertType} alert-dismissible fade show" role="alert">
                        ${message}
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>
                `;
            })
            .catch(function(error) {
                document.getElementById('responseMessage').innerHTML = `
                    <div class="alert alert-danger alert-dismissible fade show" role="alert">
                        An error occurred while sending the message. Please try again later.
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>
                `;
            });
    });
});
