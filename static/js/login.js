document.addEventListener("DOMContentLoaded", function () {
	const form = document.getElementById("loginForm");

	form.addEventListener("submit", async function (event) {
		event.preventDefault(); // Prevent default form submission

		// Clear previous error messages
		const formError = document.getElementById("formError");
		formError.textContent = "";

		// Submit form data via Fetch API
		try {
			const response = await fetch("/login", {
				method: "POST",
				headers: {
					"Content-Type": "application/x-www-form-urlencoded",
				},
				body: new URLSearchParams(new FormData(form)),
			});

			if (response.ok) {
				window.location.href = "/";
			} else {
				const result = await response.json();
				formError.textContent = result.error || "An error occurred.";
			}
		} catch (error) {
			formError.textContent = "An unexpected error occurred.";
			console.error("Error:", error);
		}
	});
});
