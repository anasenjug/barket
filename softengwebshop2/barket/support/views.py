from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from core.models import Ticket
from django.contrib.auth.models import User
from django.contrib import messages
from core.models import Ticket, Message
from core.forms import TicketForm, MessageForm

# Create your views here.

@login_required
def create_ticket(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            messages.success(request, 'Ticket created successfully!')
            return redirect('support:ticket')
    else:
        form = TicketForm()

    return render(request, 'support/create_ticket.html', {'form': form})


@login_required
def ticket_list(request):
    tickets = Ticket.objects.filter(user=request.user)
    if request.user.is_staff:
        tickets = Ticket.objects.all()
    return render(request, 'support/ticket.html', {'tickets': tickets})

@login_required
def respond_to_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    messages_for_ticket = Message.objects.filter(ticket=ticket)
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.ticket = ticket
            message.user = request.user
            message.save()
            messages.success(request, 'Message sent successfully!')
            return redirect('support:respond_to_ticket', ticket_id=ticket_id)
    else:
        form = MessageForm()

    return render(request, 'support/respond_to_ticket.html', {'ticket': ticket, 'form': form, 'ticket_messages': messages_for_ticket})

@login_required
def resolve_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    ticket.is_resolved = True
    ticket.save()
    messages.success(request, 'Ticket resolved successfully!')
    return redirect('support:ticket')
