import re

with open('frontend/templates/core/hospital_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

cards_html = '''<!-- Stats -->
    <div class="row g-3 mb-4">
      <div class="col-md-4 col-lg-2">
        <div class="card quick-card h-100"><div class="card-body text-center p-3">
          <div class="quick-icon bg-info-subtle text-info mx-auto mb-2"><i class="fa-solid fa-users"></i></div>
          <p class="text-muted mb-1 small">Total Donors</p>
          <h4 class="fw-bold text-info mb-0">{{ all_donors|length }}</h4>
        </div></div>
      </div>
      <div class="col-md-4 col-lg-2">
        <div class="card quick-card h-100"><div class="card-body text-center p-3">
          <div class="quick-icon bg-success-subtle text-success mx-auto mb-2"><i class="fa-solid fa-hand-holding-heart"></i></div>
          <p class="text-muted mb-1 small">Available Donors</p>
          <h4 class="fw-bold text-success mb-0">{{ available_organs|length }}</h4>
        </div></div>
      </div>
      <div class="col-md-4 col-lg-2">
        <div class="card quick-card h-100"><div class="card-body text-center p-3">
          <div class="quick-icon bg-primary-subtle text-primary mx-auto mb-2"><i class="fa-solid fa-bed-pulse"></i></div>
          <p class="text-muted mb-1 small">Total Recipients</p>
          <h4 class="fw-bold text-primary mb-0">{{ recipients|length }}</h4>
        </div></div>
      </div>
      <div class="col-md-4 col-lg-2">
        <div class="card quick-card h-100"><div class="card-body text-center p-3">
          <div class="quick-icon bg-warning-subtle text-warning mx-auto mb-2"><i class="fa-solid fa-link"></i></div>
          <p class="text-muted mb-1 small">Pending Matches</p>
          <h4 class="fw-bold text-warning mb-0">{{ transplants|length }}</h4>
        </div></div>
      </div>
      <div class="col-md-4 col-lg-2">
        <div class="card quick-card h-100"><div class="card-body text-center p-3">
          <div class="quick-icon bg-danger-subtle text-danger mx-auto mb-2"><i class="fa-solid fa-heart-pulse"></i></div>
          <p class="text-muted mb-1 small">Completed Surgeries</p>
          <h4 class="fw-bold text-danger mb-0">0</h4>
        </div></div>
      </div>
      <div class="col-md-4 col-lg-2">
        <div class="card quick-card h-100"><div class="card-body text-center p-3">
          <div class="quick-icon bg-secondary-subtle text-secondary mx-auto mb-2"><i class="fa-brands fa-ethereum"></i></div>
          <p class="text-muted mb-1 small">Blockchain Tx</p>
          <h4 class="fw-bold text-secondary mb-0">{{ blockchain_transactions|length }}</h4>
        </div></div>
      </div>
    </div>'''

text = re.sub(r'<!-- Stats -->.*?</div>\s*</div>\s*</div>\s*</div>\s*</div>\s*</div>', cards_html, text, flags=re.DOTALL)


# Let's add Recipient and Blockchain Tx sections to the end of the file right before Profile Settings
new_sections = '''
    <!-- ── Recipient Management ── -->
    <section id="hosp-recipients" data-hosp-section="hosp-recipients" class="card page-card mb-4 hosp-section-hidden">
      <div class="card-body">
        <div class="section-hdr"><i class="fa-solid fa-bed-pulse text-primary"></i>Recipients Management</div>
        <p class="text-muted">Manage hospital patients requesting organ transplants.</p>
        
        <div class="d-flex justify-content-end mb-3">
          <button type="button" class="btn btn-primary ui-action" data-bs-toggle="modal" data-bs-target="#addRecipientModal">
            <i class="fa-solid fa-plus me-1"></i> Add Recipient
          </button>
        </div>

        <div class="table-responsive">
          <table class="table align-middle">
            <thead class="table-light">
              <tr><th>Patient Name</th><th>Age</th><th>Blood Group</th><th>Organ Needed</th><th>Urgency</th><th>Status</th></tr>
            </thead>
            <tbody>
              {% for recipient in recipients %}
              <tr>
                <td><strong>{{ recipient.full_name }}</strong></td>
                <td>{{ recipient.age }}</td>
                <td><span class="badge text-bg-danger">{{ recipient.blood_group }}</span></td>
                <td>{{ recipient.organ_needed }}</td>
                <td>
                  <span class="badge {% if recipient.urgency_level == 'Critical' %}text-bg-danger{% elif recipient.urgency_level == 'High' %}text-bg-warning{% else %}text-bg-info{% endif %}">
                    {{ recipient.urgency_level }}
                  </span>
                </td>
                <td>
                  <span class="badge {% if recipient.match_status == 'Pending' %}text-bg-secondary{% else %}text-bg-success{% endif %}">
                    {{ recipient.match_status }}
                  </span>
                </td>
              </tr>
              {% empty %}
              <tr><td colspan="6" class="text-center text-muted py-4">No recipients registered yet.</td></tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- ── Blockchain Records ── -->
    <section id="hosp-blockchain-tx" data-hosp-section="hosp-blockchain-tx" class="card page-card mb-4 hosp-section-hidden">
      <div class="card-body">
        <div class="section-hdr"><i class="fa-brands fa-ethereum text-primary"></i>Blockchain Verification History</div>
        <p class="text-muted">Immutable log of organ registrations and transplant matches associated with this hospital.</p>

        <div class="table-responsive mt-3">
          <table class="table align-middle table-hover">
            <thead class="table-light">
              <tr>
                <th>Time</th>
                <th>Tx Hash</th>
                <th>Action</th>
                <th>Donor</th>
                <th>Organ</th>
              </tr>
            </thead>
            <tbody>
              {% for tx in blockchain_transactions %}
              <tr>
                <td class="text-nowrap small text-muted">{{ tx.timestamp|date:"M d, Y H:i" }}</td>
                <td>
                  <span class="ledger-id" title="{{ tx.transaction_hash }}">
                    {{ tx.transaction_hash|slice:":16" }}...
                  </span>
                </td>
                <td><span class="badge text-bg-info">{{ tx.action_type }}</span></td>
                <td>{{ tx.donor.user.get_full_name|default:"Unknown" }}</td>
                <td>{{ tx.organ_type|default:"-" }}</td>
              </tr>
              {% empty %}
              <tr>
                <td colspan="5" class="text-center text-muted py-4">No blockchain transactions found.</td>
              </tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- ── Profile Settings ── -->
'''

text = text.replace('<!-- ── Profile Settings ── -->', new_sections)

with open('frontend/templates/core/hospital_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(text)

