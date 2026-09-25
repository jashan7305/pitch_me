const resultRaw = sessionStorage.getItem("generation_result");

if (!resultRaw) {
    window.location.href = "/";
} else {
    const result = JSON.parse(resultRaw);

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


    document.getElementById("download-deck").addEventListener(
        "click",
        async () => {
            downloadFile(result.files.pptx);
            await wait(400);
            downloadFile(result.files.audit_report);
        }
    );
}


function downloadFile(url) {
    const link = document.createElement("a");

    link.href = url;
    link.download = "";
    document.body.appendChild(link);
    link.click();
    link.remove();
}


function wait(milliseconds) {
    return new Promise(resolve => {
        setTimeout(resolve, milliseconds);
    });
}