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

const PRODUCT_VISUALS = [
  { terms: ['apple', 'mango', 'banana', 'orange', 'grape', 'papaya', 'guava', 'fruit'], emoji: '\u{1F34E}', tone: 'fruit' },
  { terms: ['tomato', 'potato', 'onion', 'carrot', 'spinach', 'cabbage', 'cauliflower', 'vegetable'], emoji: '\u{1F966}', tone: 'vegetable' },
  { terms: ['milk', 'curd', 'yogurt', 'paneer', 'cheese', 'butter', 'ghee', 'cream', 'egg'], emoji: '\u{1F95B}', tone: 'dairy' },
  { terms: ['bread', 'bun', 'cake', 'biscuit', 'cookie', 'rusk', 'bakery'], emoji: '\u{1F956}', tone: 'bakery' },
  { terms: ['rice', 'atta', 'flour', 'maida', 'wheat', 'basmati', 'grain', 'poha'], emoji: '\u{1F33E}', tone: 'grain' },
  { terms: ['dal', 'pulse', 'chana', 'rajma', 'pea', 'bean', 'lentil'], emoji: '\u{1FAD8}', tone: 'pulses' },
  { terms: ['oil', 'mustard', 'sunflower', 'coconut', 'olive'], emoji: '\u{1FAD2}', tone: 'oil' },
  { terms: ['tea', 'coffee', 'juice', 'water', 'cola', 'drink', 'beverage'], emoji: '\u{2615}', tone: 'beverage' },
  { terms: ['salt', 'sugar', 'spice', 'masala', 'chilli', 'turmeric', 'pepper', 'cumin'], emoji: '\u{1FAD9}', tone: 'spice' },
  { terms: ['chocolate', 'chips', 'namkeen', 'snack', 'noodle', 'pasta', 'popcorn'], emoji: '\u{1F36B}', tone: 'snack' },
  { terms: ['soap', 'detergent', 'cleaner', 'phenyl', 'mosquito', 'household'], emoji: '\u{1F9FC}', tone: 'household' },
  { terms: ['shampoo', 'toothpaste', 'lotion', 'cosmetic', 'personal'], emoji: '\u{1F9F4}', tone: 'care' },
];

const CATEGORY_VISUALS = {
  'Fresh Fruits': { emoji: '\u{1F34E}', tone: 'fruit' },
  'Fresh Vegetables': { emoji: '\u{1F966}', tone: 'vegetable' },
  'Dairy & Eggs': { emoji: '\u{1F95B}', tone: 'dairy' },
  'Bakery & Breads': { emoji: '\u{1F956}', tone: 'bakery' },
  'Rice & Flours': { emoji: '\u{1F33E}', tone: 'grain' },
  'Pulses & Dals': { emoji: '\u{1FAD8}', tone: 'pulses' },
  'Cooking Oils & Ghee': { emoji: '\u{1FAD2}', tone: 'oil' },
  'Beverages & Tea': { emoji: '\u{2615}', tone: 'beverage' },
  'Spices & Seasonings': { emoji: '\u{1FAD9}', tone: 'spice' },
  'Snacks & Biscuits': { emoji: '\u{1F36B}', tone: 'snack' },
  'Cleaning & Household': { emoji: '\u{1F9FC}', tone: 'household' },
  'Personal Care': { emoji: '\u{1F9F4}', tone: 'care' },
};

function getProductVisual(product) {
  const name = String(product.name || '').toLowerCase();
  const match = PRODUCT_VISUALS.find((visual) => visual.terms.some((term) => name.includes(term)));
  return match || CATEGORY_VISUALS[product.category_name || product.category] || { emoji: '\u{1F4E6}', tone: 'general' };
}

const REAL_CATEGORY_IMAGES = {
  fruit: 'https://images.unsplash.com/photo-1610832958506-aa56368176cf?auto=format&fit=crop&w=480&q=80',
  vegetable: 'https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=480&q=80',
  dairy: 'https://images.unsplash.com/photo-1550583724-b2692b85b150?auto=format&fit=crop&w=480&q=80',
  bakery: 'https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=480&q=80',
  grain: 'https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=480&q=80',
  pulses: 'https://images.unsplash.com/photo-1515543904379-3d757abe72e4?auto=format&fit=crop&w=480&q=80',
  oil: 'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?auto=format&fit=crop&w=480&q=80',
  beverage: 'https://images.unsplash.com/photo-1544787219-7f47ccb76574?auto=format&fit=crop&w=480&q=80',
  spice: 'https://images.unsplash.com/photo-1596040033229-a9821ebd058d?auto=format&fit=crop&w=480&q=80',
  snack: 'https://images.unsplash.com/photo-1621939514649-280e2aa0abf?auto=format&fit=crop&w=480&q=80',
  household: 'https://images.unsplash.com/photo-1583947215259-38e31be8751f?auto=format&fit=crop&w=480&q=80',
  care: 'https://images.unsplash.com/photo-1556228578-8c89e6adf883?auto=format&fit=crop&w=480&q=80',
};

function getBarcodeImageUrl(barcode) {
  const code = String(barcode || '').replace(/\D/g, '');
  if (!code) return null;
  const groupedCode = code.length > 9 ? code.match(/.{1,3}/g).join('/') : code;
  return `https://images.openfoodfacts.org/images/products/${groupedCode}/front_en.400.jpg`;
}

function ProductImage({ product, visual }) {
  const exactImage = getBarcodeImageUrl(product.barcode);
  const fallbackImage = REAL_CATEGORY_IMAGES[visual.tone];
  const [imageUrl, setImageUrl] = useState(exactImage || fallbackImage);
  const [showFallbackVisual, setShowFallbackVisual] = useState(!exactImage && !fallbackImage);

  const handleImageError = () => {
    if (imageUrl !== fallbackImage && fallbackImage) {
      setImageUrl(fallbackImage);
    } else {
      setShowFallbackVisual(true);
    }
  };

  return (
    <div className={`item-image item-image-${visual.tone}`} role="img" aria-label={`${product.name} product image`}>
      {!showFallbackVisual && imageUrl ? (
        <img src={imageUrl} alt={product.name} loading="lazy" onError={handleImageError} />
      ) : (
        <span>{visual.emoji}</span>
      )}
    </div>
  );
}

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
                <ProductImage product={item} visual={getProductVisual(item)} />

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
