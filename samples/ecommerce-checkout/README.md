# E-commerce Checkout — Demo

A working e-commerce checkout flow built with vanilla HTML/CSS/JS. No framework,
no build step — just open `index.html` in any browser.

## Features

- Product cart with quantity adjustment
- Live subtotal + tax + total calculation
- Shipping + payment form with validation
- Order confirmation with generated order ID
- Stripe-style demo mode (use 4242 4242 4242 4242)

## Try it

Open `index.html` in any browser. Or visit the live demo:
[Apex Store checkout](./index.html)

## Why vanilla (no React)?

For a checkout flow this simple, vanilla JS is **3KB total** vs React's 45KB
bundle. Faster load, simpler maintenance, no dependencies to break.

For larger apps (dashboards, SaaS products) I'd use Next.js + TypeScript.

## Tech

- HTML5 semantic markup
- CSS Grid + Flexbox
- Vanilla ES6+ JavaScript
- No dependencies

## Production-ready upgrades

If this were a real store, I'd add:
- Stripe.js for actual payment processing
- Server-side cart validation
- Address autocomplete (Google Places API)
- Order confirmation email (Resend / Postmark)
- Inventory check before checkout
- Discount code field
- Multi-currency support
