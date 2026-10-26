(function () {
  'use strict';

  const BRIDGE_URL = 'http://127.0.0.1:17891';
  const TOKEN_KEY = 'saniLaundryPrinterBridgeToken';
  const PRINTER_KEY = 'saniLaundryPrinterBridgeName';
  const SERVICE_UUIDS = [
    '0000ff00-0000-1000-8000-00805f9b34fb',
    '0000ffe0-0000-1000-8000-00805f9b34fb',
    '0000ae00-0000-1000-8000-00805f9b34fb',
    '000018f0-0000-1000-8000-00805f9b34fb',
    '0000fff0-0000-1000-8000-00805f9b34fb',
    '0000ff10-0000-1000-8000-00805f9b34fb',
    '49535343-fe7d-4ae5-8fa9-9fafd205e455'
  ];

  function byData(name, root) {
    return (root || document).querySelector('[data-' + name + ']');
  }

  function getStoredToken() {
    try { return localStorage.getItem(TOKEN_KEY) || ''; } catch (_) { return ''; }
  }

  function getStoredPrinter() {
    try { return localStorage.getItem(PRINTER_KEY) || ''; } catch (_) { return ''; }
  }

  function setStatus(message, type) {
    const targets = document.querySelectorAll('[data-print-status]');
    targets.forEach(function (target) {
      target.textContent = message;
      target.dataset.statusType = type || 'info';
      target.hidden = !message;
    });
    if (!targets.length && message) window.alert(message);
  }

  function cleanText(value) {
    return String(value || '')
      .replace(/\u00a0/g, ' ')
      .replace(/[·•]/g, '-')
      .replace(/[–—]/g, '-')
      .replace(/×/g, 'x')
      .replace(/[“”]/g, '"')
      .replace(/[‘’]/g, "'")
      .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
      .replace(/[^\x20-\x7E\n\r\t]/g, ' ')
      .replace(/[ \t]+/g, ' ')
      .trim();
  }

  function splitWrap(text, width) {
    const cleaned = cleanText(text);
    if (!cleaned) return [''];
    const output = [];
    cleaned.split(/\s+/).forEach(function (word) {
      let remaining = word;
      while (remaining.length > width) {
        output.push(remaining.slice(0, width));
        remaining = remaining.slice(width);
      }
      if (!remaining) return;
      const current = output.length ? output[output.length - 1] : '';
      if (current && current.length + 1 + remaining.length <= width && !current.includes('\n')) {
        output[output.length - 1] = current + ' ' + remaining;
      } else {
        output.push(remaining);
      }
    });
    return output;
  }

  function nodeText(node) {
    return node ? cleanText(node.innerText || node.textContent || '') : '';
  }

  function addWrapped(lines, text, width, centered) {
    splitWrap(text, width).forEach(function (line) {
      lines.push({ text: line, center: !!centered });
    });
  }

  function extractReceiptLines(receipt, width) {
    const lines = [];
    const brand = receipt.querySelector('.thermal-brand');
    if (brand) {
      const name = nodeText(brand.querySelector('h1'));
      if (name) addWrapped(lines, name.toUpperCase(), width, true);
      Array.from(brand.querySelectorAll('p')).forEach(function (node) {
        const text = nodeText(node);
        if (text) addWrapped(lines, text, width, true);
      });
      lines.push({ text: '', center: true });
    }

    const title = receipt.querySelector('.receipt-title');
    if (title) {
      Array.from(title.querySelectorAll('strong, span')).forEach(function (node) {
        const text = nodeText(node);
        if (text) addWrapped(lines, text.toUpperCase(), width, true);
      });
      lines.push({ text: '', center: false });
    }

    Array.from(receipt.querySelectorAll('.receipt-section')).forEach(function (section) {
      const heading = nodeText(section.querySelector('h2'));
      if (heading) addWrapped(lines, heading.toUpperCase(), width, false);

      section.querySelectorAll('.receipt-detail-list > div').forEach(function (row) {
        const label = nodeText(row.querySelector('dt'));
        const value = nodeText(row.querySelector('dd'));
        if (label || value) addWrapped(lines, (label ? label + ': ' : '') + value, width, false);
      });

      section.querySelectorAll('.thermal-grand-total').forEach(function (row) {
        const label = nodeText(row.querySelector('span')) || 'TOTAL';
        const value = nodeText(row.querySelector('strong'));
        const totalLine = label.toUpperCase() + ': ' + value;
        if (receipt.classList.contains('receipt-copy-customer')) {
          splitWrap(totalLine, width).forEach(function (text) {
            lines.push({ text: text, center: false, grandTotal: true });
          });
        } else {
          addWrapped(lines, totalLine, width, false);
        }
      });

      section.querySelectorAll('.section-heading-row > span').forEach(function (node) {
        const text = nodeText(node);
        if (text) addWrapped(lines, text, width, false);
      });

      // Item list: bullet first, then quantity, then clothing name. The ESC/POS
      // text path uses an ASCII hyphen as a universally supported bullet.
      section.querySelectorAll('.receipt-item-row').forEach(function (row) {
        const name = nodeText(row.querySelector('.receipt-item-name strong')) || '';
        const qty = nodeText(row.querySelector('.receipt-item-qty'));
        if (name) addWrapped(lines, '- ' + (qty ? qty + 'x ' : '') + name, width, false);
        const note = nodeText(row.querySelector('.receipt-item-name small'));
        if (note) splitWrap(note, width).forEach(function (text) { lines.push({ text: text, center: false, itemNote: true }); });
      });

      section.querySelectorAll('.receipt-item-total > div').forEach(function (row) {
        const label = nodeText(row.querySelector('span'));
        const value = nodeText(row.querySelector('strong'));
        if (label || value) addWrapped(lines, label + ': ' + value, width, false);
      });
      lines.push({ text: '', center: false });
    });

    // Optional copy labels are part of the receipt content too.
    const copyLabel = receipt.querySelector('.receipt-copy-label');
    if (copyLabel) addWrapped(lines, nodeText(copyLabel).toUpperCase(), width, true);

    const footer = receipt.querySelector('.thermal-footer');
    if (footer) {
      Array.from(footer.querySelectorAll('.footer-message, .receipt-note, small')).forEach(function (node) {
        const text = nodeText(node);
        if (text) addWrapped(lines, text, width, true);
      });
    }

    // In the HTML design the cut marker follows the footer; keep that order in ESC/POS.
    const cutLine = receipt.querySelector('.receipt-cut-line');
    if (cutLine) {
      lines.push({ text: '-'.repeat(Math.min(width, 32)), center: true });
      const cutText = nodeText(cutLine);
      if (cutText) addWrapped(lines, cutText.toUpperCase(), width, true);
    }
    while (lines.length && !lines[lines.length - 1].text) lines.pop();
    return lines;
  }

  function getPaperWidth() {
    const raw = getComputedStyle(document.documentElement).getPropertyValue('--receipt-paper').trim();
    return parseInt(raw, 10) === 80 ? 80 : 58;
  }

  function buildEscPosData() {
    const width = getPaperWidth() === 80 ? 48 : 32;
    const receipts = Array.from(document.querySelectorAll('.thermal-receipt'));
    if (!receipts.length) throw new Error('Tidak ada isi struk yang dapat dicetak.');
    const bytes = [0x1b, 0x40]; // Initialize printer.
    bytes.push(0x1b, 0x74, 0x00); // Default code page; receipt text is normalized to ASCII.
    receipts.forEach(function (receipt, index) {
      const lines = extractReceiptLines(receipt, width);
      let currentAlignment = null;
      lines.forEach(function (line) {
        const alignment = line.center ? 1 : 0;
        if (alignment !== currentAlignment) {
          bytes.push(0x1b, 0x61, alignment);
          currentAlignment = alignment;
        }
        if (line.text) {
          if (line.grandTotal) {
            // Emphasize the consumer total on text-based ESC/POS printers.
            bytes.push(0x1b, 0x45, 0x01); // Bold on.
            bytes.push(0x1d, 0x21, 0x01); // Double height, normal width.
            bytes.push.apply(bytes, Array.from(new TextEncoder().encode(line.text + '\n')));
            bytes.push(0x1d, 0x21, 0x00); // Normal size.
            bytes.push(0x1b, 0x45, 0x00); // Bold off.
          } else {
            bytes.push.apply(bytes, Array.from(new TextEncoder().encode(line.text + '\n')));
          }
        } else {
          bytes.push(0x0a);
        }
      });
      bytes.push(0x0a, 0x0a, 0x1b, 0x61, 0x00);
      if (index < receipts.length - 1) {
        bytes.push(0x1b, 0x64, 0x03); // Feed before next copy.
      }
    });
    bytes.push(0x1b, 0x64, 0x03, 0x1d, 0x56, 0x00); // Feed and cut, if cutter exists.
    return new Uint8Array(bytes);
  }


  // Rasterize the actual HTML receipt to a monochrome bitmap so BLE printing
  // preserves the visual layout. All external image resources must be embedded
  // as data URLs before the SVG is drawn; otherwise the browser taints the canvas
  // and getImageData() throws a SecurityError.
  function inlineComputedStyles(source, clone) {
    if (source.nodeType !== 1 || clone.nodeType !== 1) return;
    const computed = window.getComputedStyle(source);
    let css = '';
    for (let i = 0; i < computed.length; i++) {
      const property = computed[i];
      let value = computed.getPropertyValue(property);
      // A CSS url() can also taint the raster canvas. Receipt artwork uses inline
      // <img> elements, so remove external CSS images from the snapshot.
      if (/url\(/i.test(value)) {
        value = 'none';
      }
      css += property + ':' + value + ';';
    }
    // Use only sanitized computed styles. Appending the source's original inline
    // style after this string can reintroduce background-image:url(...) and taint
    // the canvas even though the computed values were cleaned above.
    clone.setAttribute('style', css);
    const sourceChildren = source.children || [];
    const cloneChildren = clone.children || [];
    for (let i = 0; i < Math.min(sourceChildren.length, cloneChildren.length); i++) {
      inlineComputedStyles(sourceChildren[i], cloneChildren[i]);
    }
  }

  function sanitizeReceiptResources(clone) {
    const nodes = [clone].concat(Array.from(clone.querySelectorAll('*')));
    nodes.forEach(function (node) {
      if (!node.attributes) return;
      Array.from(node.attributes).forEach(function (attribute) {
        const name = attribute.name.toLowerCase();
        const value = attribute.value || '';
        if (name === 'srcset' || name === 'crossorigin' || name === 'integrity' || name === 'poster') {
          node.removeAttribute(attribute.name);
          return;
        }
        if (name === 'style' && /url\s*\(/i.test(value)) {
          node.setAttribute('style', value.replace(/url\s*\([^)]*\)/gi, 'none'));
          return;
        }
        if (name === 'src' && node.tagName && node.tagName.toLowerCase() === 'img') {
          // The image inlining pass replaces these with safe data: URLs or removes them.
          if (!/^data:image\//i.test(value)) node.removeAttribute(attribute.name);
          return;
        }
        if ((name === 'href' || name === 'xlink:href') && value && value.charAt(0) !== '#' && !/^data:image\//i.test(value)) {
          node.removeAttribute(attribute.name);
        }
        if (name === 'background') node.removeAttribute(attribute.name);
      });
    });
    // SVG image nodes can carry external references independently of <img>.
    clone.querySelectorAll('image, iframe, video, audio, object, embed').forEach(function (node) {
      node.remove();
    });
  }

  function renderReceiptTextFallback(receipt, targetWidth) {
    // Last-resort fallback for browsers that still mark an SVG/foreignObject canvas
    // as cross-origin. Draw directly at a printer-friendly dot size; small CSS-pixel
    // fonts look tiny when each canvas pixel maps to one thermal-printer dot.
    const paperWidth = getPaperWidth();
    // Keep the text fallback within the printable dot width. The former 20-25 px
    // fonts were too large for the RPP02N; this modest increase balances readability and width.
    const columns = paperWidth === 80 ? 42 : 30;
    const normalFont = paperWidth === 80 ? 18 : 17;
    const headingFont = paperWidth === 80 ? 22 : 20;
    const noteFont = paperWidth === 80 ? 17 : 16;
    const lineHeight = paperWidth === 80 ? 25 : 23;
    const padding = paperWidth === 80 ? 14 : 10;
    const lines = extractReceiptLines(receipt, columns);
    const canvas = document.createElement('canvas');
    canvas.width = targetWidth;
    canvas.height = Math.max(180, padding * 2 + lines.length * lineHeight);
    const context = canvas.getContext('2d', { willReadFrequently: true });
    if (!context) throw new Error('Canvas tidak tersedia di browser ini.');
    context.fillStyle = '#fff';
    context.fillRect(0, 0, canvas.width, canvas.height);
    context.fillStyle = '#000';
    context.textBaseline = 'top';
    let y = padding;
    lines.forEach(function (line) {
      const text = line.text || ' ';
      const fontSize = line.center ? headingFont : (line.itemNote ? noteFont : normalFont);
      context.font = ((line.center || line.itemNote) ? 'bold ' : '') + fontSize + 'px monospace';
      const metrics = context.measureText(text);
      const maxWidth = canvas.width - padding * 2;
      const x = line.center ? Math.max(padding, (canvas.width - Math.min(metrics.width, maxWidth)) / 2) : padding;
      // Avoid Canvas fillText(maxWidth) squeezing long lines to unreadably small text.
      // Lines are wrapped to the selected character count above instead.
      context.fillText(text, x, y);
      y += lineHeight;
    });
    context.getImageData(0, 0, 1, 1);
    return canvas;
  }

  function blobToDataUrl(blob) {
    return new Promise(function (resolve, reject) {
      const reader = new FileReader();
      reader.onload = function () { resolve(String(reader.result || '')); };
      reader.onerror = function () { reject(new Error('Gagal menyiapkan gambar logo untuk cetak Bluetooth.')); };
      reader.readAsDataURL(blob);
    });
  }

  async function inlineReceiptImages(sourceReceipt, clone) {
    const sourceImages = Array.from(sourceReceipt.querySelectorAll('img'));
    const cloneImages = Array.from(clone.querySelectorAll('img'));
    for (let index = 0; index < cloneImages.length; index++) {
      const image = cloneImages[index];
      const source = sourceImages[index];
      if (!source) { image.remove(); continue; }
      const rawSrc = source.currentSrc || source.getAttribute('src') || '';
      if (!rawSrc) { image.remove(); continue; }
      try {
        // Fetch and embed images rather than leaving cross-origin references inside
        // the serialized SVG. Same-origin static logos work; CORS-protected remote
        // images that cannot be fetched are omitted instead of breaking all printing.
        const response = await fetch(new URL(rawSrc, document.baseURI).href, {
          mode: 'cors',
          credentials: new URL(rawSrc, document.baseURI).origin === location.origin ? 'same-origin' : 'omit',
          cache: 'force-cache'
        });
        if (!response.ok) throw new Error('HTTP ' + response.status);
        const dataUrl = await blobToDataUrl(await response.blob());
        if (!dataUrl.startsWith('data:image/')) throw new Error('Format gambar tidak didukung');
        image.setAttribute('src', dataUrl);
        image.removeAttribute('srcset');
        image.removeAttribute('crossorigin');
      } catch (_) {
        // Keep printing the text and layout even if a remote logo cannot be embedded.
        const alt = image.getAttribute('alt') || '';
        const fallback = document.createElement('span');
        fallback.textContent = alt;
        fallback.setAttribute('style', 'font-size:10px;color:#000;');
        image.replaceWith(fallback);
      }
    }
  }

  async function receiptToCanvas(receipt, targetWidth) {
    // The browser-driver path uses @media print rules (narrower padding and
    // print-specific item/total font sizes). Temporarily activate the matching
    // .receipt-raster-mode rules before copying computed styles, so kasir/ BLE
    // raster output follows the same print layout rather than the screen preview.
    const body = document.body;
    body.classList.add('receipt-raster-mode');
    let sourceWidth;
    let sourceHeight;
    let renderHeight;
    let clone;
    try {
      const rect = receipt.getBoundingClientRect();
      sourceWidth = Math.max(1, Math.ceil(rect.width));
      sourceHeight = Math.max(1, Math.ceil(receipt.scrollHeight || rect.height));
      // Reserve extra vertical space so wrapped per-item notes are not clipped by
      // browser differences between the live DOM and the serialized SVG snapshot.
      renderHeight = sourceHeight + Math.max(24, Math.ceil(sourceHeight * 0.025));
      clone = receipt.cloneNode(true);
      inlineComputedStyles(receipt, clone);
    } finally {
      body.classList.remove('receipt-raster-mode');
    }
    await inlineReceiptImages(receipt, clone);
    sanitizeReceiptResources(clone);
    clone.style.width = sourceWidth + 'px';
    clone.style.minWidth = sourceWidth + 'px';
    clone.style.maxWidth = sourceWidth + 'px';
    clone.style.height = 'auto';
    clone.style.minHeight = sourceHeight + 'px';
    clone.style.maxHeight = 'none';
    clone.style.margin = '0';
    clone.style.boxShadow = 'none';
    clone.style.transform = 'none';
    clone.style.overflow = 'visible';
    clone.querySelectorAll('.receipt-copy-label').forEach(function (node) { node.style.display = 'block'; });

    const XHTML = 'http://www.w3.org/1999/xhtml';
    const wrapper = document.createElementNS(XHTML, 'div');
    wrapper.setAttribute('xmlns', XHTML);
    wrapper.style.width = sourceWidth + 'px';
    wrapper.style.height = renderHeight + 'px';
    wrapper.style.background = '#fff';
    wrapper.style.color = '#000';
    wrapper.appendChild(clone);
    const markup = new XMLSerializer().serializeToString(wrapper);
    const svg = '<svg xmlns="http://www.w3.org/2000/svg" width="' + sourceWidth + '" height="' + renderHeight + '"><foreignObject width="100%" height="100%">' + markup + '</foreignObject></svg>';
    const blob = new Blob([svg], { type: 'image/svg+xml;charset=utf-8' });
    const objectUrl = URL.createObjectURL(blob);
    try {
      const image = new Image();
      await new Promise(function (resolve, reject) {
        image.onload = resolve;
        image.onerror = function () { reject(new Error('Browser tidak dapat merender desain struk menjadi gambar.')); };
        image.src = objectUrl;
      });
      const canvas = document.createElement('canvas');
      canvas.width = targetWidth;
      canvas.height = Math.max(1, Math.round(renderHeight * targetWidth / sourceWidth));
      const context = canvas.getContext('2d', { willReadFrequently: true });
      if (!context) throw new Error('Canvas tidak tersedia di browser ini.');
      context.fillStyle = '#fff';
      context.fillRect(0, 0, canvas.width, canvas.height);
      context.drawImage(image, 0, 0, canvas.width, canvas.height);
      try {
        // Test readability here so a tainted canvas can fall back before ESC/POS
        // conversion calls getImageData() and aborts the Bluetooth job.
        context.getImageData(0, 0, 1, 1);
        return canvas;
      } catch (canvasError) {
        if (!canvasError || (canvasError.name !== 'SecurityError' && !/taint|cross-origin/i.test(canvasError.message || ''))) throw canvasError;
        setStatus('Browser memblokir rasterisasi desain HTML karena aset lintas-origin. Mencetak versi teks cadangan dengan huruf diperbesar; tata letak belum identik dengan desain. Periksa logo/aset eksternal untuk memulihkan mode desain.', 'info');
        return renderReceiptTextFallback(receipt, targetWidth);
      }
    } finally {
      URL.revokeObjectURL(objectUrl);
    }
  }

  function canvasToEscPosRaster(canvas) {
    const context = canvas.getContext('2d', { willReadFrequently: true });
    const image = context.getImageData(0, 0, canvas.width, canvas.height);
    const widthBytes = Math.ceil(canvas.width / 8);
    const height = canvas.height;
    const raster = new Uint8Array(widthBytes * height);
    for (let y = 0; y < height; y++) {
      for (let x = 0; x < canvas.width; x++) {
        const offset = (y * canvas.width + x) * 4;
        const luminance = (image.data[offset] * 299 + image.data[offset + 1] * 587 + image.data[offset + 2] * 114) / 1000;
        if (luminance < 205) raster[y * widthBytes + (x >> 3)] |= (0x80 >> (x & 7));
      }
    }
    const command = [0x1d, 0x76, 0x30, 0x00, widthBytes & 0xff, (widthBytes >> 8) & 0xff, height & 0xff, (height >> 8) & 0xff];
    const result = new Uint8Array(command.length + raster.length);
    result.set(command, 0);
    result.set(raster, command.length);
    return result;
  }

  async function buildEscPosRasterData(receiptList) {
    const receipts = receiptList || Array.from(document.querySelectorAll('.thermal-receipt'));
    if (!receipts.length) throw new Error('Tidak ada isi struk yang dapat dicetak.');
    const paperWidth = getPaperWidth();
    // RPP02N paper is 57 mm nominal / 58 mm setting. Use a conservative raster
    // width to stay within the effective print area and avoid clipping at both edges.
    const targetWidth = paperWidth === 80 ? 544 : 360;
    // Build one print job per receipt. This lets the cashier tear each copy before
    // confirming the next one; do not batch copies or send an automatic cutter command.
    const chunks = [[0x1b, 0x40], [0x1b, 0x61, 0x00], [0x1d, 0x4c, 0x00, 0x00]];
    for (let i = 0; i < receipts.length; i++) {
      const canvas = await receiptToCanvas(receipts[i], targetWidth);
      chunks.push(Array.from(canvasToEscPosRaster(canvas)));
      chunks.push([0x0a, 0x0a, 0x0a]);
    }
    chunks.push([0x1b, 0x64, 0x03]);
    const total = chunks.reduce(function (sum, chunk) { return sum + chunk.length; }, 0);
    const data = new Uint8Array(total);
    let offset = 0;
    chunks.forEach(function (chunk) { data.set(chunk, offset); offset += chunk.length; });
    return data;
  }

  function getReceiptNodes() {
    return Array.from(document.querySelectorAll('.thermal-receipt'));
  }

  function receiptCopyName(receipt) {
    if (receipt.classList.contains('receipt-copy-customer')) return 'struk konsumen';
    if (receipt.classList.contains('receipt-copy-laundry')) return 'struk arsip laundry';
    if (receipt.classList.contains('receipt-copy-items')) return 'struk item pakaian';
    return 'struk';
  }

  function askToContinueAfterTear(index, total, receipt) {
    return window.confirm(
      'Struk ' + (index + 1) + ' dari ' + total + ' (' + receiptCopyName(receipt) + ') sudah dikirim ke dialog/antrean cetak.\n\n' +
      'Jika struk sudah keluar, sobek/pisahkan sekarang. Klik OK untuk melanjutkan ke struk berikutnya, atau Batal untuk menghentikan proses.'
    );
  }

  function ensureSequentialPrintStyle() {
    if (document.getElementById('sani-sequential-print-style')) return;
    const style = document.createElement('style');
    style.id = 'sani-sequential-print-style';
    style.textContent = '@media print {' +
      'body.sani-sequential-print .receipt-bundle{display:block!important;gap:0!important;}' +
      'body.sani-sequential-print .thermal-receipt{display:none!important;break-after:auto!important;page-break-after:auto!important;}' +
      'body.sani-sequential-print .thermal-receipt[data-print-active="true"]{display:block!important;break-after:auto!important;page-break-after:auto!important;}' +
      'body.sani-sequential-print .receipt-copy:not(:last-child){break-after:auto!important;page-break-after:auto!important;}' +
      '}';
    document.head.appendChild(style);
  }

  function printBrowserReceiptsSequentially(receipts) {
    const list = receipts || getReceiptNodes();
    if (!list.length) {
      setStatus('Tidak ada struk yang dapat dicetak.', 'error');
      return;
    }
    if (list.length === 1) {
      window.print();
      return;
    }
    ensureSequentialPrintStyle();
    const body = document.body;
    body.classList.add('sani-sequential-print');
    list.forEach(function (receipt) { receipt.removeAttribute('data-print-active'); });
    let completed = 0;
    try {
      for (let i = 0; i < list.length; i++) {
        list.forEach(function (receipt) { receipt.removeAttribute('data-print-active'); });
        list[i].setAttribute('data-print-active', 'true');
        setStatus('Cetak bertahap: ' + (i + 1) + ' dari ' + list.length + ' — ' + receiptCopyName(list[i]) + '.', 'info');
        window.print();
        completed = i + 1;
        if (i < list.length - 1 && !askToContinueAfterTear(i, list.length, list[i])) break;
      }
    } finally {
      body.classList.remove('sani-sequential-print');
      list.forEach(function (receipt) { receipt.removeAttribute('data-print-active'); });
    }
    if (completed >= list.length) setStatus('Selesai. Semua ' + list.length + ' struk telah diproses satu per satu.', 'success');
    else setStatus('Pencetakan dihentikan setelah ' + completed + ' dari ' + list.length + ' struk.', 'info');
  }

  async function sendEscPosChunksToBluetooth(writable, data) {
    const chunkSize = 20; // Conservative default for a 23-byte ATT MTU.
    for (let offset = 0; offset < data.length; offset += chunkSize) {
      const chunk = data.slice(offset, Math.min(offset + chunkSize, data.length));
      if (writable.properties.writeWithoutResponse && writable.writeValueWithoutResponse) {
        await writable.writeValueWithoutResponse(chunk);
      } else if (writable.writeValueWithResponse) {
        await writable.writeValueWithResponse(chunk);
      } else {
        await writable.writeValue(chunk);
      }
    }
  }

  function toBase64(bytes) {
    let binary = '';
    const chunkSize = 0x8000;
    for (let offset = 0; offset < bytes.length; offset += chunkSize) {
      binary += String.fromCharCode.apply(null, bytes.subarray(offset, offset + chunkSize));
    }
    return btoa(binary);
  }

  async function bridgeRequest(path, options) {
    const response = await fetch(BRIDGE_URL + path, Object.assign({ cache: 'no-store' }, options || {}));
    let payload;
    try { payload = await response.json(); } catch (_) { payload = {}; }
    if (!response.ok || payload.ok === false) {
      throw new Error(payload.error || ('Printer Bridge merespons HTTP ' + response.status + '.'));
    }
    return payload;
  }

  async function fetchPrinters(token) {
    return bridgeRequest('/printers', { headers: { 'X-Printer-Token': token } });
  }

  function populatePrinterSelect(select, payload, preferredName) {
    if (!select) return;
    const current = preferredName || select.value || getStoredPrinter() || payload.default_printer || '';
    select.replaceChildren();
    if (!payload.printers || !payload.printers.length) {
      const option = document.createElement('option');
      option.value = '';
      option.textContent = 'Tidak ada printer Windows';
      select.appendChild(option);
      return;
    }
    payload.printers.forEach(function (printer) {
      const option = document.createElement('option');
      option.value = printer.name;
      option.textContent = printer.name + (printer.is_default ? ' (Default)' : '');
      select.appendChild(option);
    });
    if (Array.from(select.options).some(function (option) { return option.value === current; })) select.value = current;
    else if (payload.default_printer) select.value = payload.default_printer;
  }

  async function refreshBridgePanel() {
    const panel = byData('printer-bridge-panel');
    if (!panel) return;
    const tokenInput = byData('bridge-token', panel);
    const printerSelect = byData('bridge-printer', panel);
    const token = (tokenInput && tokenInput.value.trim()) || getStoredToken();
    try {
      const health = await bridgeRequest('/health');
      if (!health.printer_module_available) {
        setStatus('Layanan terdeteksi, tetapi modul pywin32 belum tersedia. Jalankan ulang setup_windows.bat.', 'error');
        return;
      }
      if (!token) {
        setStatus('Layanan Printer Bridge aktif. Masukkan token dari jendela start_printer_bridge.bat untuk memuat daftar printer.', 'info');
        return;
      }
      const payload = await fetchPrinters(token);
      populatePrinterSelect(printerSelect, payload, getStoredPrinter());
      setStatus('Terhubung. Ditemukan ' + payload.printers.length + ' printer Windows.', 'success');
    } catch (error) {
      setStatus('Printer Bridge belum dapat diakses: ' + error.message + ' Pastikan start_printer_bridge.bat berjalan di komputer kasir.', 'error');
    }
  }

  async function printViaBridge() {
    const token = getStoredToken();
    if (!token) {
      setStatus('Token Printer Bridge belum disimpan. Buka Control Center > Printer Lokal pada komputer kasir.', 'error');
      return;
    }
    setStatus('Mengirim struk ke antrean printer Windows...', 'info');
    try {
      const health = await bridgeRequest('/health');
      if (!health.printer_module_available) throw new Error('pywin32 belum tersedia di komputer kasir.');
      const payload = await fetchPrinters(token);
      const printerName = getStoredPrinter() || payload.default_printer || (payload.printers[0] && payload.printers[0].name);
      if (!printerName) throw new Error('Tidak ada printer yang terpasang di Windows. Instal driver atau pasangkan printer dahulu.');
      // Send one receipt per job so the cashier can tear it before continuing.
      const receipts = getReceiptNodes();
      if (!receipts.length) throw new Error('Tidak ada struk yang dapat dicetak.');
      for (let i = 0; i < receipts.length; i++) {
        setStatus('Merender struk ' + (i + 1) + ' dari ' + receipts.length + ' untuk printer Windows...', 'info');
        const data = await buildEscPosRasterData([receipts[i]]);
        const result = await bridgeRequest('/print', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-Printer-Token': token },
          body: JSON.stringify({ printer_name: printerName, data_base64: toBase64(data) })
        });
        if (i < receipts.length - 1 && !askToContinueAfterTear(i, receipts.length, receipts[i])) {
          setStatus('Pencetakan dihentikan setelah ' + (i + 1) + ' dari ' + receipts.length + ' struk.', 'info');
          return;
        }
      }
      setStatus('Selesai. Semua ' + receipts.length + ' struk dikirim satu per satu ke printer ' + printerName + '.', 'success');
    } catch (error) {
      setStatus('Cetak langsung gagal: ' + error.message, 'error');
    }
  }

  async function printViaBluetooth() {
    if (!navigator.bluetooth || !navigator.bluetooth.requestDevice) {
      setStatus('Browser ini tidak mendukung Web Bluetooth. Fitur langsung hanya untuk printer BLE yang kompatibel melalui Chrome Android dan halaman HTTPS. Printer Bluetooth klasik/SPP perlu aplikasi/layanan cetak Android atau driver vendor.', 'error');
      return;
    }
    let device;
    try {
      setStatus('Pilih printer Bluetooth BLE pada dialog perangkat...', 'info');
      device = await navigator.bluetooth.requestDevice({ acceptAllDevices: true, optionalServices: SERVICE_UUIDS });
      if (!device.gatt) throw new Error('Perangkat tidak menyediakan koneksi GATT BLE. Printer mungkin menggunakan Bluetooth klasik/SPP.');
      const server = await device.gatt.connect();
      let services = [];
      try { services = await server.getPrimaryServices(); } catch (_) { /* try known services below */ }
      if (!services.length) {
        for (const uuid of SERVICE_UUIDS) {
          try { services.push(await server.getPrimaryService(uuid)); } catch (_) { /* UUID not exposed by this printer */ }
        }
      }
      let writable = null;
      for (const service of services) {
        let characteristics = [];
        try { characteristics = await service.getCharacteristics(); } catch (_) { continue; }
        writable = characteristics.find(function (characteristic) {
          return characteristic.properties.write || characteristic.properties.writeWithoutResponse;
        }) || null;
        if (writable) break;
      }
      if (!writable) {
        try { device.gatt.disconnect(); } catch (_) { /* no-op */ }
        throw new Error('Tidak ditemukan karakteristik BLE yang dapat ditulis. Printer mungkin Bluetooth klasik/SPP atau memakai protokol vendor.');
      }
      setStatus('Merender desain struk menjadi gambar untuk mempertahankan tata letak...', 'info');
      const receipts = getReceiptNodes();
      if (!receipts.length) throw new Error('Tidak ada struk yang dapat dicetak.');
      for (let i = 0; i < receipts.length; i++) {
        if (!device.gatt.connected) {
          const reconnected = await device.gatt.connect();
          const serviceList = await reconnected.getPrimaryServices();
          let refreshedWritable = null;
          for (const service of serviceList) {
            const chars = await service.getCharacteristics();
            refreshedWritable = chars.find(function (characteristic) {
              return characteristic.properties.write || characteristic.properties.writeWithoutResponse;
            }) || null;
            if (refreshedWritable) break;
          }
          if (!refreshedWritable) throw new Error('Koneksi BLE tersambung kembali, tetapi kanal tulis printer tidak ditemukan.');
          writable = refreshedWritable;
        }
        setStatus('Mengirim struk ' + (i + 1) + ' dari ' + receipts.length + ' ke printer Bluetooth...', 'info');
        const data = await buildEscPosRasterData([receipts[i]]);
        await sendEscPosChunksToBluetooth(writable, data);
        if (i < receipts.length - 1 && !askToContinueAfterTear(i, receipts.length, receipts[i])) {
          try { device.gatt.disconnect(); } catch (_) { /* no-op */ }
          setStatus('Pencetakan Bluetooth dihentikan setelah ' + (i + 1) + ' dari ' + receipts.length + ' struk.', 'info');
          return;
        }
      }
      try { device.gatt.disconnect(); } catch (_) { /* print data has been sent */ }
      setStatus('Selesai. Semua ' + receipts.length + ' struk sudah dikirim satu per satu ke ' + (device.name || 'printer Bluetooth') + '.', 'success');
    } catch (error) {
      if (device && device.gatt && device.gatt.connected) {
        try { device.gatt.disconnect(); } catch (_) { /* no-op */ }
      }
      if (error && error.name === 'NotFoundError') {
        setStatus('Pemilihan printer dibatalkan.', 'info');
      } else {
        setStatus('Cetak Bluetooth gagal: ' + error.message, 'error');
      }
    }
  }

  function saveBridgeSettings() {
    const panel = byData('printer-bridge-panel');
    if (!panel) return;
    const tokenInput = byData('bridge-token', panel);
    const printerSelect = byData('bridge-printer', panel);
    const token = tokenInput ? tokenInput.value.trim() : '';
    const printerName = printerSelect ? printerSelect.value : '';
    if (!token) {
      setStatus('Token wajib diisi. Jalankan start_printer_bridge.bat lalu salin token dari jendela hitam.', 'error');
      return;
    }
    try {
      localStorage.setItem(TOKEN_KEY, token);
      if (printerName) localStorage.setItem(PRINTER_KEY, printerName);
      else localStorage.removeItem(PRINTER_KEY);
      setStatus('Pengaturan printer disimpan pada browser ini. Pengaturan tidak dikirim ke server.', 'success');
      refreshBridgePanel();
    } catch (_) {
      setStatus('Browser tidak mengizinkan penyimpanan lokal. Coba browser biasa, bukan mode privat.', 'error');
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('[data-print-browser]').forEach(function (button) {
      button.addEventListener('click', function () {
        const receipts = getReceiptNodes();
        if (receipts.length > 1) printBrowserReceiptsSequentially(receipts);
        else window.print();
      });
    });
    document.querySelectorAll('[data-print-bridge]').forEach(function (button) {
      button.addEventListener('click', printViaBridge);
    });
    document.querySelectorAll('[data-print-bluetooth]').forEach(function (button) {
      button.addEventListener('click', printViaBluetooth);
    });

    const panel = byData('printer-bridge-panel');
    if (panel) {
      const tokenInput = byData('bridge-token', panel);
      const printerSelect = byData('bridge-printer', panel);
      if (tokenInput) tokenInput.value = getStoredToken();
      if (printerSelect) {
        const savedPrinter = getStoredPrinter();
        if (savedPrinter) {
          const option = document.createElement('option');
          option.value = savedPrinter;
          option.textContent = savedPrinter + ' (tersimpan)';
          printerSelect.appendChild(option);
        }
      }
      const checkButton = byData('bridge-check', panel);
      const refreshButton = byData('bridge-refresh', panel);
      const saveButton = byData('bridge-save', panel);
      if (checkButton) checkButton.addEventListener('click', refreshBridgePanel);
      if (refreshButton) refreshButton.addEventListener('click', refreshBridgePanel);
      if (saveButton) saveButton.addEventListener('click', saveBridgeSettings);
    }

    if (document.body && document.body.dataset.autoprint === '1') {
      window.addEventListener('load', function () {
        window.setTimeout(function () {
          const receipts = getReceiptNodes();
          if (receipts.length > 1) printBrowserReceiptsSequentially(receipts);
          else if (receipts.length === 1) window.print();
        }, 320);
      }, { once: true });
    }
  });
})();
