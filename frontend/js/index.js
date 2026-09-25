const form = document.getElementById("generate-form");
const companyInput = document.getElementById("company-name");
const policySelect = document.getElementById("policy");
const policyFile = document.getElementById("policy-pdf");
const fileName = document.getElementById("file-name");
const errorElement = document.getElementById("error");
const generateButton = document.getElementById("generate-button");


async function loadPolicies() {
    try {
        const response = await fetch("/api/policies");

        if (!response.ok) {
            throw new Error("Failed to load policies.");
        }

        const policies = await response.json();

        for (const policy of policies) {
            const option = document.createElement("option");

            option.value = policy.id;

            option.textContent = policy.product_name
                ? `${policy.provider} — ${policy.product_name}`
                : policy.provider;

            policySelect.appendChild(option);
        }
    } catch (error) {
        showError(error.message);
    }
}


policyFile.addEventListener("change", () => {
    if (policyFile.files.length > 0) {
        fileName.textContent = policyFile.files[0].name;

        // Custom upload takes precedence.
        policySelect.value = "";
    } else {
        fileName.textContent = "Choose a PDF";
    }
});


policySelect.addEventListener("change", () => {
    if (policySelect.value) {
        policyFile.value = "";
        fileName.textContent = "Choose a PDF";
    }
});


form.addEventListener("submit", (event) => {
    event.preventDefault();

    hideError();

    const companyName = companyInput.value.trim();
    const policyId = policySelect.value;
    const hasCustomPolicy = policyFile.files.length > 0;

    if (!companyName) {
        showError("Enter a client company name.");
        return;
    }

    if (!policyId && !hasCustomPolicy) {
        showError("Select a policy or upload a custom policy PDF.");
        return;
    }

    const formData = new FormData();

    formData.append("company_name", companyName);

    if (policyId) {
        formData.append("policy_id", policyId);
    }

    if (hasCustomPolicy) {
        formData.append("policy_pdf", policyFile.files[0]);
    }

    // FormData cannot be stored directly in sessionStorage.
    // Store the non-file fields and keep the file temporarily in memory
    // by navigating only after saving the form state.
    //
    // For custom PDFs, use a direct request from this page instead.
    if (hasCustomPolicy) {
        generateWithFile(formData);
        return;
    }

    sessionStorage.setItem(
        "generation",
        JSON.stringify({
            company_name: companyName,
            policy_id: policyId
        })
    );

    window.location.href = "/loading";
});


async function generateWithFile(formData) {
    generateButton.disabled = true;
    generateButton.textContent = "Uploading...";

    /*
     * A file cannot survive a page navigation through sessionStorage.
     * Therefore custom PDF generation is handled directly here.
     *
     * We temporarily store the response in sessionStorage and then
     * navigate to the results page.
     */

    try {
        const response = await fetch("/api/generate", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Generation failed.");
        }

        sessionStorage.setItem("generation_result", JSON.stringify(data));

        window.location.href = "/results";
    } catch (error) {
        showError(error.message);
        generateButton.disabled = false;
        generateButton.textContent = "Generate Pitch";
    }
}


function showError(message) {
    errorElement.textContent = message;
    errorElement.classList.remove("hidden");
}


function hideError() {
    errorElement.textContent = "";
    errorElement.classList.add("hidden");
}


loadPolicies();