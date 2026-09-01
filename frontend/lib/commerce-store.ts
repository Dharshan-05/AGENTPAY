/**
 * Authoritative Shared Commerce Session & State Store for AGENTPAY Frontend.
 * Synchronizes state across /ai-command-center, /command-center, /commerce, /transactions, and /payments routes.
 */

export interface CartItem {
  cart_item_id: string;
  session_id: string;
  product_id: string;
  product_name: string;
  price: number;
  currency: string;
  mrp?: number;
  discount_percentage?: number;
  seller_name: string;
  seller_reputation?: string;
  seller_risk_score?: number;
  quantity: number;
  specifications?: any;
  added_at: string;
}

export interface AgentPayOrder {
  agentpay_order_id: string;
  provider_order_id?: string;
  product_id: string;
  product_name: string;
  seller_name: string;
  amount: number;
  currency: string;
  razorpay_payment_id: string;
  razorpay_order_id: string;
  fulfillment_status: 'PENDING' | 'CONFIRMED' | 'PROCESSING' | 'SHIPPED' | 'DELIVERED' | 'CANCELLED' | 'FULFILLMENT_UNAVAILABLE';
  created_at: string;
}

export interface SharedCommerceState {
  commerce_session_id: string;
  current_intent: string;
  search_query: string;
  category: string;
  brand?: string;
  budget?: number;
  purpose?: string;
  products: any[];
  top_four_products: any[];
  recommended_product?: any;
  selected_product?: any;
  selected_product_id?: string;
  comparison_data?: any;
  comparison_list?: any[];
  cart_items?: CartItem[];
  orders?: AgentPayOrder[];
  seller_analysis?: any;
  price_analysis?: any;
  risk_analysis?: any;
  original_price?: number;
  current_price?: number;
  purchase_state: 'IDLE' | 'SELECTED' | 'REVALIDATING' | 'AGENTGUARD_PASSED' | 'PENDING_HUMAN_VERIFICATION' | 'PAYMENT_SUCCESSFUL' | 'BLOCKED';
  agentguard_result?: any;
  fraudguard_result?: any;
  human_verification_state?: 'NOT_REQUIRED' | 'PENDING' | 'VERIFIED' | 'REJECTED';
  razorpay_order_id?: string;
  razorpay_payment_id?: string;
  payment_status?: string;
  selected_model?: string;
  is_frozen?: boolean;
  frozen_reason?: string;
  uploaded_files?: Array<{
    name: string;
    size: number;
    type: string;
    uploaded_at: string;
    url?: string;
  }>;
  updated_at: string;
}

const STORAGE_KEY = 'agentpay_shared_commerce_session';

export function getSharedCommerceState(): SharedCommerceState {
  if (typeof window === 'undefined') {
    return createEmptyCommerceState();
  }
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      return JSON.parse(raw);
    }
  } catch (e) {
    console.error('Failed to read shared commerce session:', e);
  }
  const empty = createEmptyCommerceState();
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(empty));
  } catch (e) {
    // Ignore storage write error
  }
  return empty;
}

export function saveSharedCommerceState(state: Partial<SharedCommerceState>): SharedCommerceState {
  if (typeof window === 'undefined') {
    return createEmptyCommerceState();
  }
  let current: SharedCommerceState;
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    current = raw ? JSON.parse(raw) : createEmptyCommerceState();
  } catch (e) {
    current = createEmptyCommerceState();
  }
  const updated: SharedCommerceState = {
    ...current,
    ...state,
    updated_at: new Date().toISOString(),
  };
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new Event('agentpay_commerce_session_updated'));
    }
  } catch (e) {
    console.error('Failed to save shared commerce session:', e);
  }
  return updated;
}

export function freezeCommerceSession(reason: string = 'Operator safety lock initiated'): SharedCommerceState {
  return saveSharedCommerceState({
    is_frozen: true,
    frozen_reason: reason,
  });
}

