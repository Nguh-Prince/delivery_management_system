# core/forms.py

from django import forms
from django.shortcuts import redirect
from django.contrib.auth import login
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm
from .models import Article,ProductType,Adresse, Delivery, Order, Cart, Refund, Notification, Client, Courier, Storekeeper
from django.contrib.auth import get_user_model

User = get_user_model()
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class AdminUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(choices=[
        ('client', 'Client'),
        ('courier', 'Courier'),
        ('storekeeper', 'Storekeeper'),
    ], required=True)
    phone_number = forms.CharField(max_length=15, required=False)
    address = forms.CharField(max_length=255, required=False)
    vehicle_details = forms.CharField(max_length=255, required=False)
    warehouse_location = forms.CharField(max_length=255, required=False)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'email']

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')

        if role == 'client' and not cleaned_data.get('phone_number'):
            self.add_error('phone_number', 'This field is required for clients.')
        if role == 'courier' and not cleaned_data.get('vehicle_details'):
            self.add_error('vehicle_details', 'This field is required for couriers.')
        if role == 'storekeeper' and not cleaned_data.get('warehouse_location'):
            self.add_error('warehouse_location', 'This field is required for storekeepers.')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        role = self.cleaned_data['role']

        if commit:
            user.save()
            if role == 'client':
                Client.objects.create(
                    user=user,
                    phone_number=self.cleaned_data['phone_number'],
                    address=self.cleaned_data['address']
                )
                group, created = Group.objects.get_or_create(name='Clients')
                user.groups.add(group)
                user.is_client = True
            elif role == 'courier':
                Courier.objects.create(
                    user=user,
                    phone_number=self.cleaned_data['phone_number'],
                    vehicle_details=self.cleaned_data['vehicle_details']
                )
                group, created = Group.objects.get_or_create(name='Couriers')
                user.groups.add(group)
                user.is_courier = True
            elif role == 'storekeeper':
                Storekeeper.objects.create(
                    user=user,
                    warehouse_location=self.cleaned_data['warehouse_location']
                )
                group, created = Group.objects.get_or_create(name='Storekeepers')
                user.groups.add(group)
                user.is_storekeeper = True
            user.save()
        return user
class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = ['status']

class ArticleForm(forms.ModelForm):
    sender_town = forms.ModelChoiceField(
        queryset=Adresse.objects.values_list('town', flat=True).distinct(),
        label='Sender Town'
    )
    sender_quarter = forms.ModelChoiceField(
        queryset=Adresse.objects.none(),
        label='Sender Quarter'
    )
    
    receiver_town = forms.ModelChoiceField(
        queryset=Adresse.objects.values_list('town', flat=True).distinct(),
        label='Receiver Town'
    )
    receiver_quarter = forms.ModelChoiceField(
        queryset=Adresse.objects.none(),
        label='Receiver Quarter'
    )

    class Meta:
        model = Article
        fields = [
            'sender_town', 
            'sender_quarter', 
            'receiver_town', 
            'receiver_quarter',
            'sender_phone', 
            'receiver_phone', 
            'weight'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Initialize empty querysets
        self.fields['sender_quarter'].queryset = Adresse.objects.none()
        self.fields['receiver_quarter'].queryset = Adresse.objects.none()
        
        if 'sender_town' in self.data:
            try:
                sender_town_name = self.data.get('sender_town')
                # Fetch all quarters for the selected sender town
                sender_quarters = Adresse.objects.filter(town=sender_town_name).order_by('quarter')
                # Create a list of unique quarters
                unique_sender_quarters = sorted(set(sender_quarters.values_list('quarter', flat=True)))
                self.fields['sender_quarter'].queryset = Adresse.objects.filter(quarter__in=unique_sender_quarters)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            # Handle instance case
            self.fields['sender_quarter'].queryset = Adresse.objects.filter(town=self.instance.sender_town).order_by('quarter').distinct('quarter')

        if 'receiver_town' in self.data:
            try:
                receiver_town_name = self.data.get('receiver_town')
                # Fetch all quarters for the selected receiver town
                receiver_quarters = Adresse.objects.filter(town=receiver_town_name).order_by('quarter')
                # Create a list of unique quarters
                unique_receiver_quarters = sorted(set(receiver_quarters.values_list('quarter', flat=True)))
                self.fields['receiver_quarter'].queryset = Adresse.objects.filter(quarter__in=unique_receiver_quarters)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            # Handle instance case
            self.fields['receiver_quarter'].queryset = Adresse.objects.filter(town=self.instance.receiver_town).order_by('quarter').distinct('quarter')


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['client', 'products', 'total_price', 'payment_status', 'delivery_status', 'qr_code', 'delivery_address']

class RefundForm(forms.ModelForm):
    class Meta:
        model = Refund
        fields = ['order', 'reason', 'approved']

class AddToCartForm(forms.ModelForm):
    class Meta:
        model = Cart
        fields = ['quantity']

class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['message', 'receiver']  # Exclude the sender field

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(NotificationForm, self).__init__(*args, **kwargs)

        # Limit the receiver choices to only Couriers
        self.fields['receiver'].queryset = Courier.objects.all()