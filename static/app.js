
const API_BASE = '/api/v1/customers';
const ITEMS_PER_PAGE = 10;

const ICONS = {
  success: '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="m9 11 3 3L22 4"/></svg>',
  error: '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="m15 9-6 6"/><path d="m9 9 6 6"/></svg>',
  info: '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>',
  edit: '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/><path d="m15 5 4 4"/></svg>',
  delete: '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>',
  close: '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>',
};

// ── State ──────────────────────────────────────────────────────────────────

let currentPage = 1;
let totalPages = 1;
let totalCustomers = 0;
let editingCustomerId = null;   // null => create mode, UUID => edit mode
let deletingCustomerId = null;
let searchTimeout = null;

// ── DOM References ─────────────────────────────────────────────────────────

const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

const els = {
  // Stats
  statTotal:      $('#statTotal'),
  statAvgCredit:  $('#statAvgCredit'),
  statTotalLoan:  $('#statTotalLoan'),
  statAvgIncome:  $('#statAvgIncome'),
  customerCount:  $('#customerCount'),

  // Table
  tableBody:      $('#customerTableBody'),
  emptyState:     $('#emptyState'),
  loadingState:   $('#loadingState'),

  // Search
  searchInput:    $('#searchInput'),
  searchField:    $('#searchField'),

  // Pagination
  pagination:     $('#pagination'),
  paginationInfo: $('#paginationInfo'),
  paginationCtrl: $('#paginationControls'),

  // Buttons
  btnAdd:         $('#btnAddCustomer'),
  btnAddFirst:    $('#btnAddFirstCustomer'),
  btnRefresh:     $('#btnRefresh'),

  // Customer modal
  modal:          $('#customerModal'),
  modalTitle:     $('#modalTitle'),
  modalClose:     $('#modalClose'),
  modalCancel:    $('#modalCancel'),
  modalSave:      $('#modalSave'),
  modalSaveText:  $('#modalSaveText'),
  modalSpinner:   $('#modalSpinner'),
  form:           $('#customerForm'),

  // Delete modal
  deleteModal:        $('#deleteModal'),
  deleteModalClose:   $('#deleteModalClose'),
  deleteCancelBtn:    $('#deleteCancelBtn'),
  deleteConfirmBtn:   $('#deleteConfirmBtn'),
  deleteConfirmText:  $('#deleteConfirmText'),
  deleteSpinner:      $('#deleteSpinner'),
  deleteCustomerName: $('#deleteCustomerName'),

  // Toast
  toastContainer: $('#toastContainer'),
};

// ── Helpers ────────────────────────────────────────────────────────────────

function formatCurrency(value) {
  if (value == null) return '—';
  if (value >= 10000000) return '₹' + (value / 10000000).toFixed(2) + ' Cr';
  if (value >= 100000) return '₹' + (value / 100000).toFixed(2) + ' L';
  return '₹' + Number(value).toLocaleString('en-IN');
}

function formatNumber(value) {
  if (value == null) return '—';
  return Number(value).toLocaleString('en-IN');
}

function getCreditBadgeClass(score) {
  if (score >= 750) return 'credit-badge--excellent';
  if (score >= 650) return 'credit-badge--good';
  if (score >= 500) return 'credit-badge--fair';
  return 'credit-badge--poor';
}

function getCreditLabel(score) {
  if (score >= 750) return 'Excellent';
  if (score >= 650) return 'Good';
  if (score >= 500) return 'Fair';
  return 'Poor';
}

function getInitials(first, last) {
  return ((first?.[0] || '') + (last?.[0] || '')).toUpperCase();
}

function escapeHTML(str) {
  const div = document.createElement('div');
  div.textContent = str || '';
  return div.innerHTML;
}

// ── Toast Notifications ────────────────────────────────────────────────────

function showToast(message, type = 'info') {
  const toast = document.createElement('div');
  toast.className = `toast toast--${type}`;
  toast.innerHTML = `
    <span class="toast__icon">${ICONS[type] || ICONS.info}</span>
    <span class="toast__message">${escapeHTML(message)}</span>
    <button class="toast__close" onclick="this.closest('.toast').remove()" aria-label="Close">${ICONS.close}</button>
  `;
  els.toastContainer.appendChild(toast);

  setTimeout(() => {
    toast.classList.add('removing');
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// ── API Calls ──────────────────────────────────────────────────────────────

async function apiGet(url) {
  const res = await fetch(url);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.message || `Request failed (${res.status})`);
  }
  return res.json();
}

async function apiPost(url, body) {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.message || `Request failed (${res.status})`);
  return data;
}

async function apiPut(url, body) {
  const res = await fetch(url, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.message || `Request failed (${res.status})`);
  return data;
}

