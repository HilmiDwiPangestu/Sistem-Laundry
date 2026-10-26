(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', function () {
    const body = document.body;
    const sidebar = document.querySelector('#app-sidebar');
    const openButton = document.querySelector('[data-sidebar-open]');
    const closeButton = document.querySelector('[data-sidebar-close]');
    const overlay = document.querySelector('[data-sidebar-overlay]');

    function openSidebar() {
      if (!sidebar) return;
      body.classList.add('sidebar-open');
      if (openButton) openButton.setAttribute('aria-expanded', 'true');
    }
    function closeSidebar() {
      body.classList.remove('sidebar-open');
      if (openButton) openButton.setAttribute('aria-expanded', 'false');
    }
    if (openButton) openButton.addEventListener('click', openSidebar);
    if (closeButton) closeButton.addEventListener('click', closeSidebar);
    if (overlay) overlay.addEventListener('click', closeSidebar);
    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape') closeSidebar();
    });

    document.querySelectorAll('[data-alert-close]').forEach(function (button) {
      button.addEventListener('click', function () {
        const alert = button.closest('[data-alert]');
        if (alert) alert.remove();
      });
    });

    const transactionForm = document.querySelector('[data-customer-flow]');
    if (transactionForm) {
      const modeInputs = transactionForm.querySelectorAll('input[name="mode_pelanggan"]');
      const oldBox = transactionForm.querySelector('[data-customer-old]');
      const newBox = transactionForm.querySelector('[data-customer-new]');
      const customerSelect = transactionForm.querySelector('select[name="pelanggan"]');
      const filterInput = transactionForm.querySelector('#customer-filter');
      const newNameInput = transactionForm.querySelector('input[name="nama_baru"]');

      function refreshMode() {
        const checked = transactionForm.querySelector('input[name="mode_pelanggan"]:checked');
        const mode = checked ? checked.value : 'lama';
        if (oldBox) oldBox.hidden = mode !== 'lama';
        if (newBox) newBox.hidden = mode !== 'baru';
      }

      modeInputs.forEach(function (input) {
        input.addEventListener('change', function () {
          refreshMode();
          if (input.checked && input.value === 'baru' && newNameInput) {
            window.setTimeout(function () { newNameInput.focus(); }, 30);
          }
          if (input.checked && input.value === 'lama' && filterInput) {
            window.setTimeout(function () { filterInput.focus(); }, 30);
          }
        });
      });
      refreshMode();

      if (filterInput && customerSelect) {
        const originalOptions = Array.from(customerSelect.options).map(function (option) {
          return { value: option.value, text: option.text };
        });
        filterInput.addEventListener('input', function () {
          const term = filterInput.value.trim().toLowerCase();
          const selectedValue = customerSelect.value;
          customerSelect.innerHTML = '';
          originalOptions.forEach(function (data, index) {
            if (index === 0 || !term || data.text.toLowerCase().includes(term)) {
              const option = document.createElement('option');
              option.value = data.value;
              option.textContent = data.text;
              option.selected = data.value === selectedValue;
              customerSelect.appendChild(option);
            }
          });
        });
      }
    }

    function rupiah(value) {
      return new Intl.NumberFormat('id-ID', {
        style: 'currency',
        currency: 'IDR',
        maximumFractionDigits: 0
      }).format(Number(value || 0));
    }

    function roundToThousand(value) {
      const numeric = Number(value || 0);
      const base = Math.floor(numeric / 1000) * 1000;
      const remainder = numeric - base;
      return remainder > 500 ? base + 1000 : base;
    }

    function normalizeWeightValue(value) {
      const raw = String(value == null ? '' : value).trim().replace(/\s+/g, '');
      if (!raw) return '';
      return raw.replace(',', '.');
    }

    function sanitizeWeightInput(value) {
      let raw = String(value == null ? '' : value).replace(/\s+/g, '');
      raw = raw.replace(/[^0-9.,]/g, '');

      const separatorIndex = raw.search(/[.,]/);
      if (separatorIndex === -1) return raw.replace(/^0+(?=\d)/, '') || '0';

      let integerPart = raw.slice(0, separatorIndex).replace(/[.,]/g, '');
      let decimalPart = raw.slice(separatorIndex + 1).replace(/[.,]/g, '').slice(0, 3);
      const separator = raw.charAt(separatorIndex) === '.' ? '.' : ',';

      integerPart = integerPart.replace(/^0+(?=\d)/, '') || '0';
      return integerPart + separator + decimalPart;
    }

    document.querySelectorAll('[data-weight-input]').forEach(function (input) {
      // Text input + inputmode decimal works more consistently on Android and iOS
      // and lets Indonesian users type either comma or dot.
      (function formatInitialWeight() {
        let value = String(input.value || '').replace('.', ',');
        if (value.includes(',')) {
          value = value.replace(/0+$/, '').replace(/,$/, '');
        }
        input.value = value;
      })();

      input.addEventListener('input', function () {
        const clean = sanitizeWeightInput(input.value);
        if (clean !== input.value) input.value = clean;
      });

      input.addEventListener('blur', function () {
        let clean = sanitizeWeightInput(input.value).replace('.', ',');
        clean = clean.replace(/,$/, '');
        input.value = clean;
      });
    });

    document.querySelectorAll('[data-price-form]').forEach(function (form) {
      const priceDataEl = form.querySelector('#harga-layanan-data') || document.querySelector('#harga-layanan-data');
      const calculator = form.querySelector('[data-price-calculator]');
      const weightInput = form.querySelector('[data-price-weight]');
      const kindSelect = form.querySelector('[data-price-kind]');
      const speedSelect = form.querySelector('[data-price-speed]');
      const serviceButtons = form.querySelectorAll('[data-service-choice]');
      const speedButtons = form.querySelectorAll('[data-speed-choice]');
      const serviceName = form.querySelector('[data-service-name]');
      if (!priceDataEl || !calculator || !weightInput || !kindSelect || !speedSelect) return;

      let prices = {};
      try { prices = JSON.parse(priceDataEl.textContent || '{}'); } catch (error) { prices = {}; }

      const formula = calculator.querySelector('[data-price-formula]');
      const rounding = calculator.querySelector('[data-price-rounding]');
      const total = calculator.querySelector('[data-price-total]');
      const rateText = calculator.querySelector('[data-price-rate]');

      function activeRate() {
        if (speedSelect.value === 'express') return Number(prices.express || 0);
        const mapping = {
          cs: 'reguler_cuci_setrika',
          c: 'reguler_cuci_lipat',
          s: 'reguler_setrika'
        };
        return Number(prices[mapping[kindSelect.value]] || 0);
      }

      function currentServiceLabel() {
        const labels = { cs: 'Cuci Setrika', c: 'Cuci Lipat', s: 'Setrika Saja' };
        const kindLabel = labels[kindSelect.value] || 'Belum dipilih';
        const speedLabel = speedSelect.value === 'express' ? 'Express' : 'Reguler';
        return kindLabel + ' · ' + speedLabel;
      }

      function syncServiceButtons() {
        serviceButtons.forEach(function (button) {
          const buttonKind = button.getAttribute('data-kind');
          const active = buttonKind === kindSelect.value;
          button.classList.toggle('active', active);
          button.setAttribute('aria-pressed', active ? 'true' : 'false');
          const priceNode = button.querySelector('[data-choice-price]');
          const speedLabelNode = button.querySelector('[data-choice-speed-label]');
          const chosenPrice = speedSelect.value === 'express'
            ? button.getAttribute('data-price-express')
            : button.getAttribute('data-price-reguler');
          if (priceNode && chosenPrice !== null) priceNode.textContent = rupiah(Number(chosenPrice));
          if (speedLabelNode) speedLabelNode.textContent = speedSelect.value === 'express' ? 'Tarif Express' : 'Tarif reguler';
        });
        if (serviceName) serviceName.textContent = currentServiceLabel();
        speedButtons.forEach(function (button) {
          const active = button.getAttribute('data-speed-choice') === speedSelect.value;
          button.classList.toggle('active', active);
          button.setAttribute('aria-pressed', active ? 'true' : 'false');
        });
      }

      function renderPrice() {
        const weight = Number(normalizeWeightValue(weightInput.value));
        const rate = activeRate();
        const raw = weight > 0 && rate > 0 ? weight * rate : 0;
        const rounded = roundToThousand(raw);

        syncServiceButtons();
        if (rateText) rateText.textContent = rate > 0 ? 'Tarif ' + rupiah(rate) + '/kg' : 'Tarif belum tersedia';
        if (total) total.textContent = rupiah(rounded);

        if (!weight || weight <= 0) {
          if (formula) formula.textContent = 'Isi berat untuk menghitung.';
          if (rounding) rounding.textContent = 'Pembulatan otomatis ke ribuan sesuai aturan.';
          return;
        }

        if (formula) formula.textContent = weight.toLocaleString('id-ID') + ' kg × ' + rupiah(rate) + ' = ' + rupiah(raw);
        if (rounding) {
          rounding.textContent = raw === rounded
            ? 'Total sudah tepat pada kelipatan Rp1.000.'
            : rupiah(raw) + ' dibulatkan menjadi ' + rupiah(rounded) + '.';
        }
      }

      serviceButtons.forEach(function (button) {
        button.addEventListener('click', function () {
          kindSelect.value = button.getAttribute('data-kind') || 'cs';
          kindSelect.dispatchEvent(new Event('change', { bubbles: true }));
          weightInput.focus();
        });
      });
      speedButtons.forEach(function (button) {
        button.addEventListener('click', function () {
          speedSelect.value = button.getAttribute('data-speed-choice') || 'reguler';
          speedSelect.dispatchEvent(new Event('change', { bubbles: true }));
          weightInput.focus();
        });
      });

      [weightInput, kindSelect, speedSelect].forEach(function (field) {
        field.addEventListener('input', renderPrice);
        field.addEventListener('change', renderPrice);
      });
      renderPrice();
    });


    // v32: keranjang input pakaian. Beberapa jenis dan jumlah disimpan
    // dalam satu POST agar kasir tidak perlu mengirim satu item per klik.
    document.querySelectorAll('[data-clothing-cart-form]').forEach(function (form) {
      const root = form.closest('[data-clothing-cart]');
      const payloadInput = form.querySelector('[data-cart-payload]');
      const list = form.querySelector('[data-cart-list]');
      const searchInput = form.querySelector('[data-cart-search]');
      const searchOptions = Array.from(form.querySelectorAll('[data-cart-search-option]'));
      const addButtons = Array.from(form.querySelectorAll('[data-cart-add]'));
      const customButton = form.querySelector('[data-cart-custom-add]');
      const customLabel = form.querySelector('[data-cart-custom-label]');
      const searchEmpty = form.querySelector('[data-cart-search-empty]');
      const clearButton = form.querySelector('[data-cart-clear]');
      const submitButton = form.querySelector('[data-cart-submit]');
      const cart = new Map();

      function normalize(value) {
        return String(value || '').trim().replace(/\s+/g, ' ').toLocaleLowerCase('id-ID');
      }

      function clampQty(value) {
        const parsed = parseInt(value, 10);
        if (!Number.isFinite(parsed)) return 1;
        return Math.min(99, Math.max(1, parsed));
      }

      function makeButton(text, className, action, key) {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = className;
        button.dataset.cartAction = action;
        button.dataset.cartKey = key;
        button.textContent = text;
        return button;
      }

      function renderChoiceButtons() {
        addButtons.forEach(function (button) {
          const key = normalize(button.dataset.value || button.dataset.label);
          const item = cart.get(key);
          const count = button.querySelector('[data-cart-choice-count]');
          button.classList.toggle('is-in-cart', Boolean(item));
          if (count) count.textContent = item ? '✓ Di keranjang · ' + item.jumlah : '＋ Tambah';
          button.setAttribute('aria-pressed', item ? 'true' : 'false');
        });
      }

      function syncPayload() {
        if (!payloadInput) return;
        payloadInput.value = JSON.stringify(Array.from(cart.values()).map(function (item) {
          return { jenis: item.jenis, jumlah: item.jumlah, catatan: item.catatan || '' };
        }));
      }

      function renderCart() {
        if (!root || !list) return;
        const items = Array.from(cart.entries());
        const total = items.reduce(function (sum, entry) { return sum + entry[1].jumlah; }, 0);

        root.querySelectorAll('[data-cart-kind-count]').forEach(function (el) {
          el.textContent = String(items.length);
        });
        root.querySelectorAll('[data-cart-total]').forEach(function (el) {
          el.textContent = String(total);
        });

        syncPayload();
        if (clearButton) clearButton.disabled = items.length === 0;
        if (submitButton) {
          submitButton.disabled = items.length === 0;
          submitButton.textContent = items.length
            ? 'Simpan ' + items.length + ' jenis ke nota'
            : 'Simpan semua ke nota';
        }

        list.replaceChildren();
        if (!items.length) {
          const empty = document.createElement('div');
          empty.className = 'clothing-cart-empty';
          const icon = document.createElement('span');
          icon.setAttribute('aria-hidden', 'true');
          icon.textContent = '＋';
          const title = document.createElement('strong');
          title.textContent = 'Keranjang masih kosong';
          const note = document.createElement('small');
          note.textContent = 'Pilih satu atau beberapa jenis pakaian di sebelah kiri.';
          empty.append(icon, title, note);
          list.appendChild(empty);
        } else {
          items.forEach(function (entry) {
            const key = entry[0];
            const item = entry[1];
            const row = document.createElement('div');
            row.className = 'clothing-cart-row';

            const copy = document.createElement('div');
            copy.className = 'clothing-cart-row-copy';
            const name = document.createElement('strong');
            name.textContent = item.label;
            copy.appendChild(name);
            if (item.custom) {
              const badge = document.createElement('small');
              badge.textContent = 'Jenis baru';
              copy.appendChild(badge);
            }

            const noteDetails = document.createElement('details');
            noteDetails.className = 'clothing-cart-note';
            if (item.catatan) noteDetails.open = true;
            const noteSummary = document.createElement('summary');
            noteSummary.textContent = item.catatan ? 'Edit catatan item' : '+ Catatan (opsional)';
            const noteInput = document.createElement('input');
            noteInput.type = 'text';
            noteInput.maxLength = 200;
            noteInput.className = 'form-control';
            noteInput.placeholder = 'Contoh: noda tinta, luntur, jangan disikat';
            noteInput.value = item.catatan || '';
            noteInput.dataset.cartNoteKey = key;
            noteInput.setAttribute('aria-label', 'Catatan untuk ' + item.label);
            noteDetails.append(noteSummary, noteInput);

            const controls = document.createElement('div');
            controls.className = 'clothing-cart-row-controls';
            const minus = makeButton('−', 'clothing-cart-qty-btn', 'minus', key);
            minus.setAttribute('aria-label', 'Kurangi ' + item.label);
            minus.disabled = item.jumlah <= 1;
            const qty = document.createElement('input');
            qty.type = 'number';
            qty.className = 'clothing-cart-qty-input';
            qty.min = '1';
            qty.max = '99';
            qty.step = '1';
            qty.inputMode = 'numeric';
            qty.value = String(item.jumlah);
            qty.dataset.cartQtyKey = key;
            qty.setAttribute('aria-label', 'Jumlah ' + item.label);
            const plus = makeButton('+', 'clothing-cart-qty-btn', 'plus', key);
            plus.setAttribute('aria-label', 'Tambah ' + item.label);
            plus.disabled = item.jumlah >= 99;
            const remove = makeButton('Hapus', 'clothing-cart-remove', 'remove', key);
            remove.setAttribute('aria-label', 'Hapus ' + item.label + ' dari keranjang');
            controls.append(minus, qty, plus, remove);
            row.append(copy, controls, noteDetails);
            list.appendChild(row);
          });
        }
        renderChoiceButtons();
      }

      function addItem(value, label, custom) {
        const jenis = String(value || '').trim().replace(/\s+/g, ' ');
        const display = String(label || jenis).trim().replace(/\s+/g, ' ');
        if (jenis.length < 2 || jenis.length > 100) return;
        const key = normalize(jenis);
        const existing = cart.get(key);
        if (existing) {
          if (existing.jumlah < 99) existing.jumlah += 1;
        } else {
          cart.set(key, { jenis: jenis, label: display || jenis, jumlah: 1, catatan: '', custom: Boolean(custom) });
        }
        renderCart();
      }

      function filterSearchOptions() {
        if (!searchInput) return;
        const query = normalize(searchInput.value);
        let visible = 0;
        let exact = false;
        searchOptions.forEach(function (button) {
          const value = normalize(button.dataset.value);
          const label = normalize(button.dataset.label);
          const matches = !query || value.includes(query) || label.includes(query);
          button.classList.toggle('is-hidden', !matches);
          if (matches) visible += 1;
          if (query && (value === query || label === query)) exact = true;
        });
        if (searchEmpty) searchEmpty.classList.toggle('is-hidden', !query || visible > 0);
        if (customButton) customButton.classList.toggle('is-hidden', query.length < 2 || exact);
        if (customLabel) customLabel.textContent = searchInput.value.trim();
      }

      form.addEventListener('click', function (event) {
        const addButton = event.target.closest('[data-cart-add]');
        if (addButton && form.contains(addButton)) {
          event.preventDefault();
          addItem(addButton.dataset.value, addButton.dataset.label, false);
          return;
        }

        const custom = event.target.closest('[data-cart-custom-add]');
        if (custom && form.contains(custom)) {
          event.preventDefault();
          const value = searchInput ? searchInput.value.trim().replace(/\s+/g, ' ') : '';
          if (value.length >= 2 && value.length <= 100) {
            addItem(value, value, true);
            searchInput.value = '';
            filterSearchOptions();
          }
          return;
        }

        const actionButton = event.target.closest('[data-cart-action]');
        if (actionButton && form.contains(actionButton)) {
          const key = actionButton.dataset.cartKey;
          const item = cart.get(key);
          if (!item) return;
          if (actionButton.dataset.cartAction === 'plus' && item.jumlah < 99) item.jumlah += 1;
          else if (actionButton.dataset.cartAction === 'minus' && item.jumlah > 1) item.jumlah -= 1;
          else if (actionButton.dataset.cartAction === 'remove') cart.delete(key);
          renderCart();
        }
      });

      if (list) {
        list.addEventListener('change', function (event) {
          const input = event.target.closest('[data-cart-qty-key]');
          if (!input) return;
          const item = cart.get(input.dataset.cartQtyKey);
          if (!item) return;
          item.jumlah = clampQty(input.value);
          renderCart();
        });
        list.addEventListener('input', function (event) {
          const input = event.target.closest('[data-cart-note-key]');
          if (!input) return;
          const item = cart.get(input.dataset.cartNoteKey);
          if (!item) return;
          item.catatan = input.value.slice(0, 200);
          const summary = input.closest('details') ? input.closest('details').querySelector('summary') : null;
          if (summary) summary.textContent = item.catatan ? 'Edit catatan item' : '+ Catatan (opsional)';
          syncPayload();
        });
      }

      if (searchInput) {
        searchInput.addEventListener('input', filterSearchOptions);
        filterSearchOptions();
      }
      if (clearButton) {
        clearButton.addEventListener('click', function () {
          cart.clear();
          renderCart();
        });
      }
      form.addEventListener('submit', function (event) {
        if (!cart.size) {
          event.preventDefault();
          if (window.SaniUI) {
            window.SaniUI.alert({
              icon: 'warning',
              title: 'Keranjang masih kosong',
              text: 'Pilih setidaknya satu jenis pakaian sebelum menyimpan.',
              confirmButtonText: 'Pilih pakaian'
            });
          }
          return;
        }
        syncPayload();
      });
      renderCart();
    });

    // v14: ubah jumlah item langsung tanpa reload halaman.
    // Jika fetch gagal, form tetap dikirim secara normal sebagai fallback.
    document.querySelectorAll('[data-item-qty-form]').forEach(function (form) {
      form.addEventListener('submit', async function (event) {
        if (!window.fetch) return;
        event.preventDefault();

        const row = form.closest('[data-item-row]');
        if (!row || form.dataset.busy === '1') return;

        const controls = row.querySelectorAll('.item-qty-btn');
        form.dataset.busy = '1';
        row.classList.add('is-updating');
        controls.forEach(function (button) { button.disabled = true; });

        try {
          const response = await fetch(form.action, {
            method: 'POST',
            body: new FormData(form),
            headers: {
              'X-Requested-With': 'XMLHttpRequest',
              'Accept': 'application/json'
            },
            credentials: 'same-origin'
          });

          if (!response.ok) throw new Error('Request gagal');
          const data = await response.json();
          if (!data || !data.ok) throw new Error((data && data.message) || 'Request gagal');

          if (data.deleted) {
            row.remove();
          } else {
            const qtyValue = row.querySelector('[data-item-qty-value]');
            if (qtyValue) {
              qtyValue.textContent = String(data.quantity);
              qtyValue.setAttribute('aria-label', 'Jumlah saat ini ' + data.quantity);
              qtyValue.classList.remove('qty-pop');
              void qtyValue.offsetWidth;
              qtyValue.classList.add('qty-pop');
            }
          }

          document.querySelectorAll('[data-items-total]').forEach(function (el) {
            el.textContent = String(data.total_item);
          });
          document.querySelectorAll('[data-items-kind-count]').forEach(function (el) {
            el.textContent = String(data.jenis_count);
          });

          const emptyState = document.querySelector('[data-item-empty]');
          const totalRow = document.querySelector('[data-item-total-row]');
          const help = document.querySelector('[data-item-list-help]');
          const isEmpty = Number(data.jenis_count) === 0;
          if (emptyState) emptyState.classList.toggle('is-hidden', !isEmpty);
          if (totalRow) totalRow.classList.toggle('is-hidden', isEmpty);
          if (help) help.classList.toggle('is-hidden', isEmpty);

          // Struk ketiga hanya tersedia selama nota masih mempunyai rincian pakaian.
          document.querySelectorAll('[data-item-receipt-action]').forEach(function (el) {
            el.classList.toggle('is-hidden', isEmpty);
          });
          document.querySelectorAll('[data-receipt-count]').forEach(function (el) {
            el.textContent = isEmpty ? '2' : '3';
          });
        } catch (error) {
          // Fallback aman: kirim form biasa agar fungsi tetap jalan bila AJAX diblokir.
          HTMLFormElement.prototype.submit.call(form);
          return;
        } finally {
          if (document.body.contains(row)) {
            form.dataset.busy = '0';
            row.classList.remove('is-updating');
            controls.forEach(function (button) { button.disabled = false; });
          }
        }
      });
    });

    document.querySelectorAll('[data-print]').forEach(function (button) {
      button.addEventListener('click', function () { window.print(); });
    });

    document.querySelectorAll('[data-password-toggle]').forEach(function (button) {
      button.addEventListener('click', function () {
        const wrap = button.closest('.password-wrap');
        const input = wrap ? wrap.querySelector('input') : null;
        if (!input) return;
        const showing = input.type === 'text';
        input.type = showing ? 'password' : 'text';
        button.textContent = showing ? 'Lihat' : 'Sembunyikan';
        button.setAttribute('aria-label', showing ? 'Tampilkan password' : 'Sembunyikan password');
      });
    });
  });
})();
