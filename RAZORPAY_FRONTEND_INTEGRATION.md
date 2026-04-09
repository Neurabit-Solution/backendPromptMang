# Razorpay Frontend Integration Guide

This guide explains how to integrate the credit purchase flow in your frontend application using the provided backend APIs.

## Payment Flow Overview

1.  **Fetch Pricing**: Call `/api/payments/pricing` to display the package size and price to the user.
2.  **Create Order**: When the user clicks "Buy", call `/api/payments/create-order` to get a Razorpay Order ID.
3.  **Checkout**: Use the Razorpay Web SDK to open the payment modal.
4.  **Verify Payment**: Send the payment details received from Razorpay to `/api/payments/verify-payment` to finalize the credit top-up.

---

### Step 1: Display Pricing Info

Fetch the package details from the backend to ensure the UI matches the configuration.

**API:** `GET /api/payments/pricing`

```javascript
async function loadPricing() {
  const response = await fetch('https://api.yourdomain.com/api/payments/pricing', {
    headers: { 'Authorization': `Bearer ${userToken}` }
  });
  const data = await response.json();
  
  // Update UI: "Buy ${data.credits} credits for ${data.currency} ${data.price_inr}"
}
```

---

### Step 2: Create a Razorpay Order

When the user initiates purchase, create a transaction record in the backend and get a Razorpay Order ID.

**API:** `POST /api/payments/create-order`

```javascript
async function startPurchase() {
  const response = await fetch('https://api.yourdomain.com/api/payments/create-order', {
    method: 'POST',
    headers: { 
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${userToken}` 
    },
    body: JSON.stringify({ credits: 0 }) // The backend uses the configured package size automatically
  });
  
  const orderData = await response.json();
  if (orderData.success) {
    openRazorpay(orderData);
  }
}
```

---

### Step 3: Open Razorpay Checkout

You must include the Razorpay script in your HTML:
`<script src="https://checkout.razorpay.com/v1/checkout.js"></script>`

```javascript
function openRazorpay(orderData) {
  const options = {
    key: orderData.key_id, // RAZORPAY_KEY_ID from backend
    amount: orderData.amount * 100, // Backend sends INR, Razorpay wants paise
    currency: orderData.currency,
    name: "MagicPic",
    description: `Purchase Credits`,
    order_id: orderData.order_id,
    handler: async function (response) {
      // This callback runs after successful payment capture in the popup
      await verifyPayment(response);
    },
    prefill: {
      name: user.name,
      email: user.email,
    },
    theme: {
      color: "#3399cc"
    }
  };

  const rzp1 = new window.Razorpay(options);
  
  rzp1.on('payment.failed', function (response) {
    alert("Payment Failed: " + response.error.description);
  });

  rzp1.open();
}
```

---

### Step 4: Verify Payment (Crucial)

Once Razorpay provides the `razorpay_payment_id` and `razorpay_signature`, you must send them to the backend to verify the authenticity of the transaction and update the user's credit balance.

**API:** `POST /api/payments/verify-payment`

```javascript
async function verifyPayment(paymentResponse) {
  const response = await fetch('https://api.yourdomain.com/api/payments/verify-payment', {
    method: 'POST',
    headers: { 
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${userToken}` 
    },
    body: JSON.stringify({
      razorpay_order_id: paymentResponse.razorpay_order_id,
      razorpay_payment_id: paymentResponse.razorpay_payment_id,
      razorpay_signature: paymentResponse.razorpay_signature
    })
  });

  const result = await response.json();
  if (result.success) {
    alert(`Success! Your new balance is ${result.total_credits} credits.`);
  } else {
    alert("Payment verification failed.");
  }
}
```

## Summary of Backend Responses

- **Pricing Info:** `{"credits": 50, "price_inr": 500, "currency": "INR"}`
- **Order Created:** `{"success": true, "order_id": "order_XXXXX", "amount": 500, "currency": "INR", "key_id": "rzp_test_..."}`
- **Payment Verified:** `{"success": true, "message": "...", "credits_added": 50, "total_credits": 150}`