export function unfreezeCommerceSession(): SharedCommerceState {
  return saveSharedCommerceState({
    is_frozen: false,
    frozen_reason: undefined,
  });
}

export function addUploadedFile(file: { name: string; size: number; type: string; url?: string }): SharedCommerceState {
  const current = getSharedCommerceState();
  const existingFiles = current.uploaded_files || [];
  const newFileEntry = {
    ...file,
    uploaded_at: new Date().toISOString(),
  };
  return saveSharedCommerceState({
    uploaded_files: [newFileEntry, ...existingFiles],
  });
}

export function addToCart(product: any): SharedCommerceState {
  const current = getSharedCommerceState();
  const cart = current.cart_items || [];
  const prodId = product.product_id || product.id || 'prod_' + Math.random().toString(36).slice(-6);
  
  const existingIdx = cart.findIndex((item) => item.product_id === prodId);
  let updatedCart: CartItem[];

  if (existingIdx >= 0) {
    updatedCart = [...cart];
    updatedCart[existingIdx] = {
      ...updatedCart[existingIdx],
      quantity: updatedCart[existingIdx].quantity + 1,
    };
  } else {
    const newItem: CartItem = {
      cart_item_id: 'cart_' + Math.random().toString(36).slice(-8),
      session_id: current.commerce_session_id,
      product_id: prodId,
      product_name: product.product_name || product.name || 'Selected Item',
      price: Number(product.price || 0),
      currency: product.currency || 'INR',
      mrp: product.mrp ? Number(product.mrp) : undefined,
      discount_percentage: product.discount_percentage ? Number(product.discount_percentage) : undefined,
      seller_name: product.seller?.seller_name || product.seller || 'Verified Merchant',
      seller_reputation: product.seller?.seller_reputation || 'VERIFIED',
      seller_risk_score: product.seller?.seller_risk_score || 5.0,
      quantity: 1,
      specifications: product.specifications || {},
      added_at: new Date().toISOString(),
    };
    updatedCart = [newItem, ...cart];
  }

  return saveSharedCommerceState({
    cart_items: updatedCart,
    selected_product: product,
    selected_product_id: prodId,
  });
}

export function removeFromCart(cartItemId: string): SharedCommerceState {
  const current = getSharedCommerceState();
  const cart = current.cart_items || [];
  const updatedCart = cart.filter((item) => item.cart_item_id !== cartItemId);
  return saveSharedCommerceState({ cart_items: updatedCart });
}

export function updateCartQuantity(cartItemId: string, delta: number): SharedCommerceState {
  const current = getSharedCommerceState();
  const cart = current.cart_items || [];
  const updatedCart = cart
    .map((item) => {
      if (item.cart_item_id === cartItemId) {
        const newQty = item.quantity + delta;
        return newQty > 0 ? { ...item, quantity: newQty } : null;
      }
      return item;
    })
    .filter(Boolean) as CartItem[];

  return saveSharedCommerceState({ cart_items: updatedCart });
}

export function clearCart(): SharedCommerceState {
  return saveSharedCommerceState({ cart_items: [] });
}

export function addOrder(order: AgentPayOrder): SharedCommerceState {
  const current = getSharedCommerceState();
  const existingOrders = current.orders || [];
  return saveSharedCommerceState({
    orders: [order, ...existingOrders],
  });
}

export function createEmptyCommerceState(): SharedCommerceState {
  return {
    commerce_session_id: 'session_' + Math.random().toString(36).substring(2, 10),
    current_intent: 'NONE',
    search_query: '',
    category: 'ALL',
    products: [],
    top_four_products: [],
    comparison_list: [],
    cart_items: [],
    orders: [],
    purchase_state: 'IDLE',
    human_verification_state: 'NOT_REQUIRED',
    selected_model: 'auto',
    is_frozen: false,
    uploaded_files: [],
    updated_at: new Date().toISOString(),
  };
}
