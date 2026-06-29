const CART_KEY = 'passat_cart';

const Carrinho = {
  getItems() {
    try {
      return JSON.parse(localStorage.getItem(CART_KEY)) || [];
    } catch {
      return [];
    }
  },

  saveItems(items) {
    localStorage.setItem(CART_KEY, JSON.stringify(items));
    this.updateBadge();
    window.dispatchEvent(new CustomEvent('cartUpdated'));
  },

  addItem(peca) {
    const items = this.getItems();
    const existing = items.find((i) => i.id === peca.id);

    if (existing) {
      existing.quantidade += 1;
    } else {
      items.push({
        id: peca.id,
        nome: peca.nome,
        preco: peca.preco,
        imagem: peca.imagem,
        quantidade: 1
      });
    }

    this.saveItems(items);
    return items;
  },

  removeItem(id) {
    const items = this.getItems().filter((i) => i.id !== id);
    this.saveItems(items);
    return items;
  },

  updateQuantity(id, quantidade) {
    const items = this.getItems();
    const item = items.find((i) => i.id === id);

    if (!item) return items;

    if (quantidade <= 0) {
      return this.removeItem(id);
    }

    item.quantidade = quantidade;
    this.saveItems(items);
    return items;
  },

  clear() {
    localStorage.removeItem(CART_KEY);
    this.updateBadge();
    window.dispatchEvent(new CustomEvent('cartUpdated'));
  },

  getTotal() {
    return this.getItems().reduce((sum, item) => sum + item.preco * item.quantidade, 0);
  },

  getCount() {
    return this.getItems().reduce((sum, item) => sum + item.quantidade, 0);
  },

  updateBadge() {
    const badge = document.getElementById('cart-badge');
    if (!badge) return;

    const count = this.getCount();
    badge.textContent = count;
    badge.classList.toggle('visible', count > 0);
  },

  formatPrice(value) {
    return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
  },

  formatPanfletoPrice(value) {
    const num = Math.round(Number(value));
    return `R$ ${num.toLocaleString('pt-BR', { maximumFractionDigits: 0 })}`;
  },

  buildWhatsAppUrl(items, contato) {
    const lines = items.map(
      (item) => `• ${item.nome} (${item.quantidade}x) — ${this.formatPrice(item.preco * item.quantidade)}`
    );

    const total = this.getTotal();
    const message = [
      `Olá ${contato.nome}! Tenho interesse nas seguintes peças do Passat Variant 2012:`,
      '',
      ...lines,
      '',
      `*Total: ${this.formatPrice(total)}*`,
      '',
      'Aguardo retorno para combinar entrega e pagamento.'
    ].join('\n');

    return `https://wa.me/${contato.whatsapp}?text=${encodeURIComponent(message)}`;
  },

  buildSingleItemUrl(peca, contato) {
    const message = [
      `Olá ${contato.nome}! Tenho interesse na peça:`,
      '',
      `*${peca.nome}*`,
      `Preço: ${this.formatPrice(peca.preco)}`,
      '',
      'Peça do Passat Variant 2012. Podemos conversar?'
    ].join('\n');

    return `https://wa.me/${contato.whatsapp}?text=${encodeURIComponent(message)}`;
  }
};

document.addEventListener('DOMContentLoaded', () => Carrinho.updateBadge());
