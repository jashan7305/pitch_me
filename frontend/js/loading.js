const statusElement = document.getElementById("status");

const generation = sessionStorage.getItem("generation");

if (!generation) {
    window.location.href = "/";
} else {
    generate();
}


async function generate() {
    const data = JSON.parse(generation);

    const formData = new FormData();

    formData.append("company_name", data.company_name);
    formData.append("policy_id", data.policy_id);

    try {
        statusElement.textContent = "Researching the client...";

        const response = await fetch("/api/generate", {
            method: "POST",
            body: formData
        });

        statusElement.textContent = "Generating the pitch...";

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || "Generation failed.");
        }

        statusElement.textContent = "Preparing your files...";

        sessionStorage.setItem(
            "generation_result",
            JSON.stringify(result)
        );

        sessionStorage.removeItem("generation");

        window.location.href = "/results";

    } catch (error) {
        sessionStorage.setItem(
            "generation_error",
            error.message
        );

        window.location.href = "/";
    }
}