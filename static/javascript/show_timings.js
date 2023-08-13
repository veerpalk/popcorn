function showTimings(theaterName) {
    const showTimingsDiv = document.getElementById("showTimings");
    showTimingsDiv.innerHTML = "";

    const theater = theaters.find(t => t.name === theaterName);

    if (theater) {
        const timingsTable = document.createElement("table");
        timingsTable.classList.add("show-timings-table");

        const headerRow = document.createElement("tr");
        const headers = ["Format", "Date", "Show Timings"];
        headers.forEach(headerText => {
            const headerCell = document.createElement("th");
            headerCell.textContent = headerText;
            headerRow.appendChild(headerCell);
        });
        timingsTable.appendChild(headerRow);

        for (const [format, timingsData] of Object.entries(theater.movie.show_timings)) {
            for (const dateData of timingsData.dates) {
                const row = document.createElement("tr");
                const formatCell = document.createElement("td");
                formatCell.textContent = format;
                row.appendChild(formatCell);

                const dateCell = document.createElement("td");
                dateCell.textContent = `${dateData.date} (${dateData.day})`;
                row.appendChild(dateCell);

                const timingsCell = document.createElement("td");
                timingsCell.textContent = dateData.show_timings.join(", ");
                row.appendChild(timingsCell);

                timingsTable.appendChild(row);
            }
        }

        showTimingsDiv.appendChild(timingsTable);
    }
}
