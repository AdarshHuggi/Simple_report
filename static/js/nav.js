// Navigation and Dynamic Content Setup

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
    <div id="customReportsContent"></div>
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

function setActiveNav(page) {
  document.querySelectorAll(".navbar a").forEach((a) => {
    if (a.dataset.page === page) {
      a.classList.add("active");
    } else {
      a.classList.remove("active");
    }
  });
}

function loadPage(page) {
  const content = document.getElementById("content");
  content.innerHTML = pageTemplates[page] || "<h2>Page Not Found</h2>";
  setActiveNav(page);

  // Only initialize report builder logic for custom-reports
  if (page === "custom-reports") {
    setTimeout(() => {
      if (window.initReportBuilder) window.initReportBuilder();
    }, 0);
  }
}

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
