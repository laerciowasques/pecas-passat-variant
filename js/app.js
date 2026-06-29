let catalogo = null;

const FLYER = {
  w: 1024,
  h: 1536,
  listaTop: 473,
  listaBottom: 1172,
  listaLeft: 3.5,
  listaWidth: 93,
};

function pctY(px) {
  return (px / FLYER.h) * 100;
}

function listaFrameStyle() {
  return [
    `top:${pctY(FLYER.listaTop)}%`,
    `height:${pctY(FLYER.listaBottom - FLYER.listaTop)}%`,
    `left:${FLYER.listaLeft}%`,
    `width:${FLYER.listaWidth}%`,
  ].join(';');
}

async function loadCatalogo() {
  const response = await fetch('data/pecas.json');
  catalogo = await response.json();
  return catalogo;
}

function showToast(message) {
  const toast = document.getElementById('toast');
  if (!toast) return;

  toast.textContent = message;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 2800);
}

function renderFlyerHotspots(pecas) {
  const overlay = document.getElementById('pecas-overlay');
  if (!overlay) return;

  const rows = pecas
    .map(
      (peca) => `
        <div class="flyer-lista-row" data-row="${peca.id}">
          <div class="flyer-row-highlight" aria-hidden="true"></div>
          <button
            type="button"
            class="flyer-row-hotspot"
            data-id="${peca.id}"
            aria-label="Adicionar ${peca.nome} ao carrinho"
          ></button>
        </div>
      `
    )
    .join('');

  overlay.innerHTML = `
    <div class="flyer-lista-frame flyer-lista-frame--hotspots" style="${listaFrameStyle()}">
      ${rows}
    </div>
  `;
}

function setupFlyerRowHighlight() {
  const overlay = document.getElementById('pecas-overlay');
  if (!overlay) return;

  const clearTouchActive = () => {
    overlay.querySelectorAll('.flyer-lista-row.is-touch-active').forEach((el) => {
      el.classList.remove('is-touch-active');
    });
  };

  overlay.addEventListener(
    'touchstart',
    (e) => {
      const row = e.target.closest('.flyer-lista-row');
      if (!row) return;

      clearTouchActive();
      row.classList.add('is-touch-active');
    },
    { passive: true }
  );

  overlay.addEventListener('touchend', clearTouchActive);
  overlay.addEventListener('touchcancel', clearTouchActive);

  document.addEventListener('touchstart', (e) => {
    if (!e.target.closest('.flyer-lista-row')) clearTouchActive();
  });
}

function setupFlyerEvents(pecas, contato) {
  const overlay = document.getElementById('pecas-overlay');
  if (!overlay) return;

  overlay.addEventListener('click', (e) => {
    const row = e.target.closest('.flyer-row-hotspot');
    if (!row) return;

    const id = parseInt(row.dataset.id, 10);
    const peca = pecas.find((p) => p.id === id);
    if (!peca) return;

    Carrinho.addItem(peca);
    showToast(`"${peca.nome}" adicionada ao carrinho!`);
  });

  overlay.addEventListener('dblclick', (e) => {
    const row = e.target.closest('.flyer-row-hotspot');
    if (!row) return;

    const id = parseInt(row.dataset.id, 10);
    const peca = pecas.find((p) => p.id === id);
    if (!peca) return;

    window.open(Carrinho.buildSingleItemUrl(peca, contato), '_blank');
  });

  const flyerWhatsapp = document.getElementById('flyer-whatsapp');
  if (flyerWhatsapp) {
    const msg = encodeURIComponent(
      `Olá ${contato.nome}! Tenho interesse nas peças do Passat Variant 2012. Podemos conversar?`
    );
    flyerWhatsapp.href = `https://wa.me/${contato.whatsapp}?text=${msg}`;
  }
}

function renderCartPage() {
  const container = document.getElementById('cart-items');
  const totalEl = document.getElementById('cart-total');
  const emptyEl = document.getElementById('cart-empty');
  const summaryEl = document.getElementById('cart-summary');
  const whatsappBtn = document.getElementById('btn-whatsapp-cart');

  if (!container || !catalogo) return;

  const items = Carrinho.getItems();

  if (items.length === 0) {
    container.innerHTML = '';
    emptyEl?.classList.remove('hidden');
    summaryEl?.classList.add('hidden');
    return;
  }

  emptyEl?.classList.add('hidden');
  summaryEl?.classList.remove('hidden');

  container.innerHTML = items
    .map(
      (item) => `
    <div class="cart-item" data-id="${item.id}">
      <img class="cart-item__img" src="${item.imagem}" alt="${item.nome}">
      <div class="cart-item__info">
        <h3>${item.nome}</h3>
        <p class="cart-item__preco-unit">${Carrinho.formatPrice(item.preco)} cada</p>
      </div>
      <div class="cart-item__qty">
        <button class="qty-btn" data-action="decrease" data-id="${item.id}">−</button>
        <span>${item.quantidade}</span>
        <button class="qty-btn" data-action="increase" data-id="${item.id}">+</button>
      </div>
      <span class="cart-item__subtotal">${Carrinho.formatPrice(item.preco * item.quantidade)}</span>
      <button class="cart-item__remove" data-action="remove" data-id="${item.id}" title="Remover">✕</button>
    </div>
  `
    )
    .join('');

  const total = Carrinho.getTotal();
  if (totalEl) totalEl.textContent = Carrinho.formatPrice(total);
  if (whatsappBtn) {
    whatsappBtn.href = Carrinho.buildWhatsAppUrl(items, catalogo.contato);
  }
}

function setupCartPageEvents() {
  const container = document.getElementById('cart-items');
  const clearBtn = document.getElementById('btn-clear-cart');

  if (container) {
    container.addEventListener('click', (e) => {
      const btn = e.target.closest('[data-action]');
      if (!btn) return;

      const id = parseInt(btn.dataset.id, 10);
      const items = Carrinho.getItems();
      const item = items.find((i) => i.id === id);
      if (!item) return;

      if (btn.dataset.action === 'increase') {
        Carrinho.updateQuantity(id, item.quantidade + 1);
      } else if (btn.dataset.action === 'decrease') {
        Carrinho.updateQuantity(id, item.quantidade - 1);
      } else if (btn.dataset.action === 'remove') {
        Carrinho.removeItem(id);
      }

      renderCartPage();
    });
  }

  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      Carrinho.clear();
      renderCartPage();
    });
  }

  window.addEventListener('cartUpdated', renderCartPage);
}

document.addEventListener('DOMContentLoaded', async () => {
  Carrinho.updateBadge();

  const isCartPage = document.body.classList.contains('page-cart');

  try {
    await loadCatalogo();
  } catch {
    console.error('Erro ao carregar catálogo');
    return;
  }

  if (isCartPage) {
    renderCartPage();
    setupCartPageEvents();
    return;
  }

  const { pecas, contato } = catalogo;

  renderFlyerHotspots(pecas);
  setupFlyerRowHighlight();
  setupFlyerEvents(pecas, contato);
});
