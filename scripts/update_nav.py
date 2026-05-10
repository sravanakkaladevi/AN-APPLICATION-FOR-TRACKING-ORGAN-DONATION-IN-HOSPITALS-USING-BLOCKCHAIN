import os

file_path = 'c:/Users/srava/.gemini/antigravity/scratch/organ_donation/frontend/templates/core/admin_dashboard.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

new_css = """  .admin-nav-link.active,
  .admin-nav-link:hover {
    color: var(--dash-text, #ffffff);
    background: var(--dash-panel, rgba(255, 255, 255, 0.08));
    transform: translateX(4px);
  }
  .admin-nav-group-label { font-size: 0.75rem; text-transform: uppercase; font-weight: 700; color: var(--dash-muted, #64748b); margin: 1.25rem 0 0.5rem 0.5rem; letter-spacing: 0.5px; }
  .admin-nav-sub { display: flex; flex-direction: column; gap: 0.15rem; padding-left: 1rem; margin-left: 0.75rem; border-left: 1px solid var(--dash-border, rgba(255, 255, 255, 0.1)); margin-bottom: 0.5rem; }
  .admin-nav-sub .admin-nav-link { padding: 0.5rem 1rem; font-size: 0.85rem; }
  .dropdown-toggle-link[aria-expanded="true"] .fa-chevron-down { transform: rotate(180deg); }
  .dropdown-toggle-link .fa-chevron-down { transition: transform 0.2s ease; }"""

content = content.replace("  .admin-nav-link.active,\n  .admin-nav-link:hover {\n    color: var(--dash-text, #ffffff);\n    background: var(--dash-panel, rgba(255, 255, 255, 0.08));\n    transform: translateX(4px);\n  }", new_css)

old_nav = """    <nav class="admin-sidebar-nav">
      <a class="admin-nav-link ui-action active" href="#admin-overview" data-admin-target="overview">
        <i class="fa-solid fa-gauge-high"></i><span>Dashboard</span>
      </a>
      <a class="admin-nav-link ui-action" href="#admin-wallet" data-admin-target="wallet">
        <i class="fa-brands fa-ethereum"></i><span>Wallet / Local Chain</span>
      </a>
      <a class="admin-nav-link ui-action" href="#admin-users" data-admin-target="users">
        <i class="fa-solid fa-users-gear"></i><span>User Management</span>
      </a>
      <a class="admin-nav-link ui-action" href="#admin-pending" data-admin-target="pending">
        <i class="fa-solid fa-user-clock"></i><span>Pending Users</span>
        {% if stats.pending %}<span class="admin-nav-badge" style="background:#f59e0b;">{{ stats.pending }}</span>{% endif %}
      </a>
      <a class="admin-nav-link ui-action" href="#admin-hospitals" data-admin-target="hospitals">
        <i class="fa-solid fa-hospital"></i><span>Hospital Management</span>
      </a>
      <a class="admin-nav-link ui-action" href="#admin-donors" data-admin-target="donors">
        <i class="fa-solid fa-hand-holding-heart"></i><span>Donor Management</span>
      </a>
      <a class="admin-nav-link ui-action" href="#admin-recipients" data-admin-target="recipients">
        <i class="fa-solid fa-bed-pulse"></i><span>Recipient Management</span>
      </a>
      <a class="admin-nav-link ui-action" href="#admin-ledger" data-admin-target="ledger">
        <i class="fa-solid fa-heart-pulse"></i><span>Organ Donation Details</span>
      </a>
      <a class="admin-nav-link ui-action" href="#admin-certificates" data-admin-target="certificates">
        <i class="fa-solid fa-certificate"></i><span>Death Certificates</span>
      </a>
      <a class="admin-nav-link ui-action" href="#admin-death-cert" data-admin-target="death-cert">
        <i class="fa-solid fa-skull-crossbones"></i><span>Issue Death Certificate</span>
      </a>
      <a class="admin-nav-link ui-action" href="#admin-feedback" data-admin-target="feedback">
        <i class="fa-solid fa-comments"></i><span>Feedback Management</span>
        {% if stats.feedbacks %}<span class="admin-nav-badge" style="background:#7c3aed;">{{ stats.feedbacks }}</span>{% endif %}
      </a>
      <a class="admin-nav-link ui-action" href="#admin-sentiment" data-admin-target="sentiment">
        <i class="fa-solid fa-chart-line"></i><span>Sentiment Analysis</span>
      </a>
      <a class="admin-nav-link ui-action" href="#admin-analytics" data-admin-target="analytics">
        <i class="fa-solid fa-chart-simple"></i><span>Reporting</span>
      </a>
      <a class="admin-nav-link ui-action" href="#admin-transplants" data-admin-target="transplants">
        <i class="fa-solid fa-heart-pulse"></i><span>Transplant Tracking</span>
      </a>
      <a class="admin-nav-link ui-action" href="#admin-blockchain-logs" data-admin-target="blockchain-logs">
        <i class="fa-brands fa-ethereum"></i><span>Blockchain Logs</span>
      </a>
      <a class="admin-nav-link ui-action" href="#admin-audit-logs" data-admin-target="audit-logs">
        <i class="fa-solid fa-clipboard-list"></i><span>Audit Logs</span>
      </a>
      <a class="admin-nav-link ui-action" href="#admin-profile" data-admin-target="profile">
        <i class="fa-solid fa-user-gear"></i><span>Profile Settings</span>
      </a>
    </nav>"""