async function apiDelete(url) {
  const res = await fetch(url, { method: 'DELETE' });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.message || `Request failed (${res.status})`);
  return data;
}

// ── Fetch & Render Customers ───────────────────────────────────────────────

async function loadCustomers() {
  showLoading(true);

  const searchValue = els.searchInput.value.trim();
  const searchField = els.searchField.value;

  let url = `${API_BASE}?page=${currentPage}&limit=${ITEMS_PER_PAGE}`;
  if (searchValue) {
    url += `&${searchField}=${encodeURIComponent(searchValue)}`;
  }

  try {
    const data = await apiGet(url);
    totalCustomers = data.total;
    totalPages = data.total_pages;
    currentPage = data.page;

    renderTable(data.data);
    renderPagination();
    updateStats(data.data, data.total);
  } catch (err) {
    showToast(err.message, 'error');
    renderTable([]);
  } finally {
    showLoading(false);
  }
}

function showLoading(show) {
  els.loadingState.style.display = show ? 'block' : 'none';
  if (show) {
    els.tableBody.innerHTML = '';
    els.emptyState.style.display = 'none';
    els.pagination.style.display = 'none';
  }
}

// ── Render Table ───────────────────────────────────────────────────────────

function renderTable(customers) {
  if (!customers || customers.length === 0) {
    els.tableBody.innerHTML = '';
    els.emptyState.style.display = 'flex';
    els.pagination.style.display = 'none';
    els.customerCount.textContent = '0';
    return;
  }

  els.emptyState.style.display = 'none';

  els.tableBody.innerHTML = customers.map(c => `
    <tr>
      <td>
        <div class="customer-name">
          <div class="customer-avatar">${getInitials(c.first_name, c.last_name)}</div>
          <div class="customer-name__text">
            <span class="customer-name__full">${escapeHTML(c.first_name)} ${escapeHTML(c.last_name)}</span>
            <span class="customer-name__email">${escapeHTML(c.email)}</span>
          </div>
        </div>
      </td>
      <td>${escapeHTML(c.phone)}</td>
      <td>${escapeHTML(c.gender)}</td>
      <td><span class="employment-tag">${escapeHTML(c.employment_type)}</span></td>
      <td class="amount">${formatCurrency(c.annual_income)}</td>
      <td class="amount">${formatCurrency(c.loan_amount)}</td>
      <td>
        <span class="credit-badge ${getCreditBadgeClass(c.credit_score)}">
          ${c.credit_score} · ${getCreditLabel(c.credit_score)}
        </span>
      </td>
      <td>${escapeHTML(c.city)}, ${escapeHTML(c.state)}</td>
      <td>
        <div class="actions-cell">
          <button class="btn-icon" title="Edit" onclick="openEditModal('${c.id}')">${ICONS.edit}</button>
          <button class="btn-icon btn-icon--danger" title="Delete" onclick="openDeleteModal('${c.id}', '${escapeHTML(c.first_name)} ${escapeHTML(c.last_name)}')">${ICONS.delete}</button>
        </div>
      </td>
    </tr>
  `).join('');
}

// ── Update Stats ───────────────────────────────────────────────────────────

async function updateStats(pageData, total) {
  els.statTotal.textContent = formatNumber(total);
  els.customerCount.textContent = total;

  // For stats, fetch all customers (up to 100) so we get better averages
  try {
    const allData = await apiGet(`${API_BASE}?page=1&limit=100`);
    const all = allData.data || [];
    if (all.length > 0) {
      const avgCredit = Math.round(all.reduce((s, c) => s + c.credit_score, 0) / all.length);
      const totalLoan = all.reduce((s, c) => s + c.loan_amount, 0);
      const avgIncome = Math.round(all.reduce((s, c) => s + c.annual_income, 0) / all.length);

      els.statAvgCredit.textContent = avgCredit;
      els.statTotalLoan.textContent = formatCurrency(totalLoan);
      els.statAvgIncome.textContent = formatCurrency(avgIncome);
    } else {
      els.statAvgCredit.textContent = '—';
      els.statTotalLoan.textContent = '—';
      els.statAvgIncome.textContent = '—';
    }
  } catch {
    // Keep stats as-is on error
  }
}

// ── Render Pagination ──────────────────────────────────────────────────────

