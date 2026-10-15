document.addEventListener("DOMContentLoaded", () => {
    fetch("news.json")
        .then(response => response.json())
        .then(data => {
            // Handle Last Updated timestamp display
            if (data._metadata && data._metadata.last_updated) {
                const lastUpdatedUTC = new Date(data._metadata.last_updated.replace(" UTC", "Z"));
                const now = new Date();
                
                // Calculate time elapsed since last update
                const diffMs = now - lastUpdatedUTC;
                const diffMins = Math.floor(diffMs / (1000 * 60));
                const diffHours = Math.floor(diffMins / 60);
                
                let timeAgoText = "";
                if (diffHours > 0) {
                    timeAgoText = `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
                } else {
                    timeAgoText = `${diffMins} minute${diffMins !== 1 ? 's' : ''} ago`;
                }

                // Calculate next refresh (assuming 4-hour cycle)
                const nextRefresh = new Date(lastUpdatedUTC.getTime() + (4 * 60 * 60 * 1000));
                const timeToNextMs = nextRefresh - now;
                const timeToNextMins = Math.max(0, Math.floor(timeToNextMs / (1000 * 60)));
                const nextHours = Math.floor(timeToNextMins / 60);
                const nextMins = timeToNextMins % 60;

                const statusEl = document.getElementById("update-status");
                if (statusEl) {
                    statusEl.innerHTML = `Last updated: <strong>${timeAgoText}</strong> | Next automated refresh in approx. <strong>${nextHours}h ${nextMins}m</strong>`;
                }
            }

            const grid = document.querySelector(".dashboard-grid");

            // Loop through each region in the JSON data (skipping _metadata)
            for (const [regionKey, articles] of Object.entries(data)) {
                if (regionKey === "_metadata") continue;

                const section = document.createElement("section");
                section.className = "region-card";

                const formattedTitle = regionKey
                    .split("-")
                    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                    .join(" ");

                let articlesHTML = "";
                articles.forEach(article => {
                    articlesHTML += `
                        <div class="news-item">
                            <h3>
                                <a href="${article.url}" target="_blank" rel="noopener noreferrer" class="news-link">
                                    ${article.headline}
                                </a>
                            </h3>
                            <p>${article.summary}</p>
                            <span class="sources">Sources: ${article.sources.join(", ")}</span>
                        </div>
                    `;
                });

                section.innerHTML = `
                    <h2>${formattedTitle}</h2>
                    <div class="news-scroll-container">
                        ${articlesHTML}
                    </div>
                `;

                grid.appendChild(section);
            }
        })
        .catch(error => console.error("Error loading news data:", error));
});