new_nav = """    <nav class="admin-sidebar-nav">
      <a class="admin-nav-link ui-action active" href="#admin-overview" data-admin-target="overview">
        <i class="fa-solid fa-gauge-high"></i><span>Dashboard</span>
      </a>

      <div class="admin-nav-group-label">Blockchain & Network</div>
      <a class="admin-nav-link ui-action" href="#admin-wallet" data-admin-target="wallet">
        <i class="fa-brands fa-ethereum"></i><span>Ganache Status & Wallet</span>
      </a>

      <div class="admin-nav-group-label">Management</div>

      <a class="admin-nav-link dropdown-toggle-link" data-bs-toggle="collapse" href="#collapseUsers" role="button" aria-expanded="false">
        <i class="fa-solid fa-users-gear"></i><span>User Management</span>
        <i class="fa-solid fa-chevron-down ms-auto font-size-sm"></i>
      </a>
      <div class="collapse" id="collapseUsers">
        <div class="admin-nav-sub">
          <a class="admin-nav-link ui-action" href="#admin-users" data-admin-target="users"><span>All Users</span></a>
          <a class="admin-nav-link ui-action" href="#admin-pending" data-admin-target="pending">
            <span>Pending Users</span>
            {% if stats.pending %}<span class="admin-nav-badge" style="background:#f59e0b; margin-left:auto;">{{ stats.pending }}</span>{% endif %}
          </a>
        </div>
      </div>

      <a class="admin-nav-link dropdown-toggle-link" data-bs-toggle="collapse" href="#collapseHospitals" role="button" aria-expanded="false">
        <i class="fa-solid fa-hospital"></i><span>Hospital Management</span>
        <i class="fa-solid fa-chevron-down ms-auto font-size-sm"></i>
      </a>
      <div class="collapse" id="collapseHospitals">
        <div class="admin-nav-sub">
          <a class="admin-nav-link ui-action" href="#admin-hospitals" data-admin-target="hospitals"><span>Registered Hospitals</span></a>
        </div>
      </div>

      <a class="admin-nav-link dropdown-toggle-link" data-bs-toggle="collapse" href="#collapseDonors" role="button" aria-expanded="false">
        <i class="fa-solid fa-hand-holding-heart"></i><span>Donor Management</span>
        <i class="fa-solid fa-chevron-down ms-auto font-size-sm"></i>
      </a>
      <div class="collapse" id="collapseDonors">
        <div class="admin-nav-sub">
          <a class="admin-nav-link ui-action" href="#admin-donors" data-admin-target="donors"><span>Registered Donors</span></a>
        </div>
      </div>

      <a class="admin-nav-link dropdown-toggle-link" data-bs-toggle="collapse" href="#collapseRecipients" role="button" aria-expanded="false">
        <i class="fa-solid fa-bed-pulse"></i><span>Recipient Management</span>
        <i class="fa-solid fa-chevron-down ms-auto font-size-sm"></i>
      </a>
      <div class="collapse" id="collapseRecipients">
        <div class="admin-nav-sub">
          <a class="admin-nav-link ui-action" href="#admin-recipients" data-admin-target="recipients"><span>Recipients List</span></a>
        </div>
      </div>

      <a class="admin-nav-link dropdown-toggle-link" data-bs-toggle="collapse" href="#collapseTransplants" role="button" aria-expanded="false">
        <i class="fa-solid fa-heart-pulse"></i><span>Organ Matching</span>
        <i class="fa-solid fa-chevron-down ms-auto font-size-sm"></i>
      </a>
      <div class="collapse" id="collapseTransplants">
        <div class="admin-nav-sub">
          <a class="admin-nav-link ui-action" href="#admin-ledger" data-admin-target="ledger"><span>Match Donor & Recipient</span></a>
          <a class="admin-nav-link ui-action" href="#admin-transplants" data-admin-target="transplants"><span>Transplant Tracking</span></a>
        </div>
      </div>

      <div class="admin-nav-group-label">Records & Reports</div>

      <a class="admin-nav-link dropdown-toggle-link" data-bs-toggle="collapse" href="#collapseCertificates" role="button" aria-expanded="false">
        <i class="fa-solid fa-certificate"></i><span>Certificates</span>
        <i class="fa-solid fa-chevron-down ms-auto font-size-sm"></i>
      </a>
      <div class="collapse" id="collapseCertificates">
        <div class="admin-nav-sub">
          <a class="admin-nav-link ui-action" href="#admin-death-cert" data-admin-target="death-cert"><span>Issue Death Certificate</span></a>
          <a class="admin-nav-link ui-action" href="#admin-certificates" data-admin-target="certificates"><span>Certificates History</span></a>
        </div>
      </div>

      <a class="admin-nav-link dropdown-toggle-link" data-bs-toggle="collapse" href="#collapseFeedback" role="button" aria-expanded="false">
        <i class="fa-solid fa-comments"></i><span>Feedback & Sentiment</span>
        <i class="fa-solid fa-chevron-down ms-auto font-size-sm"></i>
      </a>
      <div class="collapse" id="collapseFeedback">
        <div class="admin-nav-sub">
          <a class="admin-nav-link ui-action" href="#admin-feedback" data-admin-target="feedback">
            <span>Feedback List</span>
            {% if stats.feedbacks %}<span class="admin-nav-badge" style="background:#7c3aed; margin-left:auto;">{{ stats.feedbacks }}</span>{% endif %}
          </a>
          <a class="admin-nav-link ui-action" href="#admin-sentiment" data-admin-target="sentiment"><span>Sentiment Analysis</span></a>
        </div>
      </div>

      <a class="admin-nav-link dropdown-toggle-link" data-bs-toggle="collapse" href="#collapseReports" role="button" aria-expanded="false">
        <i class="fa-solid fa-chart-simple"></i><span>Reports & Logs</span>
        <i class="fa-solid fa-chevron-down ms-auto font-size-sm"></i>
      </a>
      <div class="collapse" id="collapseReports">
        <div class="admin-nav-sub">
          <a class="admin-nav-link ui-action" href="#admin-analytics" data-admin-target="analytics"><span>System Reports</span></a>
          <a class="admin-nav-link ui-action" href="#admin-blockchain-logs" data-admin-target="blockchain-logs"><span>Blockchain Transactions</span></a>
          <a class="admin-nav-link ui-action" href="#admin-audit-logs" data-admin-target="audit-logs"><span>User Audit Trail</span></a>
        </div>
      </div>

      <div class="admin-nav-group-label">Settings</div>
      <a class="admin-nav-link ui-action" href="#admin-profile" data-admin-target="profile">
        <i class="fa-solid fa-user-gear"></i><span>Profile Settings</span>
      </a>
    </nav>"""

content = content.replace('\r\n', '\n')
if old_nav in content:
    content = content.replace(old_nav, new_nav)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print('Successfully updated navigation.')
else:
    print('Failed to find old_nav')
