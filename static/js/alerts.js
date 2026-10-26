(function () {
  'use strict';

  const theme = {
    confirmButtonColor: '#f3df00',
    cancelButtonColor: '#ece8df'
  };

  function hasSwal() {
    return typeof window.Swal !== 'undefined' && typeof window.Swal.fire === 'function';
  }

  function normalizeIcon(level) {
    const value = String(level || 'info').toLowerCase();
    if (value.includes('error') || value.includes('danger')) return 'error';
    if (value.includes('warning')) return 'warning';
    if (value.includes('success')) return 'success';
    return 'info';
  }

  function alertBox(options) {
    const opts = Object.assign({
      icon: 'info',
      title: 'Informasi',
      text: '',
      confirmButtonText: 'OK'
    }, options || {});

    if (!hasSwal()) {
      window.alert([opts.title, opts.text].filter(Boolean).join('\n\n'));
      return Promise.resolve({ isConfirmed: true });
    }

    return window.Swal.fire({
      icon: opts.icon,
      title: opts.title,
      text: opts.text,
      html: opts.html,
      confirmButtonText: opts.confirmButtonText,
      confirmButtonColor: theme.confirmButtonColor,
      buttonsStyling: true,
      reverseButtons: true,
      heightAuto: false,
      customClass: {
        popup: 'sani-swal-popup',
        confirmButton: 'sani-swal-confirm'
      }
    });
  }

  function toast(message, level) {
    const icon = normalizeIcon(level);
    if (!hasSwal()) return Promise.resolve();
    return window.Swal.fire({
      toast: true,
      position: 'top-end',
      icon: icon,
      title: message,
      showConfirmButton: false,
      timer: icon === 'error' ? 4200 : 2600,
      timerProgressBar: true,
      heightAuto: false,
      customClass: { popup: 'sani-swal-toast' }
    });
  }

  function confirmBox(options) {
    const opts = Object.assign({
      icon: 'warning',
      title: 'Konfirmasi',
      text: 'Lanjutkan tindakan ini?',
      confirmButtonText: 'Ya, lanjutkan',
      cancelButtonText: 'Batal'
    }, options || {});

    if (!hasSwal()) {
      return Promise.resolve({ isConfirmed: window.confirm(opts.text) });
    }

    return window.Swal.fire({
      icon: opts.icon,
      title: opts.title,
      text: opts.text,
      showCancelButton: true,
      confirmButtonText: opts.confirmButtonText,
      cancelButtonText: opts.cancelButtonText,
      confirmButtonColor: theme.confirmButtonColor,
      cancelButtonColor: theme.cancelButtonColor,
      color: '#24211f',
      reverseButtons: true,
      focusCancel: true,
      heightAuto: false,
      customClass: {
        popup: 'sani-swal-popup',
        confirmButton: 'sani-swal-confirm',
        cancelButton: 'sani-swal-cancel'
      }
    });
  }

  window.SaniUI = {
    alert: alertBox,
    toast: toast,
    confirm: confirmBox
  };

  function labelFor(field) {
    if (!field) return 'Kolom';
    if (field.id) {
      const label = Array.from(document.getElementsByTagName('label')).find(function (item) { return item.htmlFor === field.id; });
      if (label) return label.textContent.replace(/opsional/gi, '').trim();
    }
    return field.getAttribute('aria-label') || field.name || 'Kolom';
  }

  function friendlyValidation(field) {
    const label = labelFor(field);
    const validity = field.validity || {};
    if (validity.valueMissing) return label + ' wajib diisi.';
    if (validity.tooShort) return label + ' terlalu pendek.';
    if (validity.tooLong) return label + ' terlalu panjang.';
    if (validity.rangeUnderflow) return label + ' minimal ' + field.min + '.';
    if (validity.rangeOverflow) return label + ' maksimal ' + field.max + '.';
    if (validity.typeMismatch) return 'Format ' + label.toLowerCase() + ' belum benar.';
    if (validity.patternMismatch) return 'Format ' + label.toLowerCase() + ' belum sesuai.';
    if (validity.stepMismatch) return 'Nilai ' + label.toLowerCase() + ' belum sesuai.';
    return field.validationMessage || ('Periksa kembali ' + label.toLowerCase() + '.');
  }

  function firstNativeError(form) {
    const fields = Array.from(form.elements || []).filter(function (field) {
      return field && typeof field.checkValidity === 'function' && !field.disabled && field.type !== 'hidden' && field.type !== 'submit' && field.type !== 'button';
    });
    for (const field of fields) {
      if (!field.checkValidity()) return { field: field, message: friendlyValidation(field) };
    }
    return null;
  }

  function customFormError(form) {
    if (form.matches('[data-customer-flow]')) {
      const mode = form.querySelector('input[name="mode_pelanggan"]:checked');
      const modeValue = mode ? mode.value : 'lama';
      if (modeValue === 'lama') {
        const customer = form.querySelector('select[name="pelanggan"]');
        if (customer && !customer.value) {
          return { field: customer, message: 'Pilih pelanggan yang sudah tersimpan.' };
        }
      } else {
        const name = form.querySelector('input[name="nama_baru"]');
        if (name && !name.value.trim()) {
          return { field: name, message: 'Nama pelanggan baru wajib diisi.' };
        }
      }

      const weight = form.querySelector('[data-weight-input]');
      if (weight) {
        const numeric = Number(String(weight.value || '').trim().replace(',', '.'));
        if (!Number.isFinite(numeric) || numeric <= 0) {
          return { field: weight, message: 'Berat cucian harus lebih dari 0 kg.' };
        }
        const parts = String(weight.value || '').replace('.', ',').split(',');
        if (parts[1] && parts[1].length > 3) {
          return { field: weight, message: 'Berat cucian maksimal 3 angka di belakang koma.' };
        }
      }
    }

    if (form.matches('[data-simple-item-form]')) {
      const name = form.querySelector('[data-simple-item-name]');
      const qty = form.querySelector('[data-simple-item-qty]');
      if (!name || name.value.trim().length < 2) {
        return { field: name, message: 'Isi jenis pakaian minimal 2 karakter.' };
      }
      const value = qty ? parseInt(qty.value || '0', 10) : 0;
      if (!Number.isFinite(value) || value < 1 || value > 99) {
        return { field: qty, message: 'Jumlah pakaian harus antara 1 sampai 99.' };
      }
    }

    return null;
  }

  async function showValidationError(error) {
    if (!error) return;
    await alertBox({
      icon: 'warning',
      title: 'Periksa input',
      text: error.message,
      confirmButtonText: 'Perbaiki'
    });
    if (error.field && typeof error.field.focus === 'function') {
      error.field.focus({ preventScroll: false });
      if (typeof error.field.scrollIntoView === 'function') {
        error.field.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }
  }

  // Satu pintu untuk validasi dan konfirmasi semua form POST.
  document.addEventListener('submit', function (event) {
    const form = event.target;
    if (!(form instanceof HTMLFormElement)) return;

    if (form.dataset.saniBypass === '1') {
      delete form.dataset.saniBypass;
      return;
    }

    const method = String(form.method || 'get').toLowerCase();
    if (method === 'post' && !form.hasAttribute('data-skip-swal-validation')) {
      const customError = customFormError(form);
      const nativeError = customError || firstNativeError(form);
      if (nativeError) {
        event.preventDefault();
        event.stopImmediatePropagation();
        showValidationError(nativeError);
        return;
      }
    }

    if (form.hasAttribute('data-confirm')) {
      event.preventDefault();
      event.stopImmediatePropagation();
      const submitter = event.submitter || null;
      const text = form.getAttribute('data-confirm') || 'Lanjutkan tindakan ini?';
      const title = form.getAttribute('data-confirm-title') || 'Konfirmasi';
      const okText = form.getAttribute('data-confirm-ok') || 'Ya, lanjutkan';
      const cancelText = form.getAttribute('data-confirm-cancel') || 'Batal';
      const icon = form.getAttribute('data-confirm-icon') || 'warning';

      confirmBox({ icon: icon, title: title, text: text, confirmButtonText: okText, cancelButtonText: cancelText })
        .then(function (result) {
          if (!result.isConfirmed) return;
          form.dataset.saniBypass = '1';
          if (typeof form.requestSubmit === 'function') form.requestSubmit(submitter || undefined);
          else HTMLFormElement.prototype.submit.call(form);
        });
    }
  }, true);

  function collectServerErrors() {
    const nodes = Array.from(document.querySelectorAll('.field-error, .alert-error'));
    const seen = new Set();
    const messages = [];
    nodes.forEach(function (node) {
      if (node.closest('.messages')) return;
      const text = (node.textContent || '').replace(/\s+/g, ' ').trim();
      if (text && !seen.has(text)) {
        seen.add(text);
        messages.push(text);
      }
      if (hasSwal() && node.classList.contains('alert-error')) {
        node.style.display = 'none';
      }
    });
    return messages;
  }

  async function showDjangoMessages() {
    const messages = Array.from(document.querySelectorAll('.messages [data-alert]'));
    if (hasSwal()) {
      for (const node of messages) {
        const text = (node.textContent || '').replace('×', '').replace(/\s+/g, ' ').trim();
        const icon = normalizeIcon(node.className);
        node.remove();
        if (!text) continue;
        if (icon === 'success') await toast(text, 'success');
        else await alertBox({ icon: icon, title: icon === 'error' ? 'Tidak berhasil' : 'Informasi', text: text });
      }
    }

    const formErrors = collectServerErrors();
    if (formErrors.length) {
      await alertBox({
        icon: 'error',
        title: 'Periksa input',
        text: formErrors.slice(0, 6).map(function (text) { return '• ' + text; }).join('\n')
      });
    }
  }

  let deferredInstallPrompt = null;

  function isStandalone() {
    return window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone === true;
  }

  function isIOS() {
    return /iphone|ipad|ipod/i.test(window.navigator.userAgent || '');
  }

  function refreshInstallButtons() {
    const installed = isStandalone();
    document.querySelectorAll('[data-install-app]').forEach(function (button) {
      button.hidden = installed;
      if (!installed) button.classList.add('is-ready');
    });
  }

  window.addEventListener('beforeinstallprompt', function (event) {
    event.preventDefault();
    deferredInstallPrompt = event;
    refreshInstallButtons();
  });

  window.addEventListener('appinstalled', function () {
    deferredInstallPrompt = null;
    refreshInstallButtons();
    toast('Sani Laundry berhasil dipasang sebagai aplikasi.', 'success');
  });

  document.addEventListener('click', async function (event) {
    const button = event.target.closest('[data-install-app]');
    if (!button) return;
    event.preventDefault();

    if (isStandalone()) {
      await alertBox({ icon: 'success', title: 'Sudah terpasang', text: 'Sani Laundry sedang berjalan sebagai aplikasi.' });
      return;
    }

    if (deferredInstallPrompt) {
      deferredInstallPrompt.prompt();
      const choice = await deferredInstallPrompt.userChoice;
      if (choice && choice.outcome === 'accepted') {
        await toast('Pemasangan aplikasi dimulai.', 'success');
      }
      deferredInstallPrompt = null;
      return;
    }

    if (isIOS()) {
      await alertBox({
        icon: 'info',
        title: 'Pasang di iPhone / iPad',
        text: 'Buka di Safari, tekan tombol Bagikan, lalu pilih “Tambahkan ke Layar Utama”.'
      });
      return;
    }

    await alertBox({
      icon: 'info',
      title: 'Pasang aplikasi',
      text: 'Buka menu browser lalu pilih “Install app” atau “Tambahkan ke layar utama”. Gunakan HTTPS agar pemasangan tersedia.'
    });
  });

  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('form[method="post"], form[method="POST"]').forEach(function (form) {
      form.setAttribute('novalidate', 'novalidate');
    });

    showDjangoMessages();
    refreshInstallButtons();

    if ('serviceWorker' in navigator && (window.isSecureContext || location.hostname === 'localhost' || location.hostname === '127.0.0.1')) {
      let reloadingForWorker = false;
      navigator.serviceWorker.addEventListener('controllerchange', function () {
        if (reloadingForWorker) return;
        reloadingForWorker = true;
        // Muat ulang sekali ketika service worker baru mengambil alih supaya CSS/JS
        // terbaru langsung dipakai tanpa pengguna harus membersihkan cache manual.
        window.location.reload();
      });

      navigator.serviceWorker.register('/service-worker.js', { scope: '/' })
        .then(function (registration) { return registration.update(); })
        .catch(function (error) {
          console.warn('Service worker Sani Laundry tidak dapat didaftarkan:', error);
        });
    }

    window.addEventListener('offline', function () {
      toast('Koneksi internet terputus. Penyimpanan data memerlukan server.', 'warning');
    });
    window.addEventListener('online', function () {
      toast('Koneksi kembali tersedia.', 'success');
    });
  });
})();
