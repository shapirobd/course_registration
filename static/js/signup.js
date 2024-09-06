document.addEventListener("DOMContentLoaded", function () {
	const form = document.querySelector("form");

	form.addEventListener("submit", function (event) {
		// Clear previous error messages
		document
			.querySelectorAll(".error-message")
			.forEach((el) => (el.textContent = ""));

		let isValid = true;

		// Get form values
		const username = document.getElementById("username").value.trim();
		const password = document.getElementById("password").value.trim();
		const firstName = document.getElementById("first_name").value.trim();
		const lastName = document.getElementById("last_name").value.trim();
		const major = document.getElementById("major").value.trim();
		const email = document.getElementById("email").value.trim();
		const phone = document.getElementById("phone").value.trim();
		const address = document.getElementById("address").value.trim();
		const city = document.getElementById("city").value.trim();
		const state = document.getElementById("state").value.trim();
		const zipCode = document.getElementById("zip_code").value.trim();

		// Username validation
		if (username.length < 5 || username.length > 20) {
			displayError("username", "Username must be between 5 and 20 characters.");
			isValid = false;
		}

		// Password validation
		if (password.length < 8) {
			displayError("password", "Password must be at least 8 characters.");
			isValid = false;
		}

		// First Name validation
		if (firstName === "") {
			displayError("first_name", "First name is required.");
			isValid = false;
		}

		// Last Name validation
		if (lastName === "") {
			displayError("last_name", "Last name is required.");
			isValid = false;
		}

		// Email validation
		if (!validateEmail(email)) {
			displayError("email", "Invalid email address.");
			isValid = false;
		}

		// Phone validation (optional but can be validated for format if needed)
		// Optional field, so no validation required here

		// Address validation
		if (address === "") {
			displayError("address", "Address is required.");
			isValid = false;
		}

		// City validation
		if (city === "") {
			displayError("city", "City is required.");
			isValid = false;
		}

		// State validation
		if (!/^[A-Z]{2}$/.test(state)) {
			displayError("state", "State must be exactly 2 letters.");
			isValid = false;
		}

		// Zip Code validation
		if (!/^\d{5}(-\d{4})?$/.test(zipCode)) {
			displayError("zip_code", "Zip code must be a valid US zip code.");
			isValid = false;
		}

		if (!isValid) {
			event.preventDefault(); // Prevent form from submitting if validation fails
		}
	});

	function displayError(inputId, message) {
		const inputElement = document.getElementById(inputId);
		let errorElement = inputElement.nextElementSibling;

		if (!errorElement || !errorElement.classList.contains("error-message")) {
			errorElement = document.createElement("div");
			errorElement.className = "error-message";
			inputElement.parentNode.insertBefore(
				errorElement,
				inputElement.nextSibling
			);
		}

		errorElement.textContent = message;
	}

	function validateEmail(email) {
		const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
		return re.test(email);
	}
});
