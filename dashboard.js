document.addEventListener("DOMContentLoaded", () => {
    const grid = document.getElementById("news-grid");

    fetch(`news.json?v=${new Date().getTime()}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
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

                // Calculate time until next refresh
                const nextRefresh = new Date(lastUpdatedUTC.getTime() + (4 * 60 * 60 * 1000));
                const timeToNextMs = nextRefresh - now;
                
                let refreshText = "";
                if (timeToNextMs <= 0) {
                    refreshText = "Next automated refresh: <strong>Due any moment</strong>";
                } else {
                    const timeToNextMins = Math.floor(timeToNextMs / (1000 * 60));
                    const nextHours = Math.floor(timeToNextMins / 60);
                    const nextMins = timeToNextMins % 60;
                    refreshText = `Next automated refresh in approx. <strong>${nextHours}h ${nextMins}m</strong>`;
                }
                
                const statusEl = document.getElementById("update-status");
                if (statusEl) {
                    statusEl.innerHTML = `Last updated: <strong>${timeAgoText}</strong> | ${refreshText}`;
                }
            }

            // Loop through each region in the JSON data (skipping _metadata)
            if (grid) {
                grid.innerHTML = ""; // Clear any placeholder loading text
                
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
            }
        })
        .catch(error => console.error("Error loading news data:", error));
});
