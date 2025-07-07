window.downloadResultAsExcel = function (result) {
  if (!result || !result.columns) {
    alert("No data to download.");
    return;
  }
  let csv = "";
  csv += result.columns.map((col) => `"${col}"`).join(",") + "\r\n";
  result.rows.forEach((row) => {
    csv +=
      row
        .map((cell) => {
          if (cell === null || cell === undefined) return "";
          return `"${String(cell).replace(/"/g, '""')}"`;
        })
        .join(",") + "\r\n";
  });
  // Use UTF-8 BOM for Excel compatibility
  const BOM = "\uFEFF";
  const blob = new Blob([BOM + csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.style.display = "none";
  a.href = url;
  a.download = "report.csv";
  document.body.appendChild(a);
  a.click();
  setTimeout(() => {
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, 100);
};
