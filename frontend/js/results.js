/**
 * Handles the display and interaction logic for the results page.
 * 
 * This script retrieves generation results from session storage,
 * populates the DOM elements with policy and audit details,
 * and handles file downloads for the presentation and audit reports.
 */

const resultRaw = sessionStorage.getItem("generation_result");

if (!resultRaw) {
    window.location.href = "/";
} else {
    const result = JSON.parse(resultRaw);

    /**
     * Populates UI elements with data from the parsed result object.
     */
    document.getElementById("company").textContent =
        `${result.company.company_name} · ${result.policy.provider}`;

    document.getElementById("ppt-download").href =
        result.files.pptx;

    document.getElementById("audit-download").href =
        result.files.audit_report;

    document.getElementById("total").textContent =
        result.audit.total_claims;

    document.getElementById("supported").textContent =
        result.audit.supported_claims;

    document.getElementById("partial").textContent =
        result.audit.partially_supported_claims;

    document.getElementById("unsupported").textContent =
        result.audit.unsupported_claims;


    /**
     * Event listener for the "Download All" button.
     * Triggers both PPTX and audit report downloads with a delay.
     */
    document.getElementById("download-deck").addEventListener(
        "click",
        async () => {
            downloadFile(result.files.pptx);
            await wait(400);
            downloadFile(result.files.audit_report);
        }
    );
}


/**
 * Helper to programmatically trigger a file download.
 * 
 * @param {string} url - The URL of the file to download.
 */
function downloadFile(url) {
    const link = document.createElement("a");

    link.href = url;
    link.download = "";
    document.body.appendChild(link);
    link.click();
    link.remove();
}


/**
 * Helper for introducing a delay.
 * 
 * @param {number} milliseconds - Time in milliseconds to wait.
 * @returns {Promise<void>}
 */
function wait(milliseconds) {
    return new Promise(resolve => {
        setTimeout(resolve, milliseconds);
    });
}
