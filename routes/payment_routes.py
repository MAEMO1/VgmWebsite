import os
import stripe
import paypalrestsdk
from datetime import datetime
from flask import Blueprint, jsonify, request, current_app, url_for, render_template
from flask_mail import Message
from app import db, mail
from models import Donation, PaymentConfig

payments = Blueprint('payments', __name__)

# Initialize payment providers
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
paypalrestsdk.configure({
    "mode": "sandbox" if os.environ.get('PAYPAL_MODE') == 'sandbox' else "live",
    "client_id": os.environ.get('PAYPAL_CLIENT_ID'),
    "client_secret": os.environ.get('PAYPAL_CLIENT_SECRET')
})

def send_donation_confirmation_email(donation):
    """Send confirmation email for donations"""
    if not donation.donor_email:
        return
    
    msg = Message(
        'Bedankt voor uw donatie aan VGM',
        sender='noreply@vgm.be',
        recipients=[donation.donor_email]
    )
    
    if donation.payment_method == 'bank_transfer':
        msg.html = render_template(
            'emails/bank_transfer_instructions.html',
            donation=donation,
            iban=os.environ.get('VGM_IBAN'),
            bic=os.environ.get('VGM_BIC')
        )
    else:
        msg.html = render_template(
            'emails/donation_confirmation.html',
            donation=donation
        )
    
    mail.send(msg)

@payments.route('/process_donation', methods=['POST'])
def process_donation():
    data = request.get_json()
    
    # Create donation record
    donation = Donation(
        amount=data['amount'],
        donor_name=data.get('donor_name'),
        donor_email=data.get('donor_email'),
        message=data.get('message'),
        is_anonymous=data.get('is_anonymous', False),
        is_monthly=data.get('is_monthly', False),
        payment_method=data['payment_method'],
        payment_initiated_at=datetime.utcnow()
    )
    
    try:
        if donation.payment_method == 'bank_transfer':
            # For bank transfers, save donation and send instructions
            db.session.add(donation)
            db.session.commit()
            send_donation_confirmation_email(donation)
            return jsonify({
                'status': 'pending',
                'payment_reference': donation.payment_reference
            })
            
        elif donation.payment_method in ['apple_pay', 'bancontact', 'ideal']:
            # Create Stripe payment intent
            payment_intent = stripe.PaymentIntent.create(
                amount=int(donation.amount * 100),  # Convert to cents
                currency='eur',
                payment_method_types=[donation.payment_method.replace('_', '')],
                metadata={
                    'donation_id': donation.id,
                    'donor_name': donation.donor_name if not donation.is_anonymous else 'Anonymous'
                }
            )
            donation.stripe_payment_intent_id = payment_intent.id
            db.session.add(donation)
            db.session.commit()
            
            return jsonify({
                'status': 'pending',
                'client_secret': payment_intent.client_secret
            })
            
        elif donation.payment_method == 'paypal':
            # Create PayPal payment
            payment = paypalrestsdk.Payment({
                "intent": "sale",
                "payer": {"payment_method": "paypal"},
                "redirect_urls": {
                    "return_url": url_for('payments.execute_paypal_payment', _external=True),
                    "cancel_url": url_for('payments.cancel_payment', _external=True)
                },
                "transactions": [{
                    "amount": {
                        "total": str(donation.amount),
                        "currency": "EUR"
                    },
                    "description": "Donatie aan VGM"
                }]
            })
            
            if payment.create():
                donation.paypal_payment_id = payment.id
                db.session.add(donation)
                db.session.commit()
                
                # Extract approval URL
                approval_url = next(link.href for link in payment.links if link.rel == "approval_url")
                return jsonify({
                    'status': 'pending',
                    'approval_url': approval_url
                })
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'PayPal payment creation failed'
                }), 400
                
    except Exception as e:
        current_app.logger.error(f"Payment processing error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Payment processing failed'
        }), 400

@payments.route('/stripe_webhook', methods=['POST'])
def stripe_webhook():
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.environ.get('STRIPE_WEBHOOK_SECRET')
        )
        
        if event.type == 'payment_intent.succeeded':
            payment_intent = event.data.object
            donation = Donation.query.filter_by(
                stripe_payment_intent_id=payment_intent.id
            ).first()
            
            if donation:
                donation.payment_status = 'completed'
                donation.payment_completed_at = datetime.utcnow()
                db.session.commit()
                send_donation_confirmation_email(donation)
                
        return jsonify({'status': 'success'})
        
    except Exception as e:
        current_app.logger.error(f"Stripe webhook error: {str(e)}")
        return jsonify({'status': 'error'}), 400

@payments.route('/execute_paypal_payment')
def execute_paypal_payment():
    payment_id = request.args.get('paymentId')
    payer_id = request.args.get('PayerID')
    
    payment = paypalrestsdk.Payment.find(payment_id)
    donation = Donation.query.filter_by(paypal_payment_id=payment_id).first()
    
    if payment.execute({"payer_id": payer_id}):
        donation.payment_status = 'completed'
        donation.payment_completed_at = datetime.utcnow()
        db.session.commit()
        send_donation_confirmation_email(donation)
        return render_template('donation_success.html')
    else:
        return render_template('donation_failed.html')

@payments.route('/cancel_payment')
def cancel_payment():
    return render_template('donation_cancelled.html')
