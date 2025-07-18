window.initReportBuilder = function () {
  const container = document.getElementById("customReportsContent");
  if (!container) return;

  // Build initial UI
  container.innerHTML = `
    <button id="loadTablesBtn">Load Tables</button>
    <div id="tablesRow"></div>
    <div id="fieldsRows"></div>
  `;

  window.tablesRow = document.getElementById("tablesRow");
  window.fieldsRows = document.getElementById("fieldsRows"); // <-- fix: remove extra space

  // Create and append selectedFieldsDiv if not present
  let selectedFieldsDiv = document.getElementById("selectedFieldsDiv");
  if (!selectedFieldsDiv) {
    selectedFieldsDiv = document.createElement("div");
    selectedFieldsDiv.id = "selectedFieldsDiv";
    container.appendChild(selectedFieldsDiv);
  }
  window.selectedFieldsDiv = selectedFieldsDiv;

  // Add a button to proceed to query generation after field selection
  let genQueryBtn = document.getElementById("genQueryBtn");
  if (!genQueryBtn) {
    genQueryBtn = document.createElement("button");
    genQueryBtn.id = "genQueryBtn";
    genQueryBtn.textContent = "Generate Query";
    genQueryBtn.style.display = "none";
    container.appendChild(genQueryBtn);
  }
  window.genQueryBtn = genQueryBtn;

  // Add SQL output area if not present
  let sqlDiv = document.getElementById("sqlDiv");
  if (!sqlDiv) {
    sqlDiv = document.createElement("div");
    sqlDiv.id = "sqlDiv";
    sqlDiv.style.marginTop = "1em";
    container.appendChild(sqlDiv);
  }
  window.sqlDiv = sqlDiv;

  // Add result table area if not present
  let resultDiv = document.getElementById("resultDiv");
  if (!resultDiv) {
    resultDiv = document.createElement("div");
    resultDiv.id = "resultDiv";
    resultDiv.style.marginTop = "1em";
    container.appendChild(resultDiv);
  }
  window.resultDiv = resultDiv;

  // Remove old click handler if any
  genQueryBtn.onclick = null;

  // Attach click handler here to ensure it is always attached
  genQueryBtn.onclick = async function () {
    const checkedTables = Array.from(
      tablesRow.querySelectorAll("input[type=checkbox]:checked")
    ).map((cb) => cb.value);

    // Collect fields and their aggregate functions
    const checkedFields = Array.from(
      fieldsRows.querySelectorAll("input.field-checkbox:checked")
    ).map((cb) => cb.value);

    // Collect aggregate functions for checked fields
    let fields = [];
    checkedFields.forEach((field) => {
      const aggSel = fieldsRows.querySelector(
        `select.agg-func-select[data-field="${field}"]`
      );
      if (aggSel && aggSel.value) {
        fields.push({ field: field, agg_func: aggSel.value });
      } else {
        fields.push({ field: field, agg_func: null });
      }
    });

    if (checkedTables.length === 0 || checkedFields.length === 0) return;

    // Collect joins from UI
    let joins = [];
    if (checkedTables.length > 1) {
      const optionsDiv = document.getElementById("queryOptionsDiv");
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

    // WHERE, HAVING, ORDER BY, GROUP BY from UI (only if enabled)
    let filters = [];
    let having = [];
    let order_by = [];
    let group_by = [];

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

    // GROUP BY
    let groupEnable = document.getElementById("groupEnable");
    let groupInput = document.getElementById("groupInput");
    if (
      groupEnable &&
      groupEnable.checked &&
      groupInput &&
      groupInput.value.trim()
    ) {
      group_by = groupInput.value
        .split(",")
        .map((s) => s.trim())
        .filter((s) => s.length > 0);
    }

    // Send to backend
    const payload = {
      base_table: checkedTables[0],
      fields, // now array of {field, agg_func}
      joins,
      filters,
      having,
      order_by,
      group_by,
    };

    try {
      const res = await fetch("/reports/generate_query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        sqlDiv.innerHTML = `<b>Error:</b> ${res.status} ${res.statusText}`;
        resultDiv.innerHTML = "";
        return;
      }
      const data = await res.json();
      // Use a <pre> with CSS for wrapping and scrolling
      sqlDiv.innerHTML = `<b>Generated SQL:</b>
        <pre style="white-space:pre-wrap; word-break:break-all; overflow-x:auto; max-width:100%; background:#f4f4f4; padding:0.5em 1em; border-radius:4px;">${data.query}</pre>`;

      // Add "Run Query" button
      let runBtn = document.getElementById("runQueryBtn");
      if (!runBtn) {
        runBtn = document.createElement("button");
        runBtn.id = "runQueryBtn";
        runBtn.textContent = "Run Query";
        runBtn.style.marginLeft = "1em";
        sqlDiv.appendChild(runBtn);
      } else {
        runBtn.style.display = "inline-block";
      }

      runBtn.onclick = async function () {
        resultDiv.innerHTML = "Loading...";
        try {
          const execRes = await fetch("/reports/execute_query", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: data.query }),
          });
          if (!execRes.ok) {
            const err = await execRes.json();
            resultDiv.innerHTML = `<b>Error:</b> ${
              err.detail || execRes.statusText
            }`;
            return;
          }
          const execData = await execRes.json();
          if (!execData.columns || execData.columns.length === 0) {
            resultDiv.innerHTML = "<i>No data returned.</i>";
            return;
          }
          // Render table
          let html =
            "<table border='1' style='border-collapse:collapse; margin-top:1em;'><thead><tr>";
          execData.columns.forEach((col) => {
            html += `<th style="padding:4px 8px;">${col}</th>`;
          });
          html += "</tr></thead><tbody>";
          execData.rows.forEach((row) => {
            html += "<tr>";
            row.forEach((cell) => {
              html += `<td style="padding:4px 8px;">${
                cell !== null ? cell : ""
              }</td>`;
            });
            html += "</tr>";
          });
          html += "</tbody></table>";
          resultDiv.innerHTML = html;
        } catch (e) {
          resultDiv.innerHTML = `<b>Error:</b> ${e}`;
        }
      };
    } catch (e) {
      sqlDiv.innerHTML = `<b>Error:</b> ${e}`;
      resultDiv.innerHTML = "";
    }
  };

  let tablesData = [];

  let loadTablesBtn = document.getElementById("loadTablesBtn");
  if (loadTablesBtn) {
    loadTablesBtn.onclick = async function () {
      if (!window.tablesRow || !window.fieldsRows || !window.selectedFieldsDiv)
        return;

      const res = await fetch("/reports/tables");
      const tables = await res.json();
      tablesData = tables;
      tablesRow.innerHTML = "";
      fieldsRows.innerHTML = "";
      selectedFieldsDiv.innerHTML = "";

      // Render tables as a row of checkboxes
      const rowDiv = document.createElement("div");
      rowDiv.style.display = "flex";
      rowDiv.style.flexWrap = "wrap";
      rowDiv.style.gap = "1.5em";
      tables.forEach((table) => {
        const label = document.createElement("label");
        label.style.display = "flex";
        label.style.alignItems = "center";
        label.style.gap = "0.3em";
        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.value = table;
        checkbox.onchange = handleTableSelection;
        label.appendChild(checkbox);
        label.appendChild(document.createTextNode(table));
        rowDiv.appendChild(label);
      });
      tablesRow.appendChild(rowDiv);
    };
  }

  // Add a list of aggregate functions
  const AGG_FUNCS = ["", "SUM", "AVG", "MIN", "MAX", "COUNT"];

  async function handleTableSelection() {
    const checkedTables = Array.from(
      tablesRow.querySelectorAll("input[type=checkbox]:checked")
    ).map((cb) => cb.value);

    fieldsRows.innerHTML = "";
    selectedFieldsDiv.innerHTML = "";

    if (checkedTables.length === 0) return;

    // Fetch columns for selected tables
    const params = checkedTables
      .map((t) => "table_names=" + encodeURIComponent(t))
      .join("&");
    const res = await fetch(`/reports/columns?${params}`);
    const columnsData = await res.json();

    // Show columns for each table as a row of checkboxes + aggregate select
    Object.entries(columnsData).forEach(([table, columns]) => {
      const tableRowDiv = document.createElement("div");
      tableRowDiv.style.display = "flex";
      tableRowDiv.style.alignItems = "center";
      tableRowDiv.style.margin = "0.5em 0";

      const tableLabel = document.createElement("span");
      tableLabel.textContent = `${table}:`;
      tableLabel.style.fontWeight = "bold";
      tableLabel.style.marginRight = "1em";
      tableRowDiv.appendChild(tableLabel);

      columns.forEach((col) => {
        const label = document.createElement("label");
        label.style.display = "flex";
        label.style.alignItems = "center";
        label.style.gap = "0.2em";
        label.style.marginRight = "1em";
        const cb = document.createElement("input");
        cb.type = "checkbox";
        cb.value = `${table}.${col}`;
        cb.className = "field-checkbox";
        cb.onchange = handleFieldSelection;

        // Aggregate function select
        const aggSel = document.createElement("select");
        aggSel.className = "agg-func-select";
        aggSel.setAttribute("data-field", `${table}.${col}`);
        AGG_FUNCS.forEach((func) => {
          const opt = document.createElement("option");
          opt.value = func;
          opt.textContent = func ? func : "None";
          aggSel.appendChild(opt);
        });
        aggSel.disabled = true;
        // Enable/disable agg select with checkbox
        cb.onchange = function () {
          aggSel.disabled = !cb.checked;
          handleFieldSelection();
        };

        label.appendChild(cb);
        label.appendChild(document.createTextNode(col));
        label.appendChild(aggSel);
        tableRowDiv.appendChild(label);
      });

      fieldsRows.appendChild(tableRowDiv);
    });
  }

  function handleFieldSelection() {
    const checkedFields = Array.from(
      fieldsRows.querySelectorAll("input.field-checkbox:checked")
    ).map((cb) => cb.value);

    selectedFieldsDiv.innerHTML = "";
    if (checkedFields.length > 0) {
      const label = document.createElement("div");
      label.textContent = "Selected Fields:";
      selectedFieldsDiv.appendChild(label);

      const ul = document.createElement("ul");
      checkedFields.forEach((f) => {
        // Show aggregate function if selected
        const aggSel = fieldsRows.querySelector(
          `select.agg-func-select[data-field="${f}"]`
        );
        const agg = aggSel && aggSel.value ? ` (${aggSel.value})` : "";
        const li = document.createElement("li");
        li.textContent = f + agg;
        ul.appendChild(li);
      });
      selectedFieldsDiv.appendChild(ul);
    }

    genQueryBtn.style.display =
      checkedFields.length > 0 ? "inline-block" : "none";

    if (checkedFields.length > 0) {
      showQueryOptionsUI();
    } else {
      removeQueryOptionsUI();
    }
  }

  function showQueryOptionsUI() {
    removeQueryOptionsUI();

    let optionsDiv = document.createElement("div");
    optionsDiv.id = "queryOptionsDiv";
    optionsDiv.style.marginTop = "1em";

    const checkedTables = Array.from(
      tablesRow.querySelectorAll("input[type=checkbox]:checked")
    ).map((cb) => cb.value);

    if (checkedTables.length > 1) {
      let joinTitle = document.createElement("div");
      joinTitle.textContent = "Joins:";
      optionsDiv.appendChild(joinTitle);

      for (let i = 1; i < checkedTables.length; i++) {
        let joinRow = document.createElement("div");
        joinRow.style.marginBottom = "0.5em";

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
        onInput.placeholder = `ON condition for ${checkedTables[0]} and ${checkedTables[i]} (e.g. ${checkedTables[0]}.id = ${checkedTables[i]}.${checkedTables[0]}_id)`;
        onInput.style.width = "350px";
        onInput.className = "join-on-input";
        onInput.disabled = true;

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

    // GROUP BY
    let groupDiv = document.createElement("div");
    groupDiv.style.marginTop = "0.5em";
    let groupEnable = document.createElement("input");
    groupEnable.type = "checkbox";
    groupEnable.id = "groupEnable";
    groupEnable.style.marginRight = "0.5em";
    let groupLabel = document.createElement("label");
    groupLabel.textContent = "GROUP BY: ";
    let groupInput = document.createElement("input");
    groupInput.type = "text";
    groupInput.placeholder = "e.g. table1.col1, table2.col2";
    groupInput.style.width = "350px";
    groupInput.id = "groupInput";
    groupInput.disabled = true;
    groupEnable.onchange = function () {
      groupInput.disabled = !groupEnable.checked;
    };
    groupDiv.appendChild(groupEnable);
    groupDiv.appendChild(groupLabel);
    groupDiv.appendChild(groupInput);
    optionsDiv.appendChild(groupDiv);

    sqlDiv.parentNode.insertBefore(optionsDiv, sqlDiv);

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
};
