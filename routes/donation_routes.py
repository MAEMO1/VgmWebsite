from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from models import Donation, FundraisingCampaign
from forms import FundraisingCampaignForm
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

@donations.route('/campagnes')
@login_required
def list_campaigns():
    if not current_user.is_admin:
        flash('Alleen administrators hebben toegang tot deze pagina.', 'error')
        return redirect(url_for('donations.donate_vgm'))

    campaigns = FundraisingCampaign.query.order_by(
        FundraisingCampaign.is_active.desc(),
        FundraisingCampaign.start_date.desc()
    ).all()

    return render_template('donations/campaigns.html', campaigns=campaigns)

@donations.route('/campagnes/toevoegen', methods=['GET', 'POST'])
@login_required
def add_campaign():
    if not current_user.is_admin:
        flash('Alleen administrators kunnen campagnes toevoegen.', 'error')
        return redirect(url_for('donations.donate_vgm'))

    form = FundraisingCampaignForm()

    if form.validate_on_submit():
        campaign = FundraisingCampaign(
            title=form.title.data,
            description=form.description.data,
            goal_amount=form.goal_amount.data,
            end_date=form.end_date.data,
            image_url=form.image_url.data,
            is_active=True
        )

        db.session.add(campaign)
        db.session.commit()

        flash('Campagne succesvol aangemaakt!', 'success')
        return redirect(url_for('donations.list_campaigns'))

    return render_template('donations/campaign_form.html', form=form)

@donations.route('/campagnes/<int:id>/bewerken', methods=['GET', 'POST'])
@login_required
def edit_campaign(id):
    if not current_user.is_admin:
        flash('Alleen administrators kunnen campagnes bewerken.', 'error')
        return redirect(url_for('donations.donate_vgm'))

    campaign = FundraisingCampaign.query.get_or_404(id)
    form = FundraisingCampaignForm(obj=campaign)

    if form.validate_on_submit():
        campaign.title = form.title.data
        campaign.description = form.description.data
        campaign.goal_amount = form.goal_amount.data
        campaign.end_date = form.end_date.data
        campaign.image_url = form.image_url.data

        db.session.commit()

        flash('Campagne succesvol bijgewerkt!', 'success')
        return redirect(url_for('donations.list_campaigns'))

    return render_template('donations/campaign_form.html', form=form, campaign=campaign)

@donations.route('/campagnes/<int:id>/toggle', methods=['POST'])
@login_required
def toggle_campaign(id):
    if not current_user.is_admin:
        flash('Alleen administrators kunnen campagnes beheren.', 'error')
        return redirect(url_for('donations.donate_vgm'))

    campaign = FundraisingCampaign.query.get_or_404(id)
    campaign.is_active = not campaign.is_active
    db.session.commit()

    status = 'geactiveerd' if campaign.is_active else 'gedeactiveerd'
    flash(f'Campagne succesvol {status}!', 'success')

    return redirect(url_for('donations.list_campaigns'))