function renderPagination() {
  if (totalCustomers === 0) {
    els.pagination.style.display = 'none';
    return;
  }

  els.pagination.style.display = 'flex';
  const start = (currentPage - 1) * ITEMS_PER_PAGE + 1;
  const end = Math.min(currentPage * ITEMS_PER_PAGE, totalCustomers);
  els.paginationInfo.textContent = `Showing ${start}–${end} of ${totalCustomers} customers`;

  let btns = '';

  btns += `<button class="pagination__btn" ${currentPage <= 1 ? 'disabled' : ''} onclick="goToPage(${currentPage - 1})">← Prev</button>`;

  const maxVisible = 5;
  let startPage = Math.max(1, currentPage - Math.floor(maxVisible / 2));
  let endPage = Math.min(totalPages, startPage + maxVisible - 1);
  if (endPage - startPage < maxVisible - 1) {
    startPage = Math.max(1, endPage - maxVisible + 1);
  }

  if (startPage > 1) {
    btns += `<button class="pagination__btn" onclick="goToPage(1)">1</button>`;
    if (startPage > 2) btns += `<span style="color:var(--text-muted);padding:0 4px;">…</span>`;
  }

  for (let i = startPage; i <= endPage; i++) {
    btns += `<button class="pagination__btn ${i === currentPage ? 'pagination__btn--active' : ''}" onclick="goToPage(${i})">${i}</button>`;
  }

  if (endPage < totalPages) {
    if (endPage < totalPages - 1) btns += `<span style="color:var(--text-muted);padding:0 4px;">…</span>`;
    btns += `<button class="pagination__btn" onclick="goToPage(${totalPages})">${totalPages}</button>`;
  }

  btns += `<button class="pagination__btn" ${currentPage >= totalPages ? 'disabled' : ''} onclick="goToPage(${currentPage + 1})">Next →</button>`;

  els.paginationCtrl.innerHTML = btns;
}

function goToPage(page) {
  if (page < 1 || page > totalPages) return;
  currentPage = page;
  loadCustomers();
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ── Modal Management ───────────────────────────────────────────────────────

function openModal() {
  els.modal.classList.add('active');
  document.body.style.overflow = 'hidden';
}

function closeModal() {
  els.modal.classList.remove('active');
  document.body.style.overflow = '';
  resetForm();
}

function openCreateModal() {
  editingCustomerId = null;
  els.modalTitle.textContent = 'Add Customer';
  els.modalSaveText.textContent = 'Save Customer';
  resetForm();
  openModal();
}

async function openEditModal(id) {
  editingCustomerId = id;
  els.modalTitle.textContent = 'Edit Customer';
  els.modalSaveText.textContent = 'Update Customer';
  resetForm();

  try {
    const data = await apiGet(`${API_BASE}/${id}`);
    const c = data.data;

    $('#firstName').value = c.first_name || '';
    $('#lastName').value = c.last_name || '';
    $('#email').value = c.email || '';
    $('#phone').value = c.phone || '';
    $('#dob').value = c.date_of_birth || '';
    $('#gender').value = c.gender || '';
    $('#employmentType').value = c.employment_type || '';
    $('#annualIncome').value = c.annual_income || '';
    $('#loanAmount').value = c.loan_amount || '';
    $('#creditScore').value = c.credit_score || '';
    $('#address').value = c.address || '';
    $('#city').value = c.city || '';
    $('#state').value = c.state || '';
    $('#country').value = c.country || '';
    $('#postalCode').value = c.postal_code || '';

    openModal();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

function resetForm() {
  els.form.reset();
  $$('.form-error').forEach(e => e.textContent = '');
}

// ── Delete Modal ───────────────────────────────────────────────────────────

function openDeleteModal(id, name) {
  deletingCustomerId = id;
  els.deleteCustomerName.textContent = name;
  els.deleteModal.classList.add('active');
  document.body.style.overflow = 'hidden';
}

function closeDeleteModal() {
  els.deleteModal.classList.remove('active');
  document.body.style.overflow = '';
  deletingCustomerId = null;
}

// ── Form Validation ────────────────────────────────────────────────────────

function validateForm() {
  let valid = true;
  $$('.form-error').forEach(e => e.textContent = '');

  const required = [
    { id: 'firstName', label: 'First name' },
    { id: 'lastName', label: 'Last name' },
    { id: 'email', label: 'Email' },
    { id: 'phone', label: 'Phone' },
    { id: 'dob', label: 'Date of birth' },
    { id: 'gender', label: 'Gender' },
    { id: 'employmentType', label: 'Employment type' },
    { id: 'annualIncome', label: 'Annual income' },
    { id: 'loanAmount', label: 'Loan amount' },
    { id: 'creditScore', label: 'Credit score' },
    { id: 'address', label: 'Address' },
    { id: 'city', label: 'City' },
    { id: 'state', label: 'State' },
    { id: 'country', label: 'Country' },
    { id: 'postalCode', label: 'Postal code' },
  ];

  for (const { id, label } of required) {
    const el = $(`#${id}`);
    if (!el.value.trim()) {
      $(`#${id}Error`).textContent = `${label} is required`;
      valid = false;
    }
  }

  // Email
  const email = $('#email').value.trim();
  if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    $('#emailError').textContent = 'Invalid email address';
    valid = false;
  }

  // Credit score range
  const cs = parseInt($('#creditScore').value);
  if (cs && (cs < 300 || cs > 900)) {
    $('#creditScoreError').textContent = 'Must be between 300 and 900';
    valid = false;
  }

  // Income > 0
  const income = parseFloat($('#annualIncome').value);
  if (income !== undefined && income <= 0) {
    $('#annualIncomeError').textContent = 'Must be greater than 0';
    valid = false;
  }

  // Loan > 0
  const loan = parseFloat($('#loanAmount').value);
  if (loan !== undefined && loan <= 0) {
    $('#loanAmountError').textContent = 'Must be greater than 0';
    valid = false;
  }

  // DOB not in future
  const dob = $('#dob').value;
  if (dob && new Date(dob) > new Date()) {
    $('#dobError').textContent = 'Cannot be in the future';
    valid = false;
  }

  return valid;
}

// ── Form Submission ────────────────────────────────────────────────────────

async function handleSave() {
  if (!validateForm()) return;

  const body = {
    first_name:      $('#firstName').value.trim(),
    last_name:       $('#lastName').value.trim(),
    email:           $('#email').value.trim(),
    phone:           $('#phone').value.trim(),
    date_of_birth:   $('#dob').value,
    gender:          $('#gender').value,
    employment_type: $('#employmentType').value,
    annual_income:   parseFloat($('#annualIncome').value),
    loan_amount:     parseFloat($('#loanAmount').value),
    credit_score:    parseInt($('#creditScore').value),
    address:         $('#address').value.trim(),
    city:            $('#city').value.trim(),
    state:           $('#state').value.trim(),
    country:         $('#country').value.trim(),
    postal_code:     $('#postalCode').value.trim(),
  };

  els.modalSaveText.style.display = 'none';
  els.modalSpinner.style.display = 'block';
  els.modalSave.disabled = true;

  try {
    if (editingCustomerId) {
      await apiPut(`${API_BASE}/${editingCustomerId}`, body);
      showToast('Customer updated successfully', 'success');
    } else {
      await apiPost(API_BASE, body);
      showToast('Customer created successfully', 'success');
    }
    closeModal();
    loadCustomers();
  } catch (err) {
    showToast(err.message, 'error');
  } finally {
    els.modalSaveText.style.display = '';
    els.modalSpinner.style.display = 'none';
    els.modalSave.disabled = false;
  }
}

// ── Delete Handling ────────────────────────────────────────────────────────

async function handleDelete() {
  if (!deletingCustomerId) return;

  els.deleteConfirmText.style.display = 'none';
  els.deleteSpinner.style.display = 'block';
  els.deleteConfirmBtn.disabled = true;

  try {
    await apiDelete(`${API_BASE}/${deletingCustomerId}`);
    showToast('Customer deleted successfully', 'success');
    closeDeleteModal();
    loadCustomers();
  } catch (err) {
    showToast(err.message, 'error');
  } finally {
    els.deleteConfirmText.style.display = '';
    els.deleteSpinner.style.display = 'none';
    els.deleteConfirmBtn.disabled = false;
  }
}

// ── Search ─────────────────────────────────────────────────────────────────

function handleSearch() {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    currentPage = 1;
    loadCustomers();
  }, 350);
}

