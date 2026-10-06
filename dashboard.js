async function loadDashboard() {
    try {
        const response = await fetch("news.json");
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();

        // 1. Render Global Overview if available
        if (data.globalOverview) {
            renderStories("global-overview", data.globalOverview);
        }

        // 2. Render each region
        const regions = [
            "north-america", 
            "latin-america", 
            "east-asia", 
            "south-asia", 
            "europe", 
            "middle-east", 
            "africa", 
            "oceania"
        ];

        regions.forEach(regionId => {
            if (data[regionId]) {
                renderStories(regionId, data[regionId]);
            }
        });

    } catch (error) {
        console.error("Failed to load news.json:", error);
    }
}

function renderStories(containerId, stories) {
    const container = document.getElementById(containerId);
    if (!container) return;

    // If it's a region panel, target its internal .stories container
    const targetContainer = container.classList.contains("region-panel") 
        ? container.querySelector(".stories") 
        : (container.querySelector(".stories") || container);

    targetContainer.innerHTML = "";

    if (!stories || stories.length === 0) {
        targetContainer.innerHTML = "<p>No updates available for this region.</p>";
        return;
    }

    stories.forEach(story => {
        const div = document.createElement("div");
        div.className = "story";

        div.innerHTML = `
            <h4>${story.headline}</h4>
            <p>${story.summary}</p>
            <p class="sources">Sources: ${story.sources.join(", ")}</p>
        `;

        targetContainer.appendChild(div);
    });
}

// Run when the page loads
document.addEventListener("DOMContentLoaded", loadDashboard);