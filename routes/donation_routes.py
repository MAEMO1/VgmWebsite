from flask import Blueprint, render_template, request, flash, redirect, url_for
from app import db
from models import Donation, FundraisingCampaign
from datetime import datetime

donations = Blueprint('donations', __name__)

@donations.route('/donate')
def donate_vgm():
    # Get active campaigns
    active_campaigns = FundraisingCampaign.query.filter_by(
        is_active=True
    ).order_by(FundraisingCampaign.start_date.desc()).all()
    
    return render_template('donate_vgm.html', campaigns=active_campaigns)

@donations.route('/donate', methods=['POST'])
def process_donation():
    amount = float(request.form.get('amount', 0))
    campaign_id = request.form.get('campaign_id')
    
    if amount <= 0:
        flash('Voer een geldig donatiebedrag in.', 'error')
        return redirect(url_for('donations.donate_vgm'))
    
    donation = Donation(
        amount=amount,
        donor_name=request.form.get('donor_name'),
        donor_email=request.form.get('donor_email'),
        is_anonymous=bool(request.form.get('is_anonymous')),
        is_monthly=bool(request.form.get('is_monthly')),
        payment_method=request.form.get('payment_method'),
        payment_status='pending',
        payment_initiated_at=datetime.utcnow()
    )
    
    if campaign_id:
        campaign = FundraisingCampaign.query.get(campaign_id)
        if campaign:
            donation.campaign = campaign
    
    db.session.add(donation)
    
    # Update campaign amount if donation is for a campaign
    if donation.campaign:
        donation.campaign.current_amount += amount
    
    db.session.commit()
    
    # Redirect based on payment method
    if donation.payment_method == 'bank_transfer':
        return redirect(url_for('donations.bank_transfer_instructions', donation_id=donation.id))
    elif donation.payment_method == 'paypal':
        return redirect(url_for('donations.process_paypal', donation_id=donation.id))
    else:
        return redirect(url_for('donations.process_stripe', donation_id=donation.id))
