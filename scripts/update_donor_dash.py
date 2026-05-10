import re

with open('frontend/templates/core/donor_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

new_nav = '''<nav class="role-sidebar-nav">
      <a class="role-nav-link active ui-action" href="#donor-overview" data-donor-target="donor-overview">
        <i class="fa-solid fa-gauge-high"></i><span>Dashboard</span>
      </a>
      <a class="role-nav-link ui-action" href="#donor-donate" data-donor-target="donor-donate">
        <i class="fa-solid fa-hand-holding-medical"></i><span>Donate Organ</span>
      </a>
      <a class="role-nav-link ui-action" href="#donor-status" data-donor-target="donor-status">
        <i class="fa-solid fa-heart-pulse"></i><span>My Donation Status</span>
      </a>
      <a class="role-nav-link ui-action" href="#donor-profile" data-donor-target="donor-profile">
        <i class="fa-solid fa-address-card"></i><span>My Profile</span>
      </a>
      
      <div class="role-nav-group-label" style="font-size: 0.75rem; text-transform: uppercase; font-weight: 700; color: var(--dash-muted, #64748b); margin: 1.25rem 0 0.5rem 0.5rem; letter-spacing: 0.5px;">Blockchain</div>
      <a class="role-nav-link dropdown-toggle-link" data-bs-toggle="collapse" href="#collapseDonorBlockchain" role="button" aria-expanded="false" style="display:flex;align-items:center;">
        <i class="fa-brands fa-ethereum"></i><span>Verification</span>
        <i class="fa-solid fa-chevron-down ms-auto font-size-sm"></i>
      </a>
      <div class="collapse" id="collapseDonorBlockchain">
        <div class="role-nav-sub" style="display:flex;flex-direction:column;gap:0.15rem;padding-left:1rem;margin-left:0.75rem;border-left:1px solid var(--dash-border, rgba(255, 255, 255, 0.1));margin-bottom:0.5rem;">
          <a class="role-nav-link ui-action" href="#donor-blockchain" data-donor-target="donor-blockchain" style="padding:0.5rem 1rem;font-size:0.85rem;min-height:auto;"><span>My Transactions</span></a>
        </div>
      </div>
      
      <div class="role-nav-group-label" style="font-size: 0.75rem; text-transform: uppercase; font-weight: 700; color: var(--dash-muted, #64748b); margin: 1.25rem 0 0.5rem 0.5rem; letter-spacing: 0.5px;">Settings</div>
      <a class="role-nav-link ui-action" href="#donor-feedback" data-donor-target="donor-feedback">
        <i class="fa-solid fa-comments"></i><span>Feedback</span>
      </a>
      <a class="role-nav-link ui-action" href="#donor-profile" data-donor-target="donor-profile">
        <i class="fa-solid fa-user-gear"></i><span>Profile Settings</span>
      </a>
      <a class="role-nav-link" href="{% url 'logout' %}">
        <i class="fa-solid fa-right-from-bracket"></i><span>Logout</span>
      </a>
    </nav>'''

text = re.sub(r'<nav class="role-sidebar-nav">.*?</nav>', new_nav, text, flags=re.DOTALL)

# Add blockchain transactions section right before Feedback section
blockchain_section = '''
    <!-- ── SECTION: Blockchain Verification ── -->
    <section id="donor-blockchain" data-donor-section="donor-blockchain" class="card page-card mb-4 donor-section-hidden">
      <div class="card-body">
        <div class="section-header"><i class="fa-brands fa-ethereum text-primary"></i>My Blockchain Transactions</div>
        <p class="text-muted">View the immutable ledger of your organ pledges and successful transplant matches.</p>
        <div class="table-responsive">
          <table class="table align-middle">
            <thead class="table-light">
              <tr>
                <th>Date</th>
                <th>Tx Hash</th>
                <th>Action</th>
                <th>Hospital</th>
                <th>Organ</th>
              </tr>
            </thead>
            <tbody>
              {% for tx in blockchain_transactions %}
              <tr>
                <td class="text-muted small">{{ tx.timestamp|date:"M d, Y H:i" }}</td>
                <td>
                  <span class="ledger-id" title="{{ tx.transaction_hash }}">
                    {{ tx.transaction_hash|slice:":16" }}...
                  </span>
                </td>
                <td><span class="badge text-bg-success">{{ tx.action_type }}</span></td>
                <td>{{ tx.hospital.hospital_name|default:"-" }}</td>
                <td>{{ tx.organ_type|default:"-" }}</td>
              </tr>
              {% empty %}
              <tr><td colspan="5" class="text-center text-muted py-4">No blockchain verification records found yet.</td></tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- ── SECTION: Feedback ── -->
'''

text = text.replace('<!-- ── SECTION: Feedback ── -->', blockchain_section)

# Update javascript keys
js_keys_replacement = '''const sectionKeys = new Set([
      "donor-overview", "donor-donate", "donor-status", "donor-profile", "donor-feedback", "donor-blockchain"
    ]);'''
text = re.sub(r'const sectionKeys = new Set\(\[.*?\]\);', js_keys_replacement, text, flags=re.DOTALL)

with open('frontend/templates/core/donor_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(text)
