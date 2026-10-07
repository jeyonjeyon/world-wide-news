document.addEventListener("DOMContentLoaded", () => {
    fetch("news.json")
        .then(response => response.json())
        .then(data => {
            const grid = document.querySelector(".dashboard-grid");
            grid.innerHTML = ""; // Clear existing content

            // Loop through each region in the JSON data
            for (const [regionKey, articles] of Object.entries(data)) {
                const section = document.createElement("section");
                section.className = "region-card";

                // Format the region title nicely (e.g., "north-america" -> "North America")
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
