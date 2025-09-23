# Stripe Connect

## Modellen
- Platform (VGM), Moskee als Connected Account (Express)
- Application Fee: 5%

## Flow (donatie)
1. Donateur initieert donatie → PaymentIntent
2. Stripe UI/SDK afhandeling
3. Webhook events (succeeded/failed/refund) → outbox → state update
4. Receipt e‑mail en notificatie

## Beveiliging
- Webhook signature validatie
- Idempotency keys
- Logging, monitoring & fraud‑signals