// ── Event Listeners ────────────────────────────────────────────────────────

// Add customer
els.btnAdd.addEventListener('click', openCreateModal);
els.btnAddFirst.addEventListener('click', openCreateModal);

// Refresh
els.btnRefresh.addEventListener('click', () => {
  els.searchInput.value = '';
  currentPage = 1;
  loadCustomers();
});

// Search
els.searchInput.addEventListener('input', handleSearch);
els.searchField.addEventListener('change', () => {
  if (els.searchInput.value.trim()) {
    currentPage = 1;
    loadCustomers();
  }
});

// Customer modal
els.modalClose.addEventListener('click', closeModal);
els.modalCancel.addEventListener('click', closeModal);
els.modalSave.addEventListener('click', handleSave);
els.modal.addEventListener('click', (e) => {
  if (e.target === els.modal) closeModal();
});

// Delete modal
els.deleteModalClose.addEventListener('click', closeDeleteModal);
els.deleteCancelBtn.addEventListener('click', closeDeleteModal);
els.deleteConfirmBtn.addEventListener('click', handleDelete);
els.deleteModal.addEventListener('click', (e) => {
  if (e.target === els.deleteModal) closeDeleteModal();
});

// Keyboard: Escape to close modals
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    if (els.modal.classList.contains('active')) closeModal();
    if (els.deleteModal.classList.contains('active')) closeDeleteModal();
  }
});

// ── Initialize ─────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  loadCustomers();
});
