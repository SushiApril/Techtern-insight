// document.addEventListener("DOMContentLoaded", () => {
//     fetch("jobtest.csv")
//         .then(response => response.text())
//         .then(data => {
//             const csvTable = document.getElementById("csvTable");
//             const lines = data.split("\n");

//             lines.forEach((line, index) => {
//                 if (line.trim() == "") {
//                     return;
//                 }
//                 if (index > 0) {
//                     const columns = line.split(",");
//                     const row = document.createElement("tr");

//                     columns.forEach(column => {
//                         const cell = document.createElement("td");
//                         cell.textContent = column;
//                         row.appendChild(cell);
//                     });

//                     csvTable.appendChild(row);
//                 }
//             });
//         })
//         .catch(error => console.error("Error fetching CSV:", error));
// });

document.addEventListener("DOMContentLoaded", () => {
    fetch("jobtest.csv")
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

                    columns.forEach((column, columnIndex) => {
                        const cell = document.createElement("td");
                        
                        
                        // Check if the current column is the 'application-link' column
                        if (columnIndex == 5) {

                            if (column.length > 5){
                                // Create an anchor element for the link
                                const link = document.createElement("a");
                                link.href = column; // Set the link's href to the application link

                                // Create an image element for the file icon
                                const icon = document.createElement("img");
                                icon.src = "icon.png"; // Replace with the path to your file icon image
                                icon.alt = "Application Link"; // Add alt text for accessibility

                                // Add CSS styles to set the size of the icon
                                icon.classList.add("icon-link");

                                // Append the icon to the anchor element
                                link.appendChild(icon);

                                // Append the anchor element to the cell
                                cell.appendChild(link);
                            }
                        } else {
                            // For other columns, just set the cell's text content
                            cell.textContent = column;
                        }

                        // Append the cell to the row
                        row.appendChild(cell);
                    });

                    // Append the row to the table
                    csvTable.appendChild(row);
                }
            });
        })
        .catch(error => console.error("Error fetching CSV:", error));
});
