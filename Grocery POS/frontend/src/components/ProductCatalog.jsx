import React, { useState, useEffect } from 'react';
import { Search, Plus, Check, ShoppingBag } from 'lucide-react';
import { getProducts } from '../api/productsApi';
import { useCart } from '../context/CartContext';

const DEFAULT_CATEGORIES = [
  'All',
  'Fresh Fruits',
  'Fresh Vegetables',
  'Dairy & Eggs',
  'Bakery & Breads',
  'Rice & Flours',
  'Pulses & Dals',
  'Cooking Oils & Ghee',
  'Spices & Seasonings',
  'Beverages & Tea',
  'Snacks & Biscuits',
  'Cleaning & Household',
  'Personal Care'
];

const CATEGORY_EMOJIS = {
  'Fresh Fruits': '🍎',
  'Fresh Vegetables': '🥦',
  'Dairy & Eggs': '🥛',
  'Bakery & Breads': '🥖',
  'Rice & Flours': '🌾',
  'Pulses & Dals': '🫘',
  'Cooking Oils & Ghee': '🫒',
  'Spices & Seasonings': '🌶️',
  'Beverages & Tea': '☕',
  'Snacks & Biscuits': '🍪',
  'Cleaning & Household': '🧼',
  'Personal Care': '🧴',
  Produce: '🥦',
  Dairy: '🥛',
  Bakery: '🥖',
  Beverages: '☕',
  Pantry: '🫒',
  Grains: '🌾',
  Snacks: '🍫',
  General: '🛒',
};

export default function ProductCatalog() {
  const [products, setProducts] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [addedAnimationId, setAddedAnimationId] = useState(null);
  const { addToCart } = useCart();

  const [categoriesList, setCategoriesList] = useState(DEFAULT_CATEGORIES);

  useEffect(() => {
    // Optionally fetch dynamic categories from API
    fetch('http://localhost:8000/api/v1/categories/')
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data) && data.length > 0) {
          const names = ['All', ...data.map(c => c.name)];
          setCategoriesList(names);
        }
      })
      .catch(() => {
        // Keep default categories
      });
  }, []);

  useEffect(() => {
    loadCatalog();
  }, [selectedCategory, searchQuery]);

  const loadCatalog = async () => {
    setLoading(true);
    try {
      const data = await getProducts(searchQuery, selectedCategory);
      setProducts(data || []);
    } catch {
      setProducts([]);
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = (product) => {
    addToCart(product, 1);
    setAddedAnimationId(product.id);
    setTimeout(() => setAddedAnimationId(null), 500);
  };

  return (
    <div className="product-catalog-section">
      <div className="catalog-toolbar">
        <div className="search-box">
          <Search size={18} className="search-icon" />
          <input
            type="text"
            placeholder="Search items by name, barcode, or category..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          {searchQuery && (
            <button className="clear-search" onClick={() => setSearchQuery('')}>✕</button>
          )}
        </div>

        <div className="category-scroll">
          {categoriesList.map((cat) => (
            <button
              key={cat}
              className={`cat-pill ${selectedCategory === cat ? 'active' : ''}`}
              onClick={() => setSelectedCategory(cat)}
            >
              <span>{CATEGORY_EMOJIS[cat] || '📦'}</span>
              <span>{cat}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="catalog-grid-wrapper">
        {loading ? (
          <div className="loading-state">
            <div className="spinner"></div>
            <span>Loading grocery catalog...</span>
          </div>
        ) : products.length === 0 ? (
          <div className="empty-state">
            <ShoppingBag size={48} />
            <p>No products match your query.</p>
          </div>
        ) : (
          <div className="products-grid">
            {products.map((item) => (
              <div
                key={item.id}
                className={`product-card ${addedAnimationId === item.id ? 'just-added' : ''}`}
                onClick={() => handleAdd(item)}
              >
                <div className="card-top">
                  <span className="item-emoji">{CATEGORY_EMOJIS[item.category_name || item.category] || '📦'}</span>
                  <span className="item-category-tag">{item.category_name || item.category}</span>
                </div>

                <div className="card-body">
                  <h4 className="item-name" title={item.name}>{item.name}</h4>
                  <div className="item-meta">
                    <span className="item-barcode">Code: {item.barcode}</span>
                    <span className="item-unit">Per {item.unit || 'pcs'}</span>
                  </div>
                </div>

                <div className="card-footer">
                  <div className="price-tag">
                    <span className="currency">₹</span>
                    <span className="amount">{Number(item.price).toFixed(2)}</span>
                  </div>

                  <button
                    className="add-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleAdd(item);
                    }}
                    title="Add to Current Bill"
                  >
                    {addedAnimationId === item.id ? <Check size={16} /> : <Plus size={16} />}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
