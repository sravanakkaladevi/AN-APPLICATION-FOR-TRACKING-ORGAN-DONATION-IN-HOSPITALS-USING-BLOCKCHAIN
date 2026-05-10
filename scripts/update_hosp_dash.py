import re

with open('frontend/templates/core/hospital_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

new_nav = '''<nav class="role-sidebar-nav">
      <a class="role-nav-link ui-action active" href="#hosp-overview" data-hosp-target="hosp-overview">
        <i class="fa-solid fa-gauge-high"></i><span>Dashboard</span>
      </a>

      <div class="role-nav-group-label">Donor Management</div>
      <a class="role-nav-link dropdown-toggle-link" data-bs-toggle="collapse" href="#collapseDonors" role="button" aria-expanded="false">
        <i class="fa-solid fa-hand-holding-heart"></i><span>Donors</span>
        <i class="fa-solid fa-chevron-down ms-auto font-size-sm"></i>
      </a>
      <div class="collapse" id="collapseDonors">
        <div class="role-nav-sub">
          <a class="role-nav-link ui-action" href="#hosp-registered-donors" data-hosp-target="hosp-registered-donors"><span>Registered Donors</span></a>
          <a class="role-nav-link ui-action" href="#hosp-available" data-hosp-target="hosp-available"><span>Available Donors</span></a>
          <a class="role-nav-link ui-action" href="#hosp-donors-mgmt" data-hosp-target="hosp-donors-mgmt"><span>Donor Verification</span></a>
          <a class="role-nav-link ui-action" href="{% url 'register_organ' %}"><span>Register Organ</span></a>
        </div>
      </div>

      <div class="role-nav-group-label">Recipient Management</div>
      <a class="role-nav-link dropdown-toggle-link" data-bs-toggle="collapse" href="#collapseRecipients" role="button" aria-expanded="false">
        <i class="fa-solid fa-bed-pulse"></i><span>Recipients</span>
        <i class="fa-solid fa-chevron-down ms-auto font-size-sm"></i>
      </a>
      <div class="collapse" id="collapseRecipients">
        <div class="role-nav-sub">
          <a class="role-nav-link ui-action" href="#hosp-recipients" data-hosp-target="hosp-recipients"><span>Recipients List & Add</span></a>
        </div>
      </div>

      <div class="role-nav-group-label">Transplants & Matching</div>
      <a class="role-nav-link dropdown-toggle-link" data-bs-toggle="collapse" href="#collapseMatching" role="button" aria-expanded="false">
        <i class="fa-solid fa-link"></i><span>Organ Matching</span>
        <i class="fa-solid fa-chevron-down ms-auto font-size-sm"></i>
      </a>
      <div class="collapse" id="collapseMatching">
        <div class="role-nav-sub">
          <a class="role-nav-link ui-action" href="#hosp-registered" data-hosp-target="hosp-registered"><span>Match Donor & Recipient</span></a>
          <a class="role-nav-link ui-action" href="#hosp-search" data-hosp-target="hosp-search"><span>Search Records</span></a>
        </div>
      </div>

      <a class="role-nav-link dropdown-toggle-link" data-bs-toggle="collapse" href="#collapseTransplants" role="button" aria-expanded="false">
        <i class="fa-solid fa-heart-pulse"></i><span>Transplant Tracking</span>
        <i class="fa-solid fa-chevron-down ms-auto font-size-sm"></i>
      </a>
      <div class="collapse" id="collapseTransplants">
        <div class="role-nav-sub">
          <a class="role-nav-link ui-action" href="#hosp-received" data-hosp-target="hosp-received"><span>Tracking & Status</span></a>
        </div>
      </div>

      <div class="role-nav-group-label">Blockchain & Reports</div>
      <a class="role-nav-link dropdown-toggle-link" data-bs-toggle="collapse" href="#collapseBlockchain" role="button" aria-expanded="false">
        <i class="fa-brands fa-ethereum"></i><span>Blockchain Records</span>
        <i class="fa-solid fa-chevron-down ms-auto font-size-sm"></i>
      </a>
      <div class="collapse" id="collapseBlockchain">
        <div class="role-nav-sub">
          <a class="role-nav-link ui-action" href="#hosp-blockchain-tx" data-hosp-target="hosp-blockchain-tx"><span>Verification History</span></a>
        </div>
      </div>

      <div class="role-nav-group-label">Settings</div>
      <a class="role-nav-link ui-action" href="#hosp-profile" data-hosp-target="hosp-profile">
        <i class="fa-solid fa-user-gear"></i><span>Profile Settings</span>
      </a>
      <a class="role-nav-link ui-action" href="{% url 'logout' %}">
        <i class="fa-solid fa-right-from-bracket"></i><span>Logout</span>
      </a>
    </nav>'''

text = re.sub(r'<nav class="role-sidebar-nav">.*?</nav>', new_nav, text, flags=re.DOTALL)

js_keys_replacement = '''const sectionKeys = new Set([
        "hosp-overview", "hosp-donors-mgmt", "hosp-registered-donors",
        "hosp-available", "hosp-search", "hosp-registered", "hosp-received", "hosp-profile",
        "hosp-recipients", "hosp-blockchain-tx"
      ]);'''

text = re.sub(r'const sectionKeys = new Set\(\[.*?\]\);', js_keys_replacement, text, flags=re.DOTALL)

# Let's add CSS for role-nav-group-label and role-nav-sub
css = '''  .role-nav-group-label {
    font-size: 0.75rem;
    text-transform: uppercase;
    font-weight: 700;
    color: var(--dash-muted, #64748b);
    margin: 1.25rem 0 0.5rem 0.5rem;
    letter-spacing: 0.5px;
  }
  .role-nav-sub {
    display: flex;
    flex-direction: column;
    gap: 0.15rem;
    padding-left: 1rem;
    margin-left: 0.75rem;
    border-left: 1px solid var(--dash-border, rgba(255, 255, 255, 0.1));
    margin-bottom: 0.5rem;
  }
  .role-nav-sub .role-nav-link {
    padding: 0.5rem 1rem;
    font-size: 0.85rem;
    min-height: auto;
  }
  .dropdown-toggle-link[aria-expanded="true"] .fa-chevron-down {
    transform: rotate(180deg);
  }
  .dropdown-toggle-link .fa-chevron-down {
    transition: transform 0.2s ease;
  }
</style>'''
text = text.replace('</style>', css)

with open('frontend/templates/core/hospital_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(text)
