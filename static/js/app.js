window.onload = function () {
  // --- Navigation and Dynamic Content Setup ---

  // Page content templates
  const pageTemplates = {
    connections: `
    <h2>Connections</h2>
    <p>Manage your database connections here. (Feature coming soon.)</p>
  `,
    "standard-reports": `
    <h2>Standard Reports</h2>
    <p>View and run pre-defined standard reports. (Feature coming soon.)</p>
  `,
    "custom-reports": `
    <h2>Custom Reports</h2>
    <button id="loadTablesBtn">Load Tables</button>
    <ul id="tablesList"></ul>
    <!-- columnsDiv, selectedFieldsDiv, genQueryBtn, sqlDiv will be added by JS -->
  `,
    admin: `
    <h2>Admin</h2>
    <p>Administer users, permissions, and settings. (Feature coming soon.)</p>
  `,
    contact: `
    <h2>Contact</h2>
    <p>For support, contact us at <a href="mailto:support@reportapp.com">support@reportapp.com</a>.</p>
  `,
  };

  // Utility to set active nav link
  function setActiveNav(page) {
    document.querySelectorAll(".navbar a").forEach((a) => {
      if (a.dataset.page === page) {
        a.classList.add("active");
      } else {
        a.classList.remove("active");
      }
    });
  }

  // Main navigation handler
  function loadPage(page) {
    const content = document.getElementById("content");
    content.innerHTML = pageTemplates[page] || "<h2>Page Not Found</h2>";
    setActiveNav(page);

    // Only initialize report builder logic for custom-reports
    if (page === "custom-reports") {
      // Wait for DOM to update, then re-attach report builder logic
      setTimeout(initReportBuilder, 0);
    }
  }

  // Attach nav event listeners
  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".navbar a").forEach((a) => {
      a.addEventListener("click", function (e) {
        e.preventDefault();
        loadPage(a.dataset.page);
      });
    });
    // Load default page
    loadPage("custom-reports");
  });

  // --- Report Builder Logic ---

  function initReportBuilder() {
    // Assign DOM elements after the page is loaded
    window.tablesList = document.getElementById("tablesList");
    if (!window.tablesList) return; // Not on custom-reports page

    // Create and append columnsDiv and selectedFieldsDiv if not present
    let columnsDiv = document.getElementById("columnsDiv");
    if (!columnsDiv) {
      columnsDiv = document.createElement("div");
      columnsDiv.id = "columnsDiv";
      tablesList.parentNode.appendChild(columnsDiv);
    }
    window.columnsDiv = columnsDiv;

    let selectedFieldsDiv = document.getElementById("selectedFieldsDiv");
    if (!selectedFieldsDiv) {
      selectedFieldsDiv = document.createElement("div");
      selectedFieldsDiv.id = "selectedFieldsDiv";
      tablesList.parentNode.appendChild(selectedFieldsDiv);
    }
    window.selectedFieldsDiv = selectedFieldsDiv;

    // Add a button to proceed to query generation after field selection
    let genQueryBtn = document.getElementById("genQueryBtn");
    if (!genQueryBtn) {
      genQueryBtn = document.createElement("button");
      genQueryBtn.id = "genQueryBtn";
      genQueryBtn.textContent = "Generate Query";
      genQueryBtn.style.display = "none";
      tablesList.parentNode.appendChild(genQueryBtn);
    }
    window.genQueryBtn = genQueryBtn;

    // Add SQL output area if not present
    let sqlDiv = document.getElementById("sqlDiv");
    if (!sqlDiv) {
      sqlDiv = document.createElement("div");
      sqlDiv.id = "sqlDiv";
      sqlDiv.style.marginTop = "1em";
      tablesList.parentNode.appendChild(sqlDiv);
    }
    window.sqlDiv = sqlDiv;

    // Remove old click handler if any
    genQueryBtn.onclick = null;

    // Attach click handler here to ensure it is always attached
    genQueryBtn.onclick = async function () {
      const checkedTables = Array.from(
        tablesList.querySelectorAll("input[type=checkbox]:checked")
      ).map((cb) => cb.value);

      const checkedFields = Array.from(
        columnsDiv.querySelectorAll("input.field-checkbox:checked")
      ).map((cb) => cb.value);

      if (checkedTables.length === 0 || checkedFields.length === 0) return;

      // Collect joins from UI
      let joins = [];
      if (checkedTables.length > 1) {
        const optionsDiv = document.getElementById("queryOptionsDiv");
        // Only enabled joins
        let joinRows = Array.from(optionsDiv.querySelectorAll("div")).filter(
          (row) =>
            row.querySelector && row.querySelector("input[type=checkbox]")
        );
        let joinIdx = 0;
        for (let i = 1; i < checkedTables.length; i++) {
          const joinRow = joinRows[joinIdx + i - 1];
          if (!joinRow) continue;
          const joinEnable = joinRow.querySelector("input[type=checkbox]");
          const joinTypeSel = joinRow.querySelector("select");
          const onInput = joinRow.querySelector("input.join-on-input");
          if (
            joinEnable &&
            joinEnable.checked &&
            joinTypeSel &&
            onInput &&
            onInput.value.trim()
          ) {
            joins.push({
              join_type: joinTypeSel.value,
              table: checkedTables[i],
              on_condition: onInput.value.trim(),
            });
          }
        }
      }

      // WHERE, HAVING, ORDER BY from UI (only if enabled)
      let filters = [];
      let having = [];
      let order_by = [];

      let whereEnable = document.getElementById("whereEnable");
      let whereInput = document.getElementById("whereInput");
      if (
        whereEnable &&
        whereEnable.checked &&
        whereInput &&
        whereInput.value.trim()
      )
        filters.push(whereInput.value.trim());

      let havingEnable = document.getElementById("havingEnable");
      let havingInput = document.getElementById("havingInput");
      if (
        havingEnable &&
        havingEnable.checked &&
        havingInput &&
        havingInput.value.trim()
      )
        having.push(havingInput.value.trim());

      let orderEnable = document.getElementById("orderEnable");
      let orderField = document.getElementById("orderField");
      let orderDir = document.getElementById("orderDir");
      if (
        orderEnable &&
        orderEnable.checked &&
        orderField &&
        orderField.value.trim()
      ) {
        order_by.push([orderField.value.trim(), orderDir.value]);
      }

      // Send to backend
      const payload = {
        base_table: checkedTables[0],
        fields: checkedFields,
        joins,
        filters,
        having,
        order_by,
      };

      try {
        const res = await fetch("/reports/generate_query", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        if (!res.ok) {
          sqlDiv.innerHTML = `<b>Error:</b> ${res.status} ${res.statusText}`;
          return;
        }
        const data = await res.json();
        sqlDiv.innerHTML = `<b>Generated SQL:</b><pre>${data.query}</pre>`;
      } catch (e) {
        sqlDiv.innerHTML = `<b>Error:</b> ${e}`;
      }
    };

    let tablesData = [];

    let loadTablesBtn = document.getElementById("loadTablesBtn");
    if (loadTablesBtn) {
      loadTablesBtn.onclick = async function () {
        // Ensure DOM elements are available
        if (
          !window.tablesList ||
          !window.columnsDiv ||
          !window.selectedFieldsDiv
        )
          return;

        const res = await fetch("/reports/tables");
        const tables = await res.json();
        tablesData = tables;
        tablesList.innerHTML = "";
        columnsDiv.innerHTML = "";
        selectedFieldsDiv.innerHTML = "";

        tables.forEach((table) => {
          const li = document.createElement("li");
          const checkbox = document.createElement("input");
          checkbox.type = "checkbox";
          checkbox.value = table;
          checkbox.onchange = handleTableSelection;
          li.appendChild(checkbox);
          li.appendChild(document.createTextNode(" " + table));
          tablesList.appendChild(li);
        });
      };
    }

    async function handleTableSelection() {
      // Get all checked tables
      const checkedTables = Array.from(
        tablesList.querySelectorAll("input[type=checkbox]:checked")
      ).map((cb) => cb.value);

      columnsDiv.innerHTML = "";
      selectedFieldsDiv.innerHTML = "";

      if (checkedTables.length === 0) return;

      // Fetch columns for selected tables
      const params = checkedTables
        .map((t) => "table_names=" + encodeURIComponent(t))
        .join("&");
      const res = await fetch(`/reports/columns?${params}`);
      const columnsData = await res.json();

      // Show columns with checkboxes
      Object.entries(columnsData).forEach(([table, columns]) => {
        const tableTitle = document.createElement("div");
        tableTitle.textContent = `Fields of ${table}:`;
        columnsDiv.appendChild(tableTitle);

        const ul = document.createElement("ul");
        columns.forEach((col) => {
          const li = document.createElement("li");
          const cb = document.createElement("input");
          cb.type = "checkbox";
          cb.value = `${table}.${col}`;
          cb.className = "field-checkbox";
          cb.onchange = handleFieldSelection;
          li.appendChild(cb);
          li.appendChild(document.createTextNode(" " + col));
          ul.appendChild(li);
        });
        columnsDiv.appendChild(ul);
      });
    }

    function handleFieldSelection() {
      // Get all checked fields
      const checkedFields = Array.from(
        columnsDiv.querySelectorAll("input.field-checkbox:checked")
      ).map((cb) => cb.value);

      selectedFieldsDiv.innerHTML = "";
      if (checkedFields.length > 0) {
        const label = document.createElement("div");
        label.textContent = "Selected Fields:";
        selectedFieldsDiv.appendChild(label);

        const ul = document.createElement("ul");
        checkedFields.forEach((f) => {
          const li = document.createElement("li");
          li.textContent = f;
          ul.appendChild(li);
        });
        selectedFieldsDiv.appendChild(ul);
      }

      // Show generate query button if fields selected
      genQueryBtn.style.display =
        checkedFields.length > 0 ? "inline-block" : "none";

      // If enough fields, show join/clauses UI (no reload, no prompt/confirm)
      if (checkedFields.length > 0) {
        showQueryOptionsUI();
      } else {
        removeQueryOptionsUI();
      }
    }

    function showQueryOptionsUI() {
      // Remove if already present
      removeQueryOptionsUI();

      let optionsDiv = document.createElement("div");
      optionsDiv.id = "queryOptionsDiv";
      optionsDiv.style.marginTop = "1em";

      // Joins
      const checkedTables = Array.from(
        tablesList.querySelectorAll("input[type=checkbox]:checked")
      ).map((cb) => cb.value);

      if (checkedTables.length > 1) {
        let joinTitle = document.createElement("div");
        joinTitle.textContent = "Joins:";
        optionsDiv.appendChild(joinTitle);

        for (let i = 1; i < checkedTables.length; i++) {
          let joinRow = document.createElement("div");
          joinRow.style.marginBottom = "0.5em";

          // Checkbox to enable join
          let joinEnable = document.createElement("input");
          joinEnable.type = "checkbox";
          joinEnable.id = `join_enable_${i}`;
          joinEnable.style.marginRight = "0.5em";

          let joinTypeSel = document.createElement("select");
          ["INNER", "LEFT", "RIGHT"].forEach((type) => {
            let opt = document.createElement("option");
            opt.value = type;
            opt.textContent = type;
            joinTypeSel.appendChild(opt);
          });
          joinTypeSel.disabled = true;

          let onInput = document.createElement("input");
          onInput.type = "text";
          onInput.placeholder = `ON condition for ${checkedTables[i]} (e.g. ${checkedTables[0]}.id = ${checkedTables[i]}.${checkedTables[0]}_id)`;
          onInput.style.width = "350px";
          onInput.className = "join-on-input";
          onInput.disabled = true;

          // Enable/disable join fields based on checkbox
          joinEnable.onchange = function () {
            joinTypeSel.disabled = !joinEnable.checked;
            onInput.disabled = !joinEnable.checked;
          };

          joinRow.appendChild(joinEnable);
          joinRow.appendChild(document.createTextNode(`${checkedTables[i]}: `));
          joinRow.appendChild(joinTypeSel);
          joinRow.appendChild(onInput);

          optionsDiv.appendChild(joinRow);
        }
      }

      // WHERE
      let whereDiv = document.createElement("div");
      whereDiv.style.marginTop = "0.5em";
      let whereEnable = document.createElement("input");
      whereEnable.type = "checkbox";
      whereEnable.id = "whereEnable";
      whereEnable.style.marginRight = "0.5em";
      let whereLabel = document.createElement("label");
      whereLabel.textContent = "WHERE: ";
      let whereInput = document.createElement("input");
      whereInput.type = "text";
      whereInput.placeholder = "e.g. table1.col1 = 'value'";
      whereInput.style.width = "350px";
      whereInput.id = "whereInput";
      whereInput.disabled = true;
      whereEnable.onchange = function () {
        whereInput.disabled = !whereEnable.checked;
      };
      whereDiv.appendChild(whereEnable);
      whereDiv.appendChild(whereLabel);
      whereDiv.appendChild(whereInput);
      optionsDiv.appendChild(whereDiv);

      // HAVING
      let havingDiv = document.createElement("div");
      havingDiv.style.marginTop = "0.5em";
      let havingEnable = document.createElement("input");
      havingEnable.type = "checkbox";
      havingEnable.id = "havingEnable";
      havingEnable.style.marginRight = "0.5em";
      let havingLabel = document.createElement("label");
      havingLabel.textContent = "HAVING: ";
      let havingInput = document.createElement("input");
      havingInput.type = "text";
      havingInput.placeholder = "e.g. SUM(table1.col2) > 100";
      havingInput.style.width = "350px";
      havingInput.id = "havingInput";
      havingInput.disabled = true;
      havingEnable.onchange = function () {
        havingInput.disabled = !havingEnable.checked;
      };
      havingDiv.appendChild(havingEnable);
      havingDiv.appendChild(havingLabel);
      havingDiv.appendChild(havingInput);
      optionsDiv.appendChild(havingDiv);

      // ORDER BY
      let orderDiv = document.createElement("div");
      orderDiv.style.marginTop = "0.5em";
      let orderEnable = document.createElement("input");
      orderEnable.type = "checkbox";
      orderEnable.id = "orderEnable";
      orderEnable.style.marginRight = "0.5em";
      let orderLabel = document.createElement("label");
      orderLabel.textContent = "ORDER BY: ";
      let orderField = document.createElement("input");
      orderField.type = "text";
      orderField.placeholder = "e.g. table1.col1";
      orderField.style.width = "200px";
      orderField.id = "orderField";
      orderField.disabled = true;
      let orderDir = document.createElement("select");
      ["ASC", "DESC"].forEach((dir) => {
        let opt = document.createElement("option");
        opt.value = dir;
        opt.textContent = dir;
        orderDir.appendChild(opt);
      });
      orderDir.id = "orderDir";
      orderDir.disabled = true;
      orderEnable.onchange = function () {
        orderField.disabled = !orderEnable.checked;
        orderDir.disabled = !orderEnable.checked;
      };
      orderDiv.appendChild(orderEnable);
      orderDiv.appendChild(orderLabel);
      orderDiv.appendChild(orderField);
      orderDiv.appendChild(orderDir);
      optionsDiv.appendChild(orderDiv);

      // Insert before SQL div
      sqlDiv.parentNode.insertBefore(optionsDiv, sqlDiv);

      // Move the Generate Query button to the end of optionsDiv
      if (genQueryBtn.parentNode !== optionsDiv) {
        genQueryBtn.parentNode.removeChild(genQueryBtn);
        genQueryBtn.style.marginTop = "1em";
        optionsDiv.appendChild(genQueryBtn);
      }
    }

    function removeQueryOptionsUI() {
      let old = document.getElementById("queryOptionsDiv");
      if (old) old.remove();
    }
  }

  // Update generate query button to use UI fields, not prompt/confirm
  genQueryBtn.onclick = async function () {
    const checkedTables = Array.from(
      tablesList.querySelectorAll("input[type=checkbox]:checked")
    ).map((cb) => cb.value);

    const checkedFields = Array.from(
      columnsDiv.querySelectorAll("input.field-checkbox:checked")
    ).map((cb) => cb.value);

    if (checkedTables.length === 0 || checkedFields.length === 0) return;

    // Collect joins from UI
    let joins = [];
    if (checkedTables.length > 1) {
      const optionsDiv = document.getElementById("queryOptionsDiv");
      // Only enabled joins
      let joinRows = Array.from(optionsDiv.querySelectorAll("div")).filter(
        (row) => row.querySelector && row.querySelector("input[type=checkbox]")
      );
      let joinIdx = 0;
      for (let i = 1; i < checkedTables.length; i++) {
        const joinRow = joinRows[joinIdx + i - 1];
        if (!joinRow) continue;
        const joinEnable = joinRow.querySelector("input[type=checkbox]");
        const joinTypeSel = joinRow.querySelector("select");
        const onInput = joinRow.querySelector("input.join-on-input");
        if (
          joinEnable &&
          joinEnable.checked &&
          joinTypeSel &&
          onInput &&
          onInput.value.trim()
        ) {
          joins.push({
            join_type: joinTypeSel.value,
            table: checkedTables[i],
            on_condition: onInput.value.trim(),
          });
        }
      }
    }

    // WHERE, HAVING, ORDER BY from UI (only if enabled)
    let filters = [];
    let having = [];
    let order_by = [];

    let whereEnable = document.getElementById("whereEnable");
    let whereInput = document.getElementById("whereInput");
    if (
      whereEnable &&
      whereEnable.checked &&
      whereInput &&
      whereInput.value.trim()
    )
      filters.push(whereInput.value.trim());

    let havingEnable = document.getElementById("havingEnable");
    let havingInput = document.getElementById("havingInput");
    if (
      havingEnable &&
      havingEnable.checked &&
      havingInput &&
      havingInput.value.trim()
    )
      having.push(havingInput.value.trim());

    let orderEnable = document.getElementById("orderEnable");
    let orderField = document.getElementById("orderField");
    let orderDir = document.getElementById("orderDir");
    if (
      orderEnable &&
      orderEnable.checked &&
      orderField &&
      orderField.value.trim()
    ) {
      order_by.push([orderField.value.trim(), orderDir.value]);
    }

    // Send to backend
    const payload = {
      base_table: checkedTables[0],
      fields: checkedFields,
      joins,
      filters,
      having,
      order_by,
    };

    try {
      const res = await fetch("/reports/generate_query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        sqlDiv.innerHTML = `<b>Error:</b> ${res.status} ${res.statusText}`;
        return;
      }
      const data = await res.json();
      sqlDiv.innerHTML = `<b>Generated SQL:</b><pre>${data.query}</pre>`;
    } catch (e) {
      sqlDiv.innerHTML = `<b>Error:</b> ${e}`;
    }
  };
};
