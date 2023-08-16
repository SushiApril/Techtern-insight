document.addEventListener("DOMContentLoaded", () => {
    fetch("p.csv")
        .then(response => response.text())
        .then(data => {
            const csvTable = document.getElementById("csvTable");
            const lines = data.split("\n");

            lines.forEach((line, index) => {
                if (line.trim() == "") {
                    return;
                }
                if (index > 0) {
                    const columns = line.split(",");
                    const row = document.createElement("tr");

                    columns.forEach(column => {
                        const cell = document.createElement("td");
                        cell.textContent = column;
                        row.appendChild(cell);
                    });

                    csvTable.appendChild(row);
                }
            });
        })
        .catch(error => console.error("Error fetching CSV:", error));
});