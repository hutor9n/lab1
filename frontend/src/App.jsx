import React, { useState, useEffect } from 'react';

// Визначаємо шлях до API:
// У браузері dev-сервер проксує /api до бекенду, або використовуємо прямий порт, якщо бекенд на 8000
const API_BASE = '/api/items';

export default function App() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState({ message: '', isError: false });

  // Стан форми
  const [editingId, setEditingId] = useState(null);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [price, setPrice] = useState('');

  const showStatus = (message, isError = false) => {
    setStatus({ message, isError });
    setTimeout(() => {
      setStatus({ message: '', isError: false });
    }, 4500);
  };

  const loadItems = async () => {
    setLoading(true);
    try {
      const res = await fetch(API_BASE);
      if (!res.ok) {
        throw new Error(`Сервер повернув статус ${res.status} (${res.statusText || 'Помилка'}). Перевірте, чи запущено Backend API.`);
      }
      const data = await res.json();
      setItems(data);
    } catch (err) {
      console.error(err);
      showStatus(`Не вдалося завантажити дані: ${err.message}`, true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadItems();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const payload = {
      name: name.trim(),
      description: description.trim() || null,
      price: parseFloat(price)
    };

    try {
      let res;
      if (editingId) {
        res = await fetch(`${API_BASE}/${editingId}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
      } else {
        res = await fetch(API_BASE, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
      }

      if (!res.ok) {
        let errorDetail = `Помилка ${res.status}: ${res.statusText}`;
        try {
          const errData = await res.clone().json();
          if (errData && errData.detail) {
            errorDetail = typeof errData.detail === 'string' ? errData.detail : JSON.stringify(errData.detail);
          }
        } catch (_) {
          // Якщо сервер повернув не-JSON або порожню відповідь
          const text = await res.text();
          if (text) errorDetail = text;
        }
        throw new Error(errorDetail);
      }

      showStatus(editingId ? 'Елемент успішно оновлено!' : 'Новий елемент успішно додано!');
      handleCancel();
      await loadItems();
    } catch (err) {
      showStatus(err.message, true);
    }
  };

  const handleEdit = (item) => {
    setEditingId(item.id);
    setName(item.name);
    setDescription(item.description || '');
    setPrice(item.price.toString());
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleCancel = () => {
    setEditingId(null);
    setName('');
    setDescription('');
    setPrice('');
  };

  const handleDelete = async (id) => {
    if (!window.confirm(`Ви дійсно бажаєте видалити елемент #${id}?`)) return;

    try {
      const res = await fetch(`${API_BASE}/${id}`, { method: 'DELETE' });
      if (!res.ok) {
        throw new Error(`Помилка при видаленні: ${res.status}`);
      }
      showStatus(`Елемент #${id} успішно видалено!`);
      await loadItems();
    } catch (err) {
      showStatus(err.message, true);
    }
  };

  return (
    <div className="container">
      <header>
        <div>
          <h1>
            📦 Управління елементами
            <span className="badge-react">React 18 SPA</span>
          </h1>
          <small style={{ color: 'var(--text-muted)' }}>
            Лабораторна робота №4: React Frontend + FastAPI Backend + PostgreSQL + Helm
          </small>
        </div>
        <button className="btn-primary" onClick={loadItems} disabled={loading}>
          {loading ? 'Оновлення...' : '🔄 Оновити'}
        </button>
      </header>

      {status.message && (
        <div className={`status-msg ${status.isError ? 'status-error' : 'status-success'}`}>
          {status.message}
        </div>
      )}

      <div className="card">
        <h2>{editingId ? `Редагування елемента #${editingId}` : 'Додати новий елемент'}</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-grid">
            <div className="form-group">
              <label htmlFor="name">Назва *</label>
              <input
                id="name"
                type="text"
                required
                placeholder="Напр. Ноутбук"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </div>
            <div className="form-group">
              <label htmlFor="description">Опис</label>
              <input
                id="description"
                type="text"
                placeholder="Напр. 16GB RAM, 1TB SSD"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>
            <div className="form-group">
              <label htmlFor="price">Ціна (₴) *</label>
              <input
                id="price"
                type="number"
                step="0.01"
                min="0.01"
                required
                placeholder="999.99"
                value={price}
                onChange={(e) => setPrice(e.target.value)}
              />
            </div>
            <div>
              <button type="submit" className="btn-primary">
                {editingId ? 'Зберегти зміни' : 'Додати'}
              </button>
              {editingId && (
                <button
                  type="button"
                  className="btn-edit"
                  style={{ marginLeft: '8px' }}
                  onClick={handleCancel}
                >
                  Скасувати
                </button>
              )}
            </div>
          </div>
        </form>
      </div>

      <div className="card">
        <h2>Список елементів</h2>
        <table>
          <thead>
            <tr>
              <th style={{ width: '60px' }}>ID</th>
              <th>Назва</th>
              <th>Опис</th>
              <th style={{ width: '120px' }}>Ціна</th>
              <th style={{ width: '180px', textAlign: 'right' }}>Дії</th>
            </tr>
          </thead>
          <tbody>
            {items.length === 0 ? (
              <tr>
                <td colSpan="5" className="empty-state">
                  {loading ? 'Завантаження даних...' : 'Список порожній. Створіть перший елемент вище.'}
                </td>
              </tr>
            ) : (
              items.map((item) => (
                <tr key={item.id}>
                  <td><span className="badge-id">#{item.id}</span></td>
                  <td><strong>{item.name}</strong></td>
                  <td style={{ color: 'var(--text-muted)' }}>
                    {item.description ? item.description : <em>(без опису)</em>}
                  </td>
                  <td><strong>{Number(item.price).toFixed(2)} ₴</strong></td>
                  <td style={{ textAlign: 'right' }}>
                    <button className="btn-edit" onClick={() => handleEdit(item)}>
                      Редагувати
                    </button>
                    <button className="btn-danger" onClick={() => handleDelete(item.id)}>
                      Видалити
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